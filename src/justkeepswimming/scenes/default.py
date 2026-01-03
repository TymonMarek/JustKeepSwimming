from justkeepswimming.scenes import SceneID
from justkeepswimming.utilities.scene import Scene

from justkeepswimming.prefabs.cameras import MainCameraPrefab

def load() -> Scene:
    scene = Scene(SceneID.DEFAULT)
    MainCameraPrefab().construct(scene)
    return scene
