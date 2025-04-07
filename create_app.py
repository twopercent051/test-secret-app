import logging

import redis.asyncio as redis
import betterlogging
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import URL

from config import config


logger = logging.getLogger(__name__)
betterlogging.basic_colorized_config(level=logging.INFO)

r = redis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)

scheduler = AsyncIOScheduler(timezone="UTC")
scheduler.add_jobstore(
    jobstore="redis",
    jobs_key="train_jobs",
    run_times_key="train_times",
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.db,
)


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=config.postgres.user,
    password=config.postgres.password,
    host=config.postgres.host,
    port=config.postgres.port,
    database=config.postgres.db,
)

DATABASE_URL = DATABASE_URL.render_as_string(hide_password=False)


