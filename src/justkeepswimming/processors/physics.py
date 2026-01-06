from pygame import Vector2

from justkeepswimming.components.input import (
    PlayerAngularMovementInputComponent,
    PlayerLinearMovementInputComponent,
)
from justkeepswimming.components.physics import (
    AngularPhysicsComponent,
    LinearPhysicsComponent,
    TransformComponent,
)
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext


class AngularPhysicsProcessor(Processor):
    reads = frozenset({AngularPhysicsComponent, PlayerAngularMovementInputComponent})
    writes = frozenset({TransformComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        delta = tick_context.delta_time

        for entity, (angular_physics, transform) in scene_context.query(
            AngularPhysicsComponent,
            TransformComponent,
        ):
            torque_acceleration: float = 0.0

            if entity.has_component(PlayerAngularMovementInputComponent):
                input_component = entity.get_component(
                    PlayerAngularMovementInputComponent
                )

                torque_acceleration = input_component.torque * angular_physics.torque

            angular_physics.angular_velocity += torque_acceleration * delta
            angular_physics.angular_velocity -= (
                angular_physics.angular_velocity * angular_physics.angular_drag * delta
            )

            if (
                abs(angular_physics.angular_velocity)
                > angular_physics.max_angular_velocity
            ):
                angular_physics.angular_velocity = (
                    angular_physics.max_angular_velocity
                    * (1 if angular_physics.angular_velocity > 0 else -1)
                )

            transform.rotation += angular_physics.angular_velocity * delta


class LinearPhysicsProcessor(Processor):
    reads = frozenset({LinearPhysicsComponent, PlayerLinearMovementInputComponent})
    writes = frozenset({TransformComponent})
    alongside = frozenset({AngularPhysicsProcessor})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        delta = tick_context.delta_time

        for entity, (linear_physics, transform) in scene_context.query(
            LinearPhysicsComponent,
            TransformComponent,
        ):
            thrust_acceleration = Vector2(0, 0)

            if entity.has_component(PlayerLinearMovementInputComponent):
                input_component = entity.get_component(
                    PlayerLinearMovementInputComponent
                )

                wish_direction = (
                    transform.up * input_component.thrust.y
                    + transform.right * input_component.thrust.x
                )

                if wish_direction.length_squared() > 0:
                    wish_direction = wish_direction.normalize()

                thrust_acceleration = wish_direction * linear_physics.thrust

            linear_physics.velocity += thrust_acceleration * delta
            linear_physics.velocity -= (
                linear_physics.velocity * linear_physics.drag * delta
            )

            if linear_physics.velocity.length() > linear_physics.max_velocity:
                linear_physics.velocity.scale_to_length(linear_physics.max_velocity)

            transform.position += linear_physics.velocity * delta
