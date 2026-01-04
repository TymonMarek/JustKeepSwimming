from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar, Set, Dict, List

T = TypeVar("T")


class DirectedAcyclicGraphError(Exception):
    pass


class NodeNotFoundError(DirectedAcyclicGraphError):
    pass


class NodeAlreadyExistsError(DirectedAcyclicGraphError):
    pass


class CyclicalDependencyError(DirectedAcyclicGraphError):
    pass


class DirectedAcyclicGraphNode(Generic[T]):
    __slots__ = ("value", "depends_on")

    def __init__(self, value: T) -> None:
        self.value: T = value
        self.depends_on: Set[DirectedAcyclicGraphNode[T]] = set()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class DirectedAcyclicGraph(Generic[T]):
    def __init__(self) -> None:
        self.nodes: Set[DirectedAcyclicGraphNode[T]] = set()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nodes={len(self.nodes)})"

    def insert_node(
        self, node: DirectedAcyclicGraphNode[T]
    ) -> DirectedAcyclicGraphNode[T]:
        if node in self.nodes:
            raise NodeAlreadyExistsError(f"{node} already exists in the graph.")
        self.nodes.add(node)
        return node

    def _require_node(self, node: DirectedAcyclicGraphNode[T]) -> None:
        if node not in self.nodes:
            raise NodeNotFoundError(f"{node} is not part of this graph.")

    def _find_path(
        self,
        start: DirectedAcyclicGraphNode[T],
        target: DirectedAcyclicGraphNode[T],
    ) -> List[DirectedAcyclicGraphNode[T]] | None:
        stack: list[
            tuple[DirectedAcyclicGraphNode[T], list[DirectedAcyclicGraphNode[T]]]
        ] = [(start, [start])]
        visited: set[DirectedAcyclicGraphNode[T]] = set()

        while stack:
            current, path = stack.pop()

            if current is target:
                return path

            if current in visited:
                continue

            visited.add(current)

            for dep in current.depends_on:
                stack.append((dep, path + [dep]))

        return None

    def _format_cycle(self, nodes: list[DirectedAcyclicGraphNode[T]]) -> str:
        names = [repr(node.value) for node in nodes]

        arrow = " -> "
        here = "^"
        cycle_line = arrow.join(names)

        underline: List[str] = []
        for index, name in enumerate(names):
            if index == 0 or index == len(names) - 1:
                underline.extend(here * len(name))
            else:
                underline.extend(" " * len(name))
            if index != len(names) - 1:
                underline.extend(" " * len(arrow))
        underline_str = "".join(underline)

        return cycle_line + "\n" + underline_str

    def set_dependency(
        self,
        node: DirectedAcyclicGraphNode[T],
        dependency: DirectedAcyclicGraphNode[T],
    ) -> None:
        self._require_node(node)
        self._require_node(dependency)

        if node is dependency:
            raise CyclicalDependencyError(
                f"Cannot add dependency: {node} cannot depend on itself."
            )

        path = self._find_path(dependency, node)
        if path is not None:
            path_str = self._format_cycle(path + [dependency])
            raise CyclicalDependencyError(
                "Cannot add dependency because it would create a cycle:\n\n"
                f"{path_str}"
            )

        node.depends_on.add(dependency)

    def topological_sort(self) -> List[T]:
        in_degree: Dict[DirectedAcyclicGraphNode[T], int] = {
            node: 0 for node in self.nodes
        }

        for node in self.nodes:
            for _ in node.depends_on:
                in_degree[node] += 1

        queue: deque[DirectedAcyclicGraphNode[T]] = deque(
            node for node, degree in in_degree.items() if degree == 0
        )

        result: List[T] = []

        while queue:
            current = queue.popleft()
            result.append(current.value)

            for dependent in self.nodes:
                if current in dependent.depends_on:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        if len(result) != len(self.nodes):
            raise CyclicalDependencyError("Graph contains a cycle.")

        return result

    def parallel_sort(self) -> List[Set[T]]:
        in_degree: Dict[DirectedAcyclicGraphNode[T], int] = {
            node: 0 for node in self.nodes
        }

        for node in self.nodes:
            for _ in node.depends_on:
                in_degree[node] += 1

        zero_in_degree: Set[DirectedAcyclicGraphNode[T]] = {
            node for node, degree in in_degree.items() if degree == 0
        }

        layers: List[Set[T]] = []

        while zero_in_degree:
            current_layer: Set[T] = set()
            next_zero_in_degree: Set[DirectedAcyclicGraphNode[T]] = set()

            for node in zero_in_degree:
                current_layer.add(node.value)

                for dependent in self.nodes:
                    if node in dependent.depends_on:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_zero_in_degree.add(dependent)

            layers.append(current_layer)
            zero_in_degree = next_zero_in_degree

        total = sum(len(layer) for layer in layers)
        if total != len(self.nodes):
            raise CyclicalDependencyError("Graph contains a cycle.")

        return layers
