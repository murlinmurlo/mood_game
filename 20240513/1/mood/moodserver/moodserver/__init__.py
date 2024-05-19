__all__ = ["run_serve"]

from asyncio import run
from . import server


def run_serve():
    run(server.main())
