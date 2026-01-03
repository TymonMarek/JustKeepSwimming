import asyncio
from logging import getLogger
from typing import Awaitable, Set, Dict, Type

from justkeepswimming.datatypes.dag import DirectedAcyclicGraph, DirectedAcyclicGraphNode
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
            awaitables: list[Awaitable[None]] = []
            for system in system_group:
                awaitables.append(
                    system.update(tick_context, scene_context, engine_context)
                )
            await asyncio.gather(*awaitables)

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

                write_read = a.writes & b.reads
                if write_read:
                    self.logger.debug(
                        f"Ordering decision: {a} runs BEFORE {b} "
                        f"because {b} reads {self._fmt_components(write_read)} "
                        f"that {a} writes"
                    )
                    self._graph.set_dependency(node_b, node_a)

                read_write = a.reads & b.writes
                if read_write:
                    self.logger.debug(
                        f"Ordering decision: {b} runs BEFORE {a} "
                        f"because {a} reads {self._fmt_components(read_write)} "
                        f"that {b} writes"
                    )
                    self._graph.set_dependency(node_a, node_b)

                write_write = a.writes & b.writes
                if write_write:
                    self.logger.debug(
                        f"Write-write conflict detected between {a} and {b} "
                        f"on {self._fmt_components(write_write)}"
                    )

                    if type(a) in b.after:
                        self.logger.debug(
                            f"Resolved by explicit ordering: {b} declares after {type(a).__name__} "
                            f"→ {a} runs BEFORE {b}"
                        )
                        self._graph.set_dependency(node_a, node_b)

                    elif type(b) in a.after:
                        self.logger.debug(
                            f"Resolved by explicit ordering: {a} declares after {type(b).__name__} "
                            f"→ {b} runs BEFORE {a}"
                        )
                        self._graph.set_dependency(node_b, node_a)

                    elif type(a) in b.before:
                        self.logger.debug(
                            f"Resolved by explicit ordering: {b} declares before {type(a).__name__} "
                            f"→ {b} runs BEFORE {a}"
                        )
                        self._graph.set_dependency(node_b, node_a)

                    elif type(b) in a.before:
                        self.logger.debug(
                            f"Resolved by explicit ordering: {a} declares before {type(b).__name__} "
                            f"→ {a} runs BEFORE {b}"
                        )
                        self._graph.set_dependency(node_a, node_b)

                    else:
                        self.logger.warning(
                            f"Unresolved write-write conflict between {a} and {b} "
                            f"on {self._fmt_components(write_write)}. "
                            f"Assuming {a} runs BEFORE {b}. This may be non-deterministic."
                        )

                    self.logger.debug(
                        f"Final decision: {a} runs BEFORE {b} due to write-write conflict"
                    )
                    self._graph.set_dependency(node_b, node_a)

        for system in systems:
            node = self._nodes[system]

            for before_type in system.before:
                target = self._find_system(before_type)
                self.logger.debug(
                    f"Explicit ordering: {system} runs BEFORE {target} "
                    f"due to 'before={before_type.__name__}'"
                )
                self._graph.set_dependency(node, self._nodes[target])

            for after_type in system.after:
                target = self._find_system(after_type)
                self.logger.debug(
                    f"Explicit ordering: {system} runs AFTER {target} "
                    f"due to 'after={after_type.__name__}'"
                )
                self._graph.set_dependency(self._nodes[target], node)

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
