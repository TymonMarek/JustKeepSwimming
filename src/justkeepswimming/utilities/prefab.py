import logging

from justkeepswimming.ecs import Component, Entity, Processor
from justkeepswimming.utilities.scene import Scene


class Prefab:
    extends: "Prefab | list[Prefab] | None" = None
    components: list[Component]
    processors: list[type[Processor]]
    logger = logging.getLogger(__name__)

    def construct(self, scene: "Scene", use_entity: Entity | None = None) -> Entity:
        entity: Entity
        if use_entity is not None:
            entity = use_entity
        else:
            entity = scene.context.create_entity()

        if self.extends:
            if isinstance(self.extends, list):
                for prefab in self.extends:
                    prefab.construct(scene, use_entity=entity)
            else:
                self.extends.construct(scene, use_entity=entity)

        for component in self.components:
            component_type = type(component)
            if entity.has_component(component_type):
                entity.remove_component(entity.get_component(component_type))
            entity.add_component(component.__class__(**vars(component)))

        for processor_cls in self.processors:
            if not any(
                isinstance(p, processor_cls) for p in scene.scheduler.processors
            ):
                scene.scheduler.add_processor(processor_cls())

        return entity
