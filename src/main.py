import asyncio

from game import Game

async def main() -> None:
    """The entry point of the game
    """
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())