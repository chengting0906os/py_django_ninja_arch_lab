"""ASGI entrypoint with lifecycle hooks for the Django + Ninja Extra stack."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.platform.settings')

import django  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402
import uvicorn  # noqa: E402

from src.platform.logging.loguru_io import Logger  # noqa: E402


django.setup()

django_asgi_app = get_asgi_application()
shutdown_event = asyncio.Event()
logger = Logger.base


@asynccontextmanager
async def app_lifespan() -> AsyncGenerator[None, None]:
    """Manage startup and shutdown routines for the application lifecycle."""
    try:
        logger.info('Application starting up...')
        yield
    except asyncio.CancelledError:
        logger.info('Application startup cancelled')
        raise
    finally:
        logger.info('Application shutting down...')
        shutdown_event.set()


async def lifespan(
    scope: Dict[str, Any],
    receive: Callable[[], Awaitable[Dict[str, Any]]],
    send: Callable[[Dict[str, Any]], Awaitable[None]],
) -> None:
    """ASGI lifespan handler that coordinates startup and shutdown events."""
    if scope['type'] != 'lifespan':
        raise ValueError(f'Unknown scope type: {scope["type"]}')

    async with app_lifespan():
        while True:
            message = await receive()
            message_type = message.get('type')

            if message_type == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message_type == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                break
            else:
                logger.warning(f'Unexpected lifespan message type: {message_type}')


async def application(
    scope: Dict[str, Any],
    receive: Callable[[], Awaitable[Dict[str, Any]]],
    send: Callable[[Dict[str, Any]], Awaitable[None]],
) -> None:
    """Dispatch lifespan events or delegate to Django's ASGI application."""
    if scope['type'] == 'lifespan':
        await lifespan(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)


def main() -> None:
    """Launch the ASGI server with uvicorn."""
    uvicorn.run(
        'src.platform.config.asgi:application',
        host='0.0.0.0',
        port=8000,
        reload=True,
        lifespan='on',
        loop='uvloop',
    )


if __name__ == '__main__':
    main()
