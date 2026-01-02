import asyncio
from logging import getLogger
from typing import Awaitable, Set, Dict, Type


from src.datatypes.dag import DirectedAcyclicGraph, DirectedAcyclicGraphNode
from src.utilities.context import GameContext
from src.modules.clock import TickContext
from src.ecs import SceneContext, System


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
        self._logger = getLogger("Scheduler")
        self._systems: Set[System] = set()
        self._nodes: Dict[System, DirectedAcyclicGraphNode[System]] = {}
        self._graph: DirectedAcyclicGraph[System] = DirectedAcyclicGraph()
        self._execution_order: list[Set[System]] = []

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
        if system in self._systems:
            raise SystemDuplicateEntryException(
                f"System {system} is already in the scheduler."
            )
        self._systems.add(system)
        self._logger.info(f"Added system {system} to the scheduler.")
        self._rebuild()

    def remove_system(self, system: System) -> None:
        if system not in self._systems:
            raise SystemNotFoundException(
                f"System {system} not found in the scheduler."
            )
        self._systems.remove(system)
        self._rebuild()

    def execution_order(self) -> list[Set[System]]:
        return self._execution_order

    def _rebuild(self) -> None:
        self._graph = DirectedAcyclicGraph()
        self._nodes = {}

        for system in self._systems:
            node = DirectedAcyclicGraphNode(system)
            self._nodes[system] = node
            self._graph.insert_node(node)

        systems = list(self._systems)

        for i in range(len(systems)):
            for j in range(len(systems)):
                if i == j:
                    continue

                a = systems[i]
                b = systems[j]

                node_a = self._nodes[a]
                node_b = self._nodes[b]

                if a.writes & b.reads:
                    self._graph.set_dependency(node_b, node_a)

                if a.reads & b.writes:
                    self._graph.set_dependency(node_a, node_b)

                if a.writes & b.writes:
                    if type(a) in b.after:
                        self._graph.set_dependency(node_a, node_b)
                    elif type(b) in a.after:
                        self._graph.set_dependency(node_b, node_a)
                    elif type(a) in b.before:
                        self._graph.set_dependency(node_b, node_a)
                    elif type(b) in a.before:
                        self._graph.set_dependency(node_a, node_b)
                    else:
                        self._logger.warning(
                            f"There is a write-write conflict between systems {a} and {b} without explicit ordering, which may lead to non-deterministic behavior. The scheduler will assume {a} runs before {b}, but this assumption may not hold in all cases."
                        )
                    self._graph.set_dependency(node_b, node_a)

        for system in systems:
            node = self._nodes[system]

            for before_type in system.before:
                target = self._find_system(before_type)
                self._graph.set_dependency(node, self._nodes[target])

            for after_type in system.after:
                target = self._find_system(after_type)
                self._graph.set_dependency(self._nodes[target], node)

        self._execution_order = self._graph.parallel_sort()

    def _find_system(self, system_type: Type[System]) -> System:
        for system in self._systems:
            if isinstance(system, system_type):
                return system
        raise SystemNotFoundException(
            f"System of type {system_type.__name__} not found."
        )
