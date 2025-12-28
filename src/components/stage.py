from src.utilities.context import Context
from src.utilities.scene import Scene


class Stage:
    def __init__(self, context: Context):
        self.scene: Scene | None = None
        self.context = context
