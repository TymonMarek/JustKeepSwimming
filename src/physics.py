from clock import Tick
import entities

class Physics:
    """A handler for all entities that support physics.
    """
    async def update(self, tick: Tick):
        for entity in entities.all:
            entity.update(tick)