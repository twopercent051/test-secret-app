import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from app.middlewares import ClientIPMiddleware, CacheControlMiddleware
from create_app import logger, config, scheduler
from app.routers import router


async def on_startup():
    logger.info("Starting App")
    scheduler.start()


async def on_shutdown():
    logger.info("Bot stopped")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)

app.add_middleware(ClientIPMiddleware)
app.add_middleware(CacheControlMiddleware)


async def main():
    app_config = uvicorn.Config(app=app, host="0.0.0.0", port=config.app.inner_port, log_level="info")
    server = uvicorn.Server(config=app_config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped")
