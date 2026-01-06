from justkeepswimming.components.physics import (
    AngularPhysicsComponent,
    LinearPhysicsComponent,
    TransformComponent,
)
from justkeepswimming.ecs import Component, Processor
from justkeepswimming.processors.physics import (
    AngularPhysicsProcessor,
    LinearPhysicsProcessor,
)
from justkeepswimming.utilities.prefab import Prefab


class GameObjectPrefab(Prefab):
    components: list[Component] = [
        TransformComponent(),
    ]
    processors: list[type[Processor]] = []


class PhysicsObjectPrefab(Prefab):
    extends = GameObjectPrefab()
    components = [
        LinearPhysicsComponent(),
        AngularPhysicsComponent(),
    ]
    processors = [
        LinearPhysicsProcessor,
        AngularPhysicsProcessor,
    ]
