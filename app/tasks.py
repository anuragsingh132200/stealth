from celery import Celery
import asyncio
from .db import JobStatus, async_session_maker, Job
from sqlalchemy import update
from sqlalchemy.future import select
import os

# Import Celery configuration
from .celery_config import *

# Initialize Celery
celery_app = Celery("job_processor")

# Apply configuration from celery_config
celery_app.config_from_object('app.celery_config')

async def update_job_status(job_id: int, status: JobStatus, result: dict = None, error: str = None):
    async with async_session_maker() as session:
        stmt = (
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=status,
                result={"result": result, "error": error} if result or error else None
            )
        )
        await session.execute(stmt)
        await session.commit()

@celery_app.task(bind=True)
def process_job(self, job_id: int, operation: str, data: list):
    # This is a synchronous function that will be called by Celery
    # We'll run the async function in an event loop
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_job_async(job_id, operation, data))

async def process_job_async(job_id: int, operation: str, data: list):
    try:
        # Update job status to IN_PROGRESS
        await update_job_status(job_id, JobStatus.IN_PROGRESS)
        
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # Process the job based on operation
        if operation == "square_sum":
            result = sum(x**2 for x in data)
        elif operation == "cube_sum":
            result = sum(x**3 for x in data)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Update job status to SUCCESS with result
        await update_job_status(job_id, JobStatus.SUCCESS, {"value": result})
        return {"status": "success", "result": result}
        
    except Exception as e:
        # Update job status to FAILED with error
        error_msg = str(e)
        await update_job_status(job_id, JobStatus.FAILED, error=error_msg)
        return {"status": "error", "error": error_msg}