from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.components.render import CameraComponent, MainCameraComponent
from justkeepswimming.components.sizing import SceneSizeConstraintComponent
from justkeepswimming.ecs import Component, Processor
from justkeepswimming.processors.camera import CameraProcessor
from justkeepswimming.processors.render import RendererProcessor
from justkeepswimming.processors.sizing import SceneSizeConstraintProcessor
from justkeepswimming.utilities.prefab import Prefab


class CameraPrefab(Prefab):
    components: list[Component] = [
        CameraComponent(),
        TransformComponent(),
    ]
    processors: list[type[Processor]] = [
        RendererProcessor,
        CameraProcessor,
    ]


class MainCameraPrefab(Prefab):
    extends = CameraPrefab()
    components: list[Component] = [
        MainCameraComponent(),
        SceneSizeConstraintComponent(),
    ]
    processors: list[type[Processor]] = [
        SceneSizeConstraintProcessor,
    ]
