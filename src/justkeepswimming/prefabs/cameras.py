from justkeepswimming.components.sizing import SceneSizeConstraint
from justkeepswimming.components.physics import Transform
from justkeepswimming.components.render import Camera, MainCamera

from justkeepswimming.systems.render import RenderSystem
from justkeepswimming.systems.cameras import CameraSystem

from justkeepswimming.utilities.prefab import Prefab
from justkeepswimming.systems.sizing import SceneSizeConstraintSystem

main_camera_prefab = Prefab(
    components=[
        Camera(),
        Transform(),
        MainCamera(),
        SceneSizeConstraint(),
    ],
    systems=[RenderSystem, CameraSystem, SceneSizeConstraintSystem],
)
