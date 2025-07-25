import pytest
from fastapi import status
from sqlalchemy import select
from app.db import Job, JobStatus

# Test data
TEST_DATA = [1, 2, 3, 4, 5]
SQUARE_SUM = sum(x**2 for x in TEST_DATA)
CUBE_SUM = sum(x**3 for x in TEST_DATA)

# Test job submission
@pytest.mark.asyncio
async def test_submit_job(client):
    # Test square sum operation
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "square_sum"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["status"] == JobStatus.PENDING
    assert data["operation"] == "square_sum"
    
    # Test cube sum operation
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "cube_sum"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["operation"] == "cube_sum"

# Test job status
@pytest.mark.asyncio
async def test_get_job_status(client):
    # Create a job
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "square_sum"}
    )
    job_id = response.json()["id"]
    
    # Check status
    response = await client.get(f"/jobs/{job_id}/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == job_id
    assert data["status"] in [JobStatus.PENDING, JobStatus.IN_PROGRESS, JobStatus.SUCCESS]

# Test job result
@pytest.mark.asyncio
async def test_get_job_result(client):
    # Create a job
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "square_sum"}
    )
    job_id = response.json()["id"]
    
    # Wait for job to complete (since we're using eager mode in tests)
    import time
    max_attempts = 5
    for _ in range(max_attempts):
        response = await client.get(f"/jobs/{job_id}/result")
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            break
        time.sleep(0.5)
    
    # Check result
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == job_id
    assert data["status"] == JobStatus.SUCCESS
    assert "result" in data
    assert "value" in data["result"]
    assert data["result"]["value"] == SQUARE_SUM

# Test invalid job ID
@pytest.mark.asyncio
async def test_invalid_job_id(client):
    # Test non-existent job status
    response = await client.get("/jobs/999/status")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Test non-existent job result
    response = await client.get("/jobs/999/result")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test invalid operation
@pytest.mark.asyncio
async def test_invalid_operation(client):
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "invalid_operation"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test cube sum operation
@pytest.mark.asyncio
async def test_cube_sum_operation(client):
    # Create a cube sum job
    response = await client.post(
        "/jobs/",
        json={"data": TEST_DATA, "operation": "cube_sum"}
    )
    job_id = response.json()["id"]
    
    # Wait for job to complete
    import time
    max_attempts = 5
    for _ in range(max_attempts):
        response = await client.get(f"/jobs/{job_id}/result")
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            break
        time.sleep(0.5)
    
    # Check result
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == JobStatus.SUCCESS
    assert data["result"]["value"] == CUBE_SUM