import pygame
from pygame import Vector2

from justkeepswimming.components.animation import (
    AnimationStateComponent,
    AnimatorComponent,
    SpritesheetComponent,
)
from justkeepswimming.components.render import RendererComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.processors.render import RendererPreProcessor, RendererProcessor
from justkeepswimming.processors.sizing import RendererTransformConstraintProcessor
from justkeepswimming.systems.clock import TickContext
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
                self.logger.debug(
                    f"Switching animation for entity: state={character_component.current_state}, "
                    f"from={getattr(character_component.current_track, 'animation', None)} to={desired_animation}"
                )
                if character_component.current_track is not None:
                    await character_component.current_track.stop()
                character_component.current_track = (
                    await animator_component.animator.load_animation(desired_animation)
                )
                await character_component.current_track.play()
