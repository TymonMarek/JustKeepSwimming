## This is a default scene module. You can expand upon it as needed.
## When loading a scene via `Scene.from_file` or `Stage.load_scene`, ensure that
## this module should define a variable called `export` that will be export an instance of `Scene`.
## Scenes may not reference other scenes directly to avoid circular dependencies.
## To request to load another scene, use emitters to signal to the stage to load a different scene.
from scene import Scene, SceneType

## The SceneType controls the inclusion of special objects in the scene
## such as the player and level-specific logic.

## Menu represents a menu scene without player or level logic.
scene = Scene("Default", SceneType.Unassigned)

## Level represents a playable level with player and entities.
# scene = Scene("Level 1", SceneType.Level)

## Unassigned represents a scene that does not do anything by default.
# scene = Scene("Loading screen", SceneType.Unassigned)

## To run actions when the scene is loaded or being unloaded, use the `loaded` and `unloading` emitters.
# scene.unloading.once(lambda: print("The scene is unloading..."))

## Scene configuration should be done here.
## WARNING: Scenes should never have any behavior that directly affects the state of the game
## for this, use Scene.context and emitters to signal to the stage or game to make changes.

## Example: To request a scene switch, emit on the `switch` emitter.
# scene.context.switch.emit("other_scene_name")

## Sprites can be created and added to the scene using `Scene.add(sprite)`.
## This can be done for all supported objects. Keep in mind objects
## that are not added to the scene will not be updated or rendered.
# sprite = Sprite.from_path(Path("assets/sprites/example.png"))
# scene.add(sprite)
## This can also be shortened, since `scene.add()` returns the added object.
# sprite = scene.add(Sprite.from_path(Path("assets/sprites/example.png")))

## The exported scene instance that will be loaded by the stage.
export = scene
