__all__ = []

from asyncio import run
from moodserver.server import main


def run_serve():
    run(main())
