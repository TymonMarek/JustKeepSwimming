import logging
from src.components.clock import TickData
from src.utilities.ecs import Component, Entity


class System:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".System")

    def update(self, scene: "Scene", tick_data: TickData) -> None:
        self.logger.debug(f"System update called with tick_data={tick_data}")
        ...


class Scene:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Scene")
        self.entities: list[Entity] = []
        self.components: dict[int, dict[type, Component]] = {}
        self.systems: list[System] = []

    def create_entity(self) -> Entity:
        entity = Entity(id=len(self.entities))
        self.logger.info(f"Creating entity: {entity}")
        self.entities.append(entity)
        self.components[entity.id] = {}
        return entity

    def remove_entity(self, entity: Entity) -> None:
        if entity in self.entities:
            self.logger.info(f"Removing entity: {entity}")
            self.entities.remove(entity)
            if entity.id in self.components:
                del self.components[entity.id]

    def add_component(self, entity: Entity, component: Component) -> None:
        self.logger.info(f"Adding component {component} to entity {entity}")
        self.components[entity.id][type(component)] = component

    def remove_component(self, entity: Entity, component_type: type) -> None:
        self.logger.info(f"Removing component {component_type} from entity {entity}")
        if component_type in self.components[entity.id]:
            del self.components[entity.id][component_type]

    def add_system(self, system: System) -> None:
        self.logger.info(f"Adding system: {system}")
        self.systems.append(system)

    def get_matching_entities(
        self, *component_types: type
    ) -> dict[Entity, tuple[Component, ...]]:
        self.logger.debug(f"Getting entities matching components: {component_types}")
        result: dict[Entity, tuple[Component, ...]] = {}
        for entity in self.entities:
            entity_components = self.components.get(entity.id, {})
            if all(
                component_type in entity_components
                for component_type in component_types
            ):
                result[entity] = tuple(
                    entity_components[component_type]
                    for component_type in component_types
                )
        return result

    def update(self, tick_data: TickData) -> None:
        self.logger.debug(f"Updating scene with tick_data={tick_data}")
        for system in self.systems:
            system.update(self, tick_data)
