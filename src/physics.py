from clock import Tick
import entities

class Physics:
    def __init__(self) -> None:
        ...

    async def update(self, tick: Tick):
        for entity in entities.all:
            entity.update(tick)