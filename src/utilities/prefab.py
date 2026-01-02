from src.ecs.scheduler import SystemDuplicateEntryException
from src.ecs import Component, Entity, System
from src.utilities.scene import Scene


class Prefab:
    def __init__(self, components: list[Component], systems: list[System]) -> None:
        self.components = components
        self.systems = systems

    def construct(self, scene: Scene) -> Entity:
        entity = scene.context.create_entity()
        for component in self.components:
            scene.context.add_component(entity, component)
        for system in self.systems:
            try:
                scene.scheduler.add_system(system)
            except SystemDuplicateEntryException:
                pass
        return entity
