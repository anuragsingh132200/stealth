from fastapi import APIRouter, HTTPException, Depends, status, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..db import Job, JobStatus, get_db, create_tables
from ..schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse, OperationType
from .. import tasks

router = APIRouter()

@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new job",
    description="""
    Submit a new job for processing. The job will be processed asynchronously.
    
    Supported operations:
    - `square_sum`: Calculate the sum of squares of the input numbers
    - `cube_sum`: Calculate the sum of cubes of the input numbers
    """,
    responses={
        201: {"description": "Job successfully submitted"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    },
    response_description="The created job with PENDING status"
)
async def create_job(
    job: JobCreate = Body(
        ...,
        example={
            "data": [1, 2, 3, 4, 5],
            "operation": "square_sum"
        },
        description="Job creation payload"
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Create a new job in the database
        db_job = Job(
            status=JobStatus.PENDING,
            operation=job.operation,
            input_data={"data": job.data}
        )
        
        db.add(db_job)
        await db.commit()
        await db.refresh(db_job)
        
        # Start the background task
        tasks.process_job.delay(
            job_id=db_job.id,
            operation=job.operation,
            data=job.data
        )
        
        return db_job
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )

@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="""
    Retrieve the current status of a job by its ID.
    
    Possible statuses:
    - `PENDING`: Job is queued for processing
    - `IN_PROGRESS`: Job is currently being processed
    - `SUCCESS`: Job completed successfully
    - `FAILED`: Job failed during processing
    """,
    responses={
        200: {"description": "Job status retrieved successfully"},
        404: {"description": "Job not found"},
        500: {"description": "Internal server error"}
    },
    response_description="The current status of the job"
)
async def get_job_status(
    job_id: int = Path(
        ...,
        description="The ID of the job to check",
        example=1,
        gt=0
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Job).filter(Job.id == job_id))
        job = result.scalars().first()
        
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found"
            )
        
        return job
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job status: {str(e)}"
        )

@router.get(
    "/{job_id}/result",
    response_model=JobResultResponse,
    summary="Get job result",
    description="""
    Retrieve the result of a completed job by its ID.
    
    Note: This endpoint will only return results for jobs that have completed
    (status SUCCESS or FAILED). For jobs that are still processing, check the
    status endpoint first.
    """,
    responses={
        200: {"description": "Job result retrieved successfully"},
        400: {"description": "Job is still processing"},
        404: {"description": "Job not found"},
        500: {"description": "Internal server error"}
    },
    response_description="The result of the completed job"
)
async def get_job_result(
    job_id: int = Path(
        ...,
        description="The ID of the job to retrieve results for",
        example=1,
        gt=0
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Job).filter(Job.id == job_id))
        job = result.scalars().first()
        
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found"
            )
        
        if job.status not in [JobStatus.SUCCESS, JobStatus.FAILED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job with ID {job_id} is still {job.status}. Please check back later.",
                headers={"Retry-After": "5"}
            )
        
        response_data = {
            "id": job.id,
            "status": job.status,
            "operation": job.operation,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
        
        if job.result:
            if "error" in job.result and job.result["error"]:
                response_data["error"] = job.result["error"]
            if "result" in job.result:
                response_data["result"] = job.result["result"]
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job result: {str(e)}"
        )