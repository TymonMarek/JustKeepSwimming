from justkeepswimming.ecs import Component, Entity, System
from justkeepswimming.utilities.scene import Scene


class Prefab:
    extends: Prefab | None = None
    components: list[Component]
    systems: list[type[System]]

    def construct(self, scene: Scene) -> Entity:
        entity: Entity
        
        if self.extends is not None:
            entity = self.extends.construct(scene)
        else:
            entity = scene.context.create_entity()
        
        for component in self.components:
            scene.context.add_component(entity, component)
        for system_class in self.systems:
            if any(
                isinstance(system, system_class) for system in scene.scheduler.systems
            ):
                continue
            scene.scheduler.add_system(system_class())
        return entity
