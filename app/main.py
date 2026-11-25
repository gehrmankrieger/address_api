""" Main. """


import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.db import init_db
from app.routers import addresses


settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncGenerator[None, None]:
    """ Reun once on startup before yield, and once after teardown after yield. """

    logger.info("Starting: %s v%s", settings.app_name, settings.app_version)
    init_db()
    logger.info("DB ready: %s", settings.database_url)
    yield
    logger.info("Teardown.")


def create_api() -> FastAPI:
    """ Build Fast API. """
    api = FastAPI(title=settings.app_name, version=settings.app_version, description="Sample Address API...", lifespan=lifespan)
    api.include_router(addresses.router)

    @api.exception_handler(SQLAlchemyError)
    async def handle_db_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """ Log error, return generic message to client. """

        logger.error("DB error on %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal DB error. "})

    @api.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """ Health check. """

        return {"status": "ok"}

    return api

api = create_api()