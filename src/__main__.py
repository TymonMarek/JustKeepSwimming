import asyncio
import logging
import argparse
from rich.logging import RichHandler

from src.game import Game

def setup_logging(verbosity: int):
    level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][min(3, max(0, verbosity))]
    logging.basicConfig(
        level=level,
        format='%(levelname)s %(name)s: %(message)s',
        handlers=[RichHandler(show_time=False)]
    )

async def main():
    game = Game()
    await game.initialize()
    await game.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Just Keep Swimming")
    parser.add_argument('-v', '--verbosity', type=int, default=2, help="Logging verbosity: 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG")
    args = parser.parse_args()
    setup_logging(args.verbosity)
    asyncio.run(main())
