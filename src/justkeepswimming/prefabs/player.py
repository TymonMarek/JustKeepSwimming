from justkeepswimming.characters.turtle import TurtlePrefab
from justkeepswimming.components.input import (
    PlayerAngularMovementInputComponent,
    PlayerLinearMovementInputComponent,
)
from justkeepswimming.components.physics import (
    AngularPhysicsComponent,
    LinearPhysicsComponent,
)
from justkeepswimming.prefabs.physics import PhysicsObjectPrefab
from justkeepswimming.processors.input import (
    PlayerAngularMovementInputProcessor,
    PlayerLinearMovementInputProcessor,
)
from justkeepswimming.utilities.prefab import Prefab


class PlayerPrefab(Prefab):
    extends = [PhysicsObjectPrefab(), TurtlePrefab()]
    components = [
        LinearPhysicsComponent(
            thrust=200.0,
            max_velocity=200.0,
        ),
        AngularPhysicsComponent(
            torque=150.0,
            max_angular_velocity=120.0,
        ),
        PlayerLinearMovementInputComponent(),
        PlayerAngularMovementInputComponent(),
    ]
    processors = [
        PlayerLinearMovementInputProcessor,
        PlayerAngularMovementInputProcessor,
    ]
