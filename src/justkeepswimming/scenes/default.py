from justkeepswimming.scenes import SceneID
from justkeepswimming.utilities.scene import Scene

from justkeepswimming.prefabs.cameras import main_camera_prefab

def load() -> Scene:
    scene = Scene(SceneID.DEFAULT)
    _ = main_camera_prefab.construct(scene)
    return scene
