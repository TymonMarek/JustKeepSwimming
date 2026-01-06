from pygame import Vector2

from justkeepswimming.components.input import (
    PlayerAngularMovementInputComponent,
    PlayerLinearMovementInputComponent,
)
from justkeepswimming.components.pseudo import InputPseudoComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.systems.input import InputActionId
from justkeepswimming.utilities.context import EngineContext
from justkeepswimming.utilities.log import logger

LINEAR_INPUT_ACTION_TO_WISH_VECTOR: dict[InputActionId, Vector2] = {
    InputActionId.PLAYER_MOVE_UP: Vector2(0, 1),
    InputActionId.PLAYER_MOVE_DOWN: Vector2(0, -1),
    InputActionId.PLAYER_MOVE_LEFT: Vector2(-1, 0),
    InputActionId.PLAYER_MOVE_RIGHT: Vector2(1, 0),
}


class PlayerLinearMovementInputProcessor(Processor):
    reads = frozenset({InputPseudoComponent})
    writes = frozenset({PlayerLinearMovementInputComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        input_actions = engine_context.input.action_manager.actions
        direction = Vector2(0, 0)
        for action_id, vector in LINEAR_INPUT_ACTION_TO_WISH_VECTOR.items():
            action = input_actions.get(action_id)
            if not action:
                logger.warning(f"Input action {action_id} not found")
                raise ValueError(f"Input action {action_id} not found")
            if action.active:
                direction += vector

        if direction.length_squared() > 0:
            direction = direction.normalize()

        for _, (wish,) in scene_context.query(PlayerLinearMovementInputComponent):
            wish.thrust = direction


ANGULAR_INPUT_ACTION_TO_WISH_TORQUE: dict[InputActionId, float] = {
    InputActionId.PLAYER_TURN_LEFT: -1.0,
    InputActionId.PLAYER_TURN_RIGHT: 1.0,
}


class PlayerAngularMovementInputProcessor(Processor):
    reads = frozenset({InputPseudoComponent})
    writes = frozenset({PlayerAngularMovementInputComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        input_actions = engine_context.input.action_manager.actions
        torque = 0.0
        for action_id, wish_torque in ANGULAR_INPUT_ACTION_TO_WISH_TORQUE.items():
            action = input_actions.get(action_id)
            if not action:
                logger.warning(f"Input action {action_id} not found")
                raise ValueError(f"Input action {action_id} not found")
            if action.active:
                torque += wish_torque

        for _, (wish,) in scene_context.query(PlayerAngularMovementInputComponent):
            wish.torque = torque
