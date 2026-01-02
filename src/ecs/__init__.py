from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import overload

from src.modules.clock import TickContext
from src.utilities.context import GameContext


@dataclass(frozen=True)
class Entity:
    id: int


@dataclass
class Component:
    pass


class System:
    writes: frozenset[type[Component]] = frozenset()
    reads: frozenset[type[Component]] = frozenset()
    before: frozenset[type[System]] = frozenset()
    after: frozenset[type[System]] = frozenset()

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        raise NotImplementedError


@dataclass
class SceneContext:
    entities: dict[int, Entity] = field(default_factory=dict[int, Entity])
    components: dict[int, dict[type, Component]] = field(
        default_factory=dict[int, dict[type, Component]]
    )

    def create_entity(self) -> Entity:
        entity = Entity(len(self.entities) + 1)
        self.entities[entity.id] = entity
        self.components[entity.id] = {}
        return entity

    def delete_entity(self, entity: Entity) -> None:
        if entity.id in self.entities:
            del self.entities[entity.id]
            del self.components[entity.id]

    def add_component(self, entity: Entity, component: Component) -> None:
        if entity.id in self.components:
            self.components[entity.id][type(component)] = component

    @overload
    def query[C1](
        self, component_type: type[C1]
    ) -> Iterable[tuple[Entity, tuple[C1]]]: ...

    @overload
    def query[C1, C2](
        self, first_component_type: type[C1], second_component_type: type[C2]
    ) -> Iterable[tuple[Entity, tuple[C1, C2]]]: ...

    @overload
    def query[C1, C2, C3](
        self,
        first_component_type: type[C1],
        second_component_type: type[C2],
        third_component_type: type[C3],
    ) -> Iterable[tuple[Entity, tuple[C1, C2, C3]]]: ...

    @overload
    def query[C1, C2, C3, C4](
        self,
        first_component_type: type[C1],
        second_component_type: type[C2],
        third_component_type: type[C3],
        fourth_component_type: type[C4],
    ) -> Iterable[tuple[Entity, tuple[C1, C2, C3, C4]]]: ...

    def query(self, *classes: type[Component]) -> Iterable[tuple[Entity, tuple[Component, ...]]]: # type: ignore (See https://discuss.python.org/t/pre-pep-considerations-and-feedback-type-transformations-on-variadic-generics/50605)
        for entity_id, components in self.components.items():
            if all(component_type in components.keys() for component_type in classes):
                entity = self.entities[entity_id]
                components = tuple(components[component_type] for component_type in classes)
                yield (entity, components)
