from typing import Optional
from clock import Tick
from player import Player
from scene import Scene
from window import Window

DEFAULT_SCENE = Scene.resolve("default")

class Stage:
    def __init__(self, player: Player, window: Window) -> None:
        self.scene: Optional[Scene] = None
        self.player = player
        self.window = window

    async def update(self, tick: Tick) -> None:
        if not self.scene:
            return
        await self.scene.update(tick, self.window, self.player)

    async def load_scene(self, name: str) -> None:
        scene = await self._preload_scene(name)
        await self.set_scene(scene)

    async def _preload_scene(self, name: str) -> Scene:
        return Scene.resolve(name)

    async def set_scene(self, new_scene: Scene) -> None:
        current_scene = self.scene
        if current_scene:
            await current_scene.unloading.emit()

        new_scene.context.switch.once(self.load_scene)

        self.scene = new_scene
        await self.scene.loaded.emit()