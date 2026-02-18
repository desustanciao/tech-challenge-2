# tech-challenge

A **FastAPI application deployed on AWS** that exposes REST endpoints, health checks, metrics, authentication, and item access-structured with a layered architecture, database integration, and observability tooling.


## Project Overview

This project implements a backend API using **FastAPI**, designed to be scalable, testable, and cloud-ready. It follows modern practices:

- Asynchronous FastAPI server
- PostgreSQL integration using SQLAlchemy with async sessions
- Authentication endpoints (JWT & cookies)
- Health and Liveness checks
- Prometheus metrics support
- Docker + AWS deployment readiness
- Infrastructure defined using AWS CDK (`cdk/` folder)

---

## Features

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/live` | GET | Liveness check — verifies server is running |
| `/health/ready` | GET | Readiness check — verifies database connectivity |
| `/items` | GET | Returns a list of items (protected route) |
| `/get_token` | POST | Generates a new bearer access token for a user |
| `/get_cookie` | GET | Sets an HTTP-only cookie with a token |
| `/logout` | GET | Clears user session (cookie) |
| `/metrics` | GET | Prometheus metrics endpoint |

---

### Architecture Diagram

## Network Diagram
```mermaid
flowchart TD
  Client["Client / Browser"] -->|HTTP/HTTPS| App["FastAPI App (Public Subnet)"]
  App -->|DB Connection| DB["PostgreSQL RDS (Private Subnet)"]
  subgraph Public_Subnet
      App
      IGW["Internet Gateway"]
  end
  subgraph Private_Subnet
      DB
  end
  App --> IGW
```

## Application Diagram
```mermaid
flowchart TD

    %% Clients
    A[Client<br/>Browser / API Consumer]

    %% API Layer
    B[FastAPI Application<br/>app.main]
    C[Routers<br/>Health / Auth / Items / Metrics]
    D[Middleware<br/>Auth / Logging / Metrics]

    %% Business Layer
    E[Service Layer<br/>Business Logic]
    F[Security Module<br/>JWT Handling]

    %% Data Layer
    G[Repository Layer<br/>SQLAlchemy Async]
    H[(PostgreSQL Database)]

    %% Observability
    I[Prometheus Metrics Endpoint]
    
    %% Infrastructure
    J[Docker Container]
    K[AWS Infrastructure<br/>Defined with CDK]

    %% Flows
    A -->|HTTP Requests| B
    B --> C
    B --> D
    C --> E
    E --> G
    G --> H

    C --> F
    F --> C

    D --> I

    B --> J
    J --> K
```

## Tech Stack
| Category       | Technology              |
| -------------- | ----------------------- |
| Framework      | FastAPI                 |
| Python Version | ≥ 3.12                  |
| Async ORM      | SQLAlchemy (asyncio)    |
| ASGI Server    | Uvicorn                 |
| Metrics        | Prometheus              |
| Database       | PostgreSQL              |
| Deployment     | Docker, AWS CDK         |
| Testing        | Pytest + pytest-asyncio |
| Linting        | Ruff                    |

## Running the Application with uv

Prepare an .env file with the following data:
````txt
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_NAME=appdb
LOCAL=true
SECRET_KEY=
````
If you don’t have uv installed:
```bash
pip install uv
```
Or via the official installer:
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```
Install dependencies
```bash
uv sync
```
Run the application
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

