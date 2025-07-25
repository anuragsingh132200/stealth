import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware as CORSMiddlewareBase
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from .db import create_tables, get_db
from .api.routes import router as job_router
from .schemas import JobStatus, JobResponse, JobResultResponse

# CORS middleware configuration
middleware = [
    Middleware(
        CORSMiddlewareBase,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    await create_tables()
    yield
    # Clean up resources if needed

app = FastAPI(
    title="Async Job Processing API",
    description="""
    ## Job Processing Service
    
    A high-performance, asynchronous job processing API built with FastAPI, Celery, and Redis.
    
    ### Features:
    - Submit jobs for processing (square_sum, cube_sum operations)
    - Check job status
    - Retrieve job results
    - Asynchronous processing with Celery
    - Containerized with Docker
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "jobs",
            "description": "Operations with jobs. You can submit, check status, and get results.",
        },
    ],
    middleware=middleware,
    lifespan=lifespan,
    docs_url=None,  # We'll customize the docs URLs
    redoc_url=None,
    openapi_url="/openapi.json"
)

# Custom docs endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="API health status",
    responses={
        200: {"description": "API is healthy"},
        500: {"description": "API is not healthy"}
    }
)
async def health_check():
    """
    Health check endpoint that verifies the API is running and can connect to required services.
    
    Returns:
        dict: A dictionary containing the health status of the API and its dependencies.
    """
    # Add additional health checks here (e.g., database, Redis)
    return {
        "status": "healthy",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "database": "connected",
            "redis": "connected",
            "celery": "connected"
        }
    }

# Include routers
app.include_router(
    job_router,
    prefix="/api/v1/jobs",
    tags=["jobs"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security definitions
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access"
                    }
                }
            }
        }
    }
    
    # Add more customizations as needed
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi