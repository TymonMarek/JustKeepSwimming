import asyncio
from logging import getLogger
from typing import Set, Dict, Type

from justkeepswimming.datatypes.dag import (
    DirectedAcyclicGraph,
    DirectedAcyclicGraphNode,
)
from justkeepswimming.utilities.context import GameContext
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.ecs import Component, SceneContext, System


class SchedulerException(Exception):
    pass


class SystemNotFoundException(SchedulerException):
    pass


class SystemDuplicateEntryException(SchedulerException):
    pass


class SystemConflictException(SchedulerException):
    pass


class SystemScheduler:
    def __init__(self) -> None:
        self.logger = getLogger("Scheduler")
        self.systems: Set[System] = set()
        self._nodes: Dict[System, DirectedAcyclicGraphNode[System]] = {}
        self._graph: DirectedAcyclicGraph[System] = DirectedAcyclicGraph()
        self._execution_order: list[Set[System]] = []

    def _fmt_components(self, components: frozenset[Type[Component]]) -> str:
        return "{" + ", ".join(comp.__name__ for comp in components) + "}"

    async def process_tick(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        for system_group in self._execution_order:
            await asyncio.gather(
                *(
                    system.update(tick_context, scene_context, engine_context)
                    for system in system_group
                )
            )

    def add_system(self, system: System) -> None:
        if system in self.systems:
            raise SystemDuplicateEntryException(
                f"System {system} is already in the scheduler."
            )
        self.systems.add(system)
        self.logger.debug(f"Added system {system} to the scheduler.")
        self._rebuild()

    def remove_system(self, system: System) -> None:
        if system not in self.systems:
            raise SystemNotFoundException(
                f"System {system} not found in the scheduler."
            )
        self.systems.remove(system)
        self._rebuild()

    def execution_order(self) -> list[Set[System]]:
        return self._execution_order

    def _explicit_order(self, a: System, b: System) -> int | None:
        if type(b) in a.before or type(a) in b.after:
            return -1
        if type(b) in a.after or type(a) in b.before:
            return 1
        return None

    def _rebuild(self) -> None:
        self.logger.debug("Rebuilding system scheduler DAG")

        self._graph = DirectedAcyclicGraph()
        self._nodes = {}

        for system in self.systems:
            node = DirectedAcyclicGraphNode(system)
            self._nodes[system] = node
            self._graph.insert_node(node)
            self.logger.debug(
                f"Inserted node for system {system} "
                f"(reads={self._fmt_components(system.reads)}, "
                f"writes={self._fmt_components(system.writes)})"
            )

        systems = list(self.systems)

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

    def _find_system(self, system_type: Type[System]) -> System:
        for system in self.systems:
            if isinstance(system, system_type):
                return system
        raise SystemNotFoundException(
            f"System of type {system_type.__name__} not found."
        )
