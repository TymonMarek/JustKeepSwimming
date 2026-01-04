import asyncio
from logging import getLogger
from typing import Dict, Set, Type

from justkeepswimming.datatypes.dag import (
    DirectedAcyclicGraph,
    DirectedAcyclicGraphNode,
)
from justkeepswimming.ecs import Component, Processor, SceneContext
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext


class SchedulerException(Exception):
    pass


class SystemNotFoundException(SchedulerException):
    pass


class SystemDuplicateEntryException(SchedulerException):
    pass


class SystemConflictException(SchedulerException):
    pass


class ProcessorScheduler:
    def __init__(self) -> None:
        self.logger = getLogger("Scheduler")
        self.processors: Set[Processor] = set()
        self._nodes: Dict[Processor, DirectedAcyclicGraphNode[Processor]] = {}
        self._graph: DirectedAcyclicGraph[Processor] = DirectedAcyclicGraph()
        self._execution_order: list[Set[Processor]] = []

    def _fmt_components(self, components: frozenset[Type[Component]]) -> str:
        return "{" + ", ".join(comp.__name__ for comp in components) + "}"

    async def process_tick(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for system_group in self._execution_order:
            await asyncio.gather(
                *(
                    system.update(tick_context, scene_context, engine_context)
                    for system in system_group
                )
            )

    def add_system(self, system: Processor) -> None:
        if system in self.processors:
            raise SystemDuplicateEntryException(
                f"System {system} is already in the scheduler."
            )
        self.processors.add(system)
        self.logger.debug(f"Added system {system} to the scheduler.")
        self._rebuild()

    def remove_system(self, system: Processor) -> None:
        if system not in self.processors:
            raise SystemNotFoundException(
                f"System {system} not found in the scheduler."
            )
        self.processors.remove(system)
        self._rebuild()

    def execution_order(self) -> list[Set[Processor]]:
        return self._execution_order

    def _explicit_order(self, a: Processor, b: Processor) -> int | None:
        if type(b) in a.before or type(a) in b.after:
            return -1
        if type(b) in a.after or type(a) in b.before:
            return 1
        return None

    def _rebuild(self) -> None:
        self.logger.debug("Rebuilding system scheduler DAG")

        self._graph = DirectedAcyclicGraph()
        self._nodes = {}

        for system in self.processors:
            node = DirectedAcyclicGraphNode(system)
            self._nodes[system] = node
            self._graph.insert_node(node)
            self.logger.debug(
                f"Inserted node for system {system} "
                f"(reads={self._fmt_components(system.reads)}, "
                f"writes={self._fmt_components(system.writes)})"
            )

        systems = list(self.processors)

        for i in range(len(systems)):
            for j in range(len(systems)):
                if i == j:
                    continue

                a = systems[i]
                b = systems[j]

                node_a = self._nodes[a]
                node_b = self._nodes[b]

                order = self._explicit_order(a, b)
                if order is not None:
                    if order < 0:
                        self.logger.debug(f"Explicit override: {a} runs BEFORE {b}")
                        self._graph.set_dependency(node_b, node_a)
                    else:
                        self.logger.debug(f"Explicit override: {a} runs AFTER {b}")
                        self._graph.set_dependency(node_a, node_b)
                    continue

                write_read = a.writes & b.reads
                if write_read:
                    self.logger.debug(
                        f"Inferred: {a} runs BEFORE {b} "
                        f"because {b} reads {self._fmt_components(write_read)}"
                    )
                    self._graph.set_dependency(node_b, node_a)

                read_write = a.reads & b.writes
                if read_write:
                    self.logger.debug(
                        f"Inferred: {b} runs BEFORE {a} "
                        f"because {a} reads {self._fmt_components(read_write)}"
                    )
                    self._graph.set_dependency(node_a, node_b)

                write_write = a.writes & b.writes
                if write_write:
                    raise SystemConflictException(
                        f"Unresolved write-write conflict between {a} and {b} "
                        f"on {self._fmt_components(write_write)}"
                    )

        self._execution_order = self._graph.parallel_sort()

        self.logger.debug(
            "Final execution layers: "
            + " | ".join(
                "{" + ", ".join(type(s).__name__ for s in layer) + "}"
                for layer in self._execution_order
            )
        )

    def _find_system(self, system_type: Type[Processor]) -> Processor:
        for system in self.processors:
            if isinstance(system, system_type):
                return system
        raise SystemNotFoundException(
            f"System of type {system_type.__name__} not found."
        )
