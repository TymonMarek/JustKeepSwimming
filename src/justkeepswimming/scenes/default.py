from justkeepswimming.prefabs.sprites import SpritePrefab
from justkeepswimming.scenes import SceneID
from justkeepswimming.utilities.scene import Scene

from justkeepswimming.prefabs.cameras import MainCameraPrefab


def load() -> Scene:
    scene = Scene(SceneID.DEFAULT)
    MainCameraPrefab().construct(scene)
    SpritePrefab().construct(scene)
    return scene
