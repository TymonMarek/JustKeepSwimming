from pathlib import Path

from pygame import Color, Vector2

from justkeepswimming.components.animation import (
    AnimationStateComponent,
    SpritesheetComponent,
)
from justkeepswimming.components.filter import TintComponent
from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.prefabs.characters import CharacterPrefab
from justkeepswimming.processors.filter import TintProcessor
from justkeepswimming.utilities.animation import (
    Animation,
    AnimationPriority,
    AnimationType,
    Keyframe,
    KeyframeSequence,
)
from justkeepswimming.utilities.image import Frame, Image
from justkeepswimming.utilities.prefab import Prefab
from justkeepswimming.utilities.transform import Grid

TURTLE_GRID = Grid(
    rows=5,
    columns=6,
    cell_size=Vector2(48, 48),
)


class TurtlePrefab(Prefab):
    extends = CharacterPrefab()
    components = [
        SpritesheetComponent(
            {
                AnimationType.IDLE: Animation(
                    image=Image(Path("assets/spritesheets/turtle.png")),
                    priority=AnimationPriority.LOW,
                    looped=True,
                    speed=1.0,
                    sequence=KeyframeSequence(
                        [
                            Keyframe(
                                0.25,
                                Frame(TURTLE_GRID.cell(0, 0)),
                            ),
                            Keyframe(
                                0.50,
                                Frame(TURTLE_GRID.cell(0, 1)),
                            ),
                            Keyframe(
                                0.5,
                                Frame(TURTLE_GRID.cell(0, 2)),
                            ),
                            Keyframe(
                                1.00,
                                Frame(TURTLE_GRID.cell(0, 3)),
                            ),
                        ]
                    ),
                ),
                AnimationType.WALK: Animation(
                    image=Image(Path("assets/spritesheets/turtle.png")),
                    priority=AnimationPriority.MEDIUM,
                    looped=True,
                    speed=1.0,
                    sequence=KeyframeSequence(
                        [
                            Keyframe(
                                0,
                                Frame(TURTLE_GRID.cell(1, 0)),
                            ),
                            Keyframe(
                                0.2,
                                Frame(TURTLE_GRID.cell(1, 1)),
                            ),
                            Keyframe(
                                0.3,
                                Frame(TURTLE_GRID.cell(1, 2)),
                            ),
                            Keyframe(
                                0.4,
                                Frame(TURTLE_GRID.cell(1, 3)),
                            ),
                            Keyframe(
                                0.6,
                                Frame(TURTLE_GRID.cell(1, 4)),
                            ),
                            Keyframe(
                                1.0,
                                Frame(TURTLE_GRID.cell(1, 5)),
                            ),
                        ]
                    ),
                ),
                AnimationType.ATTACK: Animation(
                    image=Image(Path("assets/spritesheets/turtle.png")),
                    priority=AnimationPriority.HIGH,
                    looped=False,
                    speed=1.0,
                    sequence=KeyframeSequence(
                        [
                            Keyframe(
                                0,
                                Frame(TURTLE_GRID.cell(2, 0)),
                            ),
                            Keyframe(
                                0.2,
                                Frame(TURTLE_GRID.cell(2, 1)),
                            ),
                            Keyframe(
                                0.4,
                                Frame(TURTLE_GRID.cell(2, 2)),
                            ),
                            Keyframe(
                                0.6,
                                Frame(TURTLE_GRID.cell(2, 3)),
                            ),
                            Keyframe(
                                0.8,
                                Frame(TURTLE_GRID.cell(2, 4)),
                            ),
                            Keyframe(
                                1.0,
                                Frame(TURTLE_GRID.cell(2, 5)),
                            ),
                        ]
                    ),
                ),
                AnimationType.HURT: Animation(
                    image=Image(Path("assets/spritesheets/turtle.png")),
                    priority=AnimationPriority.HIGH,
                    looped=True,
                    speed=1.0,
                    sequence=KeyframeSequence(
                        [
                            Keyframe(
                                0,
                                Frame(TURTLE_GRID.cell(3, 0)),
                            ),
                            Keyframe(
                                1,
                                Frame(TURTLE_GRID.cell(3, 1)),
                            ),
                        ]
                    ),
                ),
                AnimationType.DEATH: Animation(
                    image=Image(Path("assets/spritesheets/turtle.png")),
                    priority=AnimationPriority.RESERVED,
                    looped=False,
                    speed=1.0,
                    sequence=KeyframeSequence(
                        [
                            Keyframe(
                                0,
                                Frame(TURTLE_GRID.cell(4, 0)),
                            ),
                            Keyframe(
                                0.2,
                                Frame(TURTLE_GRID.cell(4, 1)),
                            ),
                            Keyframe(
                                0.4,
                                Frame(TURTLE_GRID.cell(4, 2)),
                            ),
                            Keyframe(
                                0.6,
                                Frame(TURTLE_GRID.cell(4, 3)),
                            ),
                            Keyframe(
                                0.8,
                                Frame(TURTLE_GRID.cell(4, 4)),
                            ),
                            Keyframe(
                                1.0,
                                Frame(TURTLE_GRID.cell(4, 5)),
                            ),
                        ]
                    ),
                ),
            }
        ),
        TransformComponent(
            position=Vector2(300, 300),
            size=Vector2(48 * 3, 48 * 3),
            anchor=Vector2(0.5, 0.5),
        ),
        AnimationStateComponent(
            current_state=AnimationType.WALK,
        ),
        TintComponent(
            color=Color(0, 255, 0),
            intensity=0.7,
        ),
    ]
    processors = [TintProcessor]
