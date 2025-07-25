#!/bin/bash

# Exit on error
set -e

echo "Starting test environment..."
docker-compose up -d db redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

echo "Running tests..."
docker-compose run --rm web pytest tests/ -v $@

echo "Stopping test environment..."
docker-compose down
