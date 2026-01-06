import pygame
from pygame import Vector2

from justkeepswimming.components.animation import (
    AnimationStateComponent,
    AnimatorComponent,
    SpritesheetComponent,
)
from justkeepswimming.components.physics import (
    LinearPhysicsComponent,
    TransformComponent,
)
from justkeepswimming.components.render import RendererComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.processors.render import RendererPreProcessor, RendererProcessor
from justkeepswimming.processors.sizing import RendererTransformConstraintProcessor
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.animation import AnimationType
from justkeepswimming.utilities.context import EngineContext


class AnimationTrackPlaybackProcessor(Processor):
    reads = frozenset({AnimatorComponent, RendererComponent})
    writes = frozenset({AnimatorComponent, RendererComponent})
    before = frozenset({RendererProcessor})
    after = frozenset({RendererTransformConstraintProcessor, RendererPreProcessor})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (animation_component, renderer_component) in scene_context.query(
            AnimatorComponent,
            RendererComponent,
        ):
            await animation_component.animator.update(tick_context)
            current_frame = await animation_component.animator.get_current_frame()
            if current_frame is not None:
                renderer_component.surface.blit(
                    pygame.transform.scale(
                        current_frame, renderer_component.surface.get_size()
                    ),
                    Vector2(0, 0),
                )


class CharacterAnimationStateProcessors(Processor):
    reads = frozenset(
        {AnimationStateComponent, TransformComponent, LinearPhysicsComponent}
    )
    writes = frozenset({AnimationStateComponent})

    ACCEL_EPS = 0.1
    DOT_HYST = 0.2

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (anim_state, transform, physics) in scene_context.query(
            AnimationStateComponent,
            TransformComponent,
            LinearPhysicsComponent,
        ):
            accel = physics.acceleration.length()

            if accel <= self.ACCEL_EPS:
                if anim_state.current_state != AnimationType.IDLE:
                    anim_state.current_state = AnimationType.IDLE
                continue

            vel = physics.velocity
            if vel.length_squared() < 1e-6:
                desired = AnimationType.WALK
            else:
                move_dir = vel.normalize()
                facing_dir = Vector2(1, 0).rotate(transform.rotation)
                dot = move_dir.dot(facing_dir)

                if anim_state.current_state == AnimationType.REVERSE_WALK:
                    desired = (
                        AnimationType.REVERSE_WALK
                        if dot < +self.DOT_HYST
                        else AnimationType.WALK
                    )
                else:
                    desired = (
                        AnimationType.WALK
                        if dot > -self.DOT_HYST
                        else AnimationType.REVERSE_WALK
                    )

            if anim_state.current_state != desired:
                anim_state.current_state = desired


class CharacterAnimationProcessor(Processor):
    reads = frozenset(
        {AnimatorComponent, AnimationStateComponent, SpritesheetComponent}
    )
    writes = frozenset({AnimatorComponent})
    before = frozenset({RendererProcessor, AnimationTrackPlaybackProcessor})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (
            animator_component,
            character_component,
            spritesheet_component,
        ) in scene_context.query(
            AnimatorComponent,
            AnimationStateComponent,
            SpritesheetComponent,
        ):
            desired_animation = spritesheet_component.animations[
                character_component.current_state
            ]
            if (
                character_component.current_track is None
                or character_component.current_track.animation != desired_animation
            ):
                if (
                    character_component.current_track is not None
                    and character_component.current_track.priority.value
                    >= desired_animation.priority.value
                ):
                    await character_component.current_track.stop()
                character_component.current_track = (
                    await animator_component.animator.load_animation(
                        character_component.current_state, desired_animation
                    )
                )
                await character_component.current_track.play()
