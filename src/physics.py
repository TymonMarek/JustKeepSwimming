from entities import Entity
from clock import Tick
from typing import List

class Physics:
    """A handler for all entities that support physics.
    """
    def __init__(self) -> None:
        self.enabled = True
   
    async def update(self, tick: Tick, entities: List[Entity]):
        if not self.enabled:
            return
        for entity in entities:
            entity.update(tick)