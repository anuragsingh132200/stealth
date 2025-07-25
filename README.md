# Async Job Processing API

A high-performance, containerized backend service for processing mathematical operations asynchronously using FastAPI, Celery, Redis, and PostgreSQL.

## 🚀 Project Overview

This application provides a RESTful API for submitting and monitoring background jobs that perform mathematical operations. It's built with a modern async Python stack and follows best practices for scalability and reliability.

### How It Works

1. **Job Submission**: Users submit jobs with a list of numbers and an operation type (square_sum or cube_sum).
2. **Asynchronous Processing**: Jobs are processed asynchronously using Celery with Redis as the message broker.
3. **Status Tracking**: Job status is tracked in real-time (PENDING → IN_PROGRESS → SUCCESS/FAILED).
4. **Result Retrieval**: Users can check job status and retrieve results once processing is complete.

### Processing Simulation

In the current implementation, there's a simulated processing delay of 2 seconds (using `asyncio.sleep(2)`). This simulates CPU-intensive work and demonstrates the asynchronous nature of the application. In a production environment, this would be replaced with actual computation or integration with other services.

## ✨ Features

- **RESTful API** with OpenAPI documentation
- **Asynchronous Processing** using Celery and Redis
- **Real-time Status Updates** with multiple job states
- **Containerized** with Docker for easy deployment
- **PostgreSQL** for persistent job storage
- **Flower** for monitoring Celery tasks
- **Health Check** endpoint
- **Comprehensive Error Handling**
- **Type Annotations** throughout the codebase

## 🛠 Tech Stack

- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM
- **Celery** - Distributed task queue
- **Redis** - Message broker and result backend
- **PostgreSQL** - Primary database
- **Docker** - Containerization
- **Pydantic** - Data validation

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Git (for version control)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file if needed
   ```

3. **Initialize Git** (if not already initialized)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

### Running with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Start all services
docker compose up -d --build
```

### Access Services

- **API Documentation**: http://localhost:8000/docs
- **Flower Dashboard**: http://localhost:5555
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### 1. Submit a Job
```
POST /api/v1/jobs/
```

**Request:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "operation": "square_sum"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "status": "PENDING",
  "operation": "square_sum",
  "created_at": "2023-07-25T18:30:00.000Z",
  "updated_at": "2023-07-25T18:30:00.000Z"
}
```

### 2. Check Job Status
```
GET /api/v1/jobs/{job_id}/status
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "IN_PROGRESS",
  "operation": "square_sum",
  "created_at": "2023-07-25T18:30:00.000Z",
  "updated_at": "2023-07-25T18:30:02.123Z"
}
```

### 3. Get Job Result
```
GET /api/v1/jobs/{job_id}/result
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "SUCCESS",
  "operation": "square_sum",
  "created_at": "2023-07-25T18:30:00.000Z",
  "updated_at": "2023-07-25T18:30:02.123Z",
  "result": {
    "result": 55,
    "error": null
  }
}
```

## 🔧 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── db.py            # Database models and session
│   ├── schemas.py       # Pydantic models
│   ├── tasks.py         # Celery tasks
│   ├── celery_config.py # Celery configuration
│   └── api/
│       ├── __init__.py
│       └── routes.py    # API endpoints
├── tests/               # Test files
│   ├── __init__.py
│   ├── conftest.py     # Test fixtures
│   └── test_jobs.py    # Test cases
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore file
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker configuration
├── init.sql            # Database initialization
└── requirements.txt    # Python dependencies
```

## 🧪 Running Tests

```bash
# Run tests
docker compose exec web pytest -v

# Run with coverage
docker compose exec web pytest --cov=app --cov-report=term-missing
```

## 🌐 Monitoring

### Flower Dashboard
Monitor Celery tasks at: http://localhost:5555
- **Username**: `admin`
- **Password**: `admin`
- **Features**:
  - Real-time task monitoring
  - Worker status and statistics
  - Task history and results
  - Task retry and revoke functionality

### Health Check
Check service health at: http://localhost:8000/health

### Accessing Logs

```bash
# View web server logs
docker compose logs web

# View worker logs
docker compose logs worker

# View Flower logs
docker compose logs flower

# View database logs
docker compose logs db

# View Redis logs
docker compose logs redis
```

## 🔄 Job Lifecycle

1. **PENDING**: Job is created and waiting in the queue
2. **IN_PROGRESS**: Worker has picked up the job (after ~2s delay)
3. **SUCCESS/FAILED**: Job completes successfully or fails with an error

## 📦 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@db:5432/jobdb` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `ENVIRONMENT` | Application environment | `development` |
| `FLOWER_BASIC_AUTH` | Basic auth for Flower dashboard | `admin:admin` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/0` |

## 🤝 Contributing

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/yourusername/stealth.git
   cd stealth
   ```
3. **Set up** the development environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. **Make** your changes and commit them
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```
6. **Push** to your fork
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open** a Pull Request on GitHub

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryq.dev/)
- [Redis](https://redis.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)