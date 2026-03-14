# Docker Nginx Flask Task Manager

A production‑style **multi‑container web application** built using
**Docker, Flask, Nginx, PostgreSQL, and Redis**.

This project demonstrates how to containerize a Python application and
run it with multiple services using **Docker Compose**.

------------------------------------------------------------------------

## Architecture

The application consists of the following services:

-   **Nginx** -- Reverse proxy and load balancer
-   **Flask (2 instances)** -- Python API application
-   **PostgreSQL** -- Main database
-   **Redis** -- Cache layer
-   **Docker Compose** -- Container orchestration

Architecture flow:

Client → Nginx → Flask (x2) → PostgreSQL\
↘ Redis Cache

------------------------------------------------------------------------

## Features

-   REST API for managing tasks
-   Redis caching for better performance
-   PostgreSQL persistent storage
-   Health checks for services
-   Nginx reverse proxy
-   Multi‑container Docker environment

------------------------------------------------------------------------

## Project Structure

    .
    ├── docker-compose.yml
    ├── Dockerfile
    ├── flask_app.py
    ├── requirements.txt
    ├── init.sql
    ├── .env.example
    ├── conf/nginx.conf
    └── static/

------------------------------------------------------------------------

## Requirements

You only need:

-   Docker
-   Docker Compose

Install Docker from: https://docs.docker.com/get-docker/

------------------------------------------------------------------------

## Run the Project

Clone the repository:

``` bash
git clone https://github.com/YOUR_USERNAME/docker-nginx-flask-app.git
cd docker-nginx-flask-app
```

Start the containers:

``` bash
docker compose up --build
```

------------------------------------------------------------------------

## Access the Application

Open your browser:

    http://localhost

------------------------------------------------------------------------

## API Endpoints

### Health Check

    GET /api/health

Example response:

``` json
{
  "status": "healthy",
  "db": true,
  "redis": true
}
```

------------------------------------------------------------------------

### Get Tasks

    GET /api/tasks

------------------------------------------------------------------------

### Add Task

    POST /api/tasks

Example:

``` json
{
  "title": "Learn Docker",
  "priority": "high"
}
```

------------------------------------------------------------------------

### Complete Task

    PATCH /api/tasks/{task_id}/done

------------------------------------------------------------------------

## Docker Services

  Service    Description
  ---------- ---------------------
  nginx      Reverse proxy
  flask1     Flask API instance
  flask2     Flask API instance
  postgres   PostgreSQL database
  redis      Redis cache

------------------------------------------------------------------------

## Database

The database initializes automatically using `init.sql`.

Example table:

    tasks
    - id
    - title
    - priority
    - done
    - created_at

------------------------------------------------------------------------

## Tech Stack

-   Python
-   Flask
-   PostgreSQL
-   Redis
-   Nginx
-   Docker
-   Docker Compose

------------------------------------------------------------------------

## Author

**Ebrahim Ashraf**\
DevOps & Cloud Enthusiast
