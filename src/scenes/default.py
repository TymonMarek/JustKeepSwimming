from src.scenes import SceneID
from src.utilities.scene import Scene

from src.prefabs.cameras import main_camera_prefab

def load() -> Scene:
    scene = Scene(SceneID.DEFAULT)
    _ = main_camera_prefab.construct(scene)
    return scene
