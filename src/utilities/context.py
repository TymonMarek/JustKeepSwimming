from dataclasses import dataclass

from src.components.window import Window

@dataclass
class Context:
    window: Window