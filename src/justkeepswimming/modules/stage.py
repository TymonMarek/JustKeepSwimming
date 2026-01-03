import enum
import copy
from dataclasses import dataclass, field
from logging import getLogger
from typing import Callable, Optional

from justkeepswimming.modules.clock import TickContext
from justkeepswimming.utilities.context import GameContext
from justkeepswimming.utilities.scene import Scene, SceneID
from justkeepswimming.utilities.signal import Signal


class SceneLoadingStrategy(enum.Enum):
    LAZY = enum.auto()
    EAGER = enum.auto()


type SceneFactory = Callable[[], Scene]


class SceneHandle:
    def __init__(
        self,
        scene_id: SceneID,
        factory: SceneFactory,
        strategy: SceneLoadingStrategy,
    ) -> None:
        self.scene_id = scene_id
        self.factory = factory
        self.strategy = strategy
        self._scene: Optional[Scene] = None

    async def get_scene(self) -> Scene:
        if self._scene is None:
            self._scene = self.factory()
            await self._scene.on_load.emit()

        return copy.deepcopy(self._scene)


@dataclass
class StageContext:
    scene: Optional[Scene] = None
    on_request_switch_scene: Signal[SceneID] = field(
        default_factory=lambda: Signal[SceneID]()
    )


class Stage:
    def __init__(
        self,
        engine_context: GameContext,
        scenes: dict[SceneID, SceneFactory],
        loading_strategy: SceneLoadingStrategy = SceneLoadingStrategy.EAGER,
    ) -> None:
        self.logger = getLogger("Stage")

        self.scenes = scenes
        self.loading_strategy = loading_strategy

        self.scene: Optional[Scene] = None
        self.handles: dict[SceneID, SceneHandle] = {}

        self.on_tick = Signal[TickContext, GameContext]()
        self.engine_context = engine_context
        self.context = StageContext()

        self.on_tick.connect(self._process_scene)
        self.context.on_request_switch_scene.connect(self._handle_request_switch_scene)

        if loading_strategy is SceneLoadingStrategy.EAGER:
            self._create_all_handles()

    def _create_all_handles(self) -> None:
        for scene_id, factory in self.scenes.items():
            self.handles[scene_id] = SceneHandle(
                scene_id,
                factory,
                self.loading_strategy,
            )

    def _get_handle(self, scene_id: SceneID) -> SceneHandle:
        try:
            return self.handles[scene_id]
        except KeyError:
            try:
                factory = self.scenes[scene_id]
            except KeyError:
                raise ValueError(f"Scene {scene_id} does not exist")

            handle = SceneHandle(scene_id, factory, self.loading_strategy)
            self.handles[scene_id] = handle
            return handle

    async def switch_scene(self, scene_id: SceneID) -> None:
        await self.context.on_request_switch_scene.emit(scene_id)

    async def _handle_request_switch_scene(self, scene_id: SceneID) -> None:
        if self.scene:
            await self.scene.on_exit.emit()
            await self.scene.on_unload.emit()

        handle = self._get_handle(scene_id)
        self.scene = await handle.get_scene()
        await self.scene.on_enter.emit(self.engine_context)

    async def _process_scene(
        self,
        tick_context: TickContext,
        game_context: GameContext,
    ) -> None:
        if self.scene:
            await self.scene.on_tick.emit(tick_context, game_context)
