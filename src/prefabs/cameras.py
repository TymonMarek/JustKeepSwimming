from src.components.sizing import SceneSizeConstraint
from src.components.physics import Transform
from src.components.render import Camera, MainCamera

from src.systems.render import RenderSystem
from src.systems.cameras import CameraSystem

from src.utilities.prefab import Prefab
from src.systems.sizing import SceneSizeConstraintSystem

main_camera_prefab = Prefab(
    components=[
        Camera(),
        Transform(),
        MainCamera(),
        SceneSizeConstraint(),
    ],
    systems=[RenderSystem, CameraSystem, SceneSizeConstraintSystem],
)
