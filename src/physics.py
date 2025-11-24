from clock import Tick
import entities

class Physics:
    """A handler for all entities that support physics.
    """
    def __init__(self) -> None:
        self.enabled = True
   
    async def update(self, tick: Tick):
        if not self.enabled:
            return
        for entity in entities.all:
            entity.update(tick)