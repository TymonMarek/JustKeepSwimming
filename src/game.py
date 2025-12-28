import pygame
pygame.init()

from src.components.dispatcher import Dispatcher
from src.components.window import Window
from src.components.clock import Clock

class Game:
    def __init__(self):
        self.dispatcher = Dispatcher() 
        self.window = Window()
        self.clock = Clock()
        self.running = False
        
    async def tick(self) -> None:
        await self.dispatcher.process_events()
        await self.clock.tick()

    async def run(self) -> None:
        self.running = True
        while self.running:
            await self.tick()
        pygame.quit()
            
    def stop(self) -> None:
        self.running = False
