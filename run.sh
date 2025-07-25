#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage information
show_help() {
    echo -e "${YELLOW}Usage: ./run.sh [command]${NC}"
    echo ""
    echo "Commands:"
    echo "  up           Start all services in detached mode"
    echo "  down         Stop and remove all services"
    echo "  build        Rebuild all services"
    echo "  logs         Show logs for all services"
    echo "  status       Show status of all services"
    echo "  test         Run tests"
    echo "  shell        Open a shell in the web container"
    echo "  db-shell     Open a PostgreSQL shell"
    echo "  redis-cli    Open a Redis CLI"
    echo "  help         Show this help message"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}" >&2
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}Error: docker compose is not installed. Please install it and try again.${NC}" >&2
        exit 1
    fi
}

# Function to start services
start_services() {
    echo -e "${GREEN}Starting services...${NC}"
    docker compose up -d
    echo -e "${GREEN}Services started successfully!${NC}"
    echo -e "${YELLOW}API Documentation: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}Flower (Celery Monitor): http://localhost:5555${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    docker compose down
    echo -e "${GREEN}Services stopped successfully!${NC}"
}

# Function to rebuild services
rebuild_services() {
    echo -e "${YELLOW}Rebuilding services...${NC}"
    docker compose build --no-cache
    echo -e "${GREEN}Services rebuilt successfully!${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing logs (press Ctrl+C to exit)...${NC}"
    docker compose logs -f
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Service Status:${NC}"
    docker compose ps
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    docker compose exec web pytest tests/ -v
}

# Function to open a shell in the web container
open_shell() {
    echo -e "${YELLOW}Opening shell in web container...${NC}"
    docker compose exec web /bin/bash
}

# Function to open a PostgreSQL shell
open_db_shell() {
    echo -e "${YELLOW}Opening PostgreSQL shell...${NC}"
    echo -e "${YELLOW}Database: jobdb, User: postgres${NC}"
    docker compose exec db psql -U postgres -d jobdb
}

# Function to open Redis CLI
open_redis_cli() {
    echo -e "${YELLOW}Opening Redis CLI...${NC}"
    docker compose exec redis redis-cli
}

# Main script execution
check_docker
check_docker_compose

case "$1" in
    up)
        start_services
        ;;
    down)
        stop_services
        ;;
    build)
        rebuild_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    test)
        run_tests
        ;;
    shell)
        open_shell
        ;;
    db-shell)
        open_db_shell
        ;;
    redis-cli)
        open_redis_cli
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac

exit 0
