from datetime import datetime

from create_app import scheduler

from db.dao import SecretsDAO


async def __scheduler_dispatcher(secret_id: int):
    await SecretsDAO.delete_secret_by_secret_id(secret_id=secret_id)


async def create_task(run_date: datetime, secret_id: int):
    scheduler.add_job(
        func=__scheduler_dispatcher,
        trigger="date",
        run_date=run_date,
        kwargs={"secret_id": secret_id},
        misfire_grace_time=None,
    )
