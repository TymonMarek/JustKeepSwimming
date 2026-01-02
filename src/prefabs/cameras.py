from src.components.physics import Transform
from src.components.render import Camera, MainCamera

from src.systems.render import RenderSystem
from src.systems.cameras import CameraSystem

from src.utilities.prefab import Prefab

main_camera_prefab = Prefab(
    components=[
        Camera(),
        Transform(),
        MainCamera(),
    ],
    systems=[
        RenderSystem,
        CameraSystem,
    ],
)
