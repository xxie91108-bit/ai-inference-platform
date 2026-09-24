# AI Inference Platform

A lightweight AI model serving and infrastructure project built with **FastAPI, PyTorch, Docker, Prometheus, Grafana, and GitHub Actions**.

The project demonstrates how a machine learning model can be packaged as a production-style inference service, containerized with Docker, monitored with Prometheus and Grafana, tested under concurrent traffic, and validated automatically through CI.

---

## Overview

This project explores the infrastructure around serving machine learning models rather than focusing only on model training.

The system provides:

- PyTorch model inference
- REST API serving with FastAPI
- Docker containerization
- Multi-service orchestration with Docker Compose
- Prometheus metrics collection
- Grafana monitoring dashboards
- Model warm-up
- Container health checks
- Concurrent load testing
- P50 / P95 / P99 latency measurement
- Automated API testing
- GitHub Actions CI

---

## Architecture

```text
                         Client / Load Tester
                                 |
                                 | HTTP
                                 v
                      +----------------------+
                      |   AI Model Server    |
                      |                      |
                      | FastAPI + PyTorch    |
                      |      Port 8000       |
                      +----------+-----------+
                                 |
                                 | /metrics
                                 v
                      +----------------------+
                      |      Prometheus      |
                      |      Port 9090       |
                      +----------+-----------+
                                 |
                                 | PromQL
                                 v
                      +----------------------+
                      |       Grafana        |
                      |      Port 3000       |
                      +----------------------+

                  All services run with Docker Compose
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Model | PyTorch |
| API | FastAPI |
| Server | Uvicorn |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Metrics | Prometheus |
| Visualization | Grafana |
| Load Testing | Python + ThreadPoolExecutor |
| Testing | Pytest |
| CI | GitHub Actions |

---

## Project Structure

```text
ai-inference-platform/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── tests/
│   └── test_api.py
│
├── app.py
├── model.py
├── load_test.py
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Model Serving

The current project uses a lightweight PyTorch model to keep the infrastructure experiments reproducible and inexpensive.

The model implements a simple linear transformation:

```text
prediction = 2 × input + 1
```

For example:

```text
Input: 10
Prediction: 21
```

The model is placed in evaluation mode and inference is executed using `torch.inference_mode()`.

A dummy inference is also performed during initialization as a simple **model warm-up** step before real traffic is served.

The simple model is intentional: the focus of this project is the **serving infrastructure, observability, benchmarking, and scaling behaviour**, rather than model accuracy.

---

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Prediction

```http
POST /predict
```

Example request:

```json
{
  "value": 10
}
```

Example response:

```json
{
  "input": 10,
  "prediction": 21,
  "latency_ms": 0.1
}
```

### Metrics

```http
GET /metrics
```

Exposes Prometheus-compatible metrics including:

```text
inference_requests_total
inference_latency_seconds
```

---

## Running the Platform

### Prerequisites

Install:

- Docker
- Docker Compose

Clone the repository:

```bash
git clone https://github.com/xxie91108-bit/ai-inference-platform.git
cd ai-inference-platform
```

Start the complete stack:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

The model server includes a Docker health check, so a healthy deployment should show the model container as:

```text
healthy
```

---

## Services

After startup:

| Service | Address |
|---|---|
| FastAPI | `http://localhost:8000` |
| API Documentation | `http://localhost:8000/docs` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |

---

## Observability

Prometheus scrapes metrics exposed by the FastAPI model server.

The Grafana dashboard monitors metrics such as:

- Total inference requests
- Requests per second (RPS)
- Average inference latency
- P95 inference latency

This provides visibility into how the inference service behaves as request concurrency increases.

---

## Load Testing

The project includes a Python-based concurrent load testing tool.

The benchmark measures:

- Successful requests
- Throughput
- Average client latency
- P50 latency
- P95 latency
- P99 latency

Example:

```bash
python load_test.py
```

The benchmark can test multiple concurrency levels:

```text
1
10
25
50
100
200
```

---

## Benchmark Results

Initial benchmark results from the local Docker/WSL development environment:

| Concurrency | Successful | Throughput (req/s) | Avg (ms) | P50 (ms) | P95 (ms) | P99 (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5000 | 673.46 | 1.42 | 1.35 | 1.77 | 2.58 |
| 10 | 5000 | 1172.72 | 8.19 | 8.01 | 10.44 | 12.39 |
| 25 | 5000 | 1192.81 | 19.61 | 19.31 | 26.03 | 29.97 |
| 50 | 5000 | 1069.33 | 42.88 | 40.79 | 62.64 | 110.88 |
| 100 | 5000 | 1053.86 | 80.75 | 77.75 | 127.11 | 213.96 |
| 200 | 2571 | 214.05 | 106.26 | 104.82 | 227.31 | 282.25 |

### Initial observations

Throughput increased substantially between concurrency 1 and 10 and reached approximately **1.19K requests/second** in this test around concurrency 25.

Beyond this region, additional concurrency did not improve throughput and tail latency increased significantly. For example, P99 latency increased from approximately 30 ms at concurrency 25 to more than 200 ms at concurrency 100.

The 5000-request run at concurrency 200 also experienced request failures. However, a later shorter 500-request experiment at concurrency 200 completed successfully at approximately 1006 req/s.

Therefore, the concurrency-200 result should not yet be interpreted as a fixed server capacity limit. Further repeated testing and resource monitoring are required to distinguish server saturation from client-side, runtime, Docker/WSL, or other environmental effects.

---

## Testing

API tests are implemented with Pytest.

Run locally:

```bash
pytest -v
```

Current tests validate core endpoints including:

- `/health`
- `/predict`

---

## Continuous Integration

GitHub Actions automatically validates changes pushed to the repository.

The CI pipeline performs:

```text
Checkout source code
        ↓
Set up Python
        ↓
Install dependencies
        ↓
Run Pytest
        ↓
Build Docker image
        ↓
CI Pass / Fail
```

This ensures that API functionality and container builds are automatically checked after code changes.

---

## Engineering Concepts Explored

This project currently demonstrates several concepts relevant to AI infrastructure and model serving:

**Model Serving**
- REST-based inference
- PyTorch inference mode
- Model warm-up

**Containerization**
- Docker images
- Docker Compose
- Container health checks
- Persistent Grafana storage

**Observability**
- Application metrics
- Prometheus
- Grafana
- Request rate and latency monitoring

**Performance Engineering**
- Concurrent load generation
- Throughput measurement
- P50 / P95 / P99 latency
- Tail latency
- Saturation analysis

**Software Engineering**
- Automated testing
- Git version control
- GitHub Actions CI

---

## Roadmap

Planned improvements include:

- Automated benchmark result export
- Performance visualization
- Concurrency limiting and backpressure
- Dynamic request batching
- Structured logging
- Improved Prometheus latency buckets
- Model serving optimization
- Kubernetes deployment
- Horizontal scaling and autoscaling
- Comparative benchmarks before and after optimization

---

## Current Goal

The long-term goal of this project is to evolve a simple PyTorch inference API into a small but reproducible **AI inference infrastructure platform**, and to experimentally study the trade-offs between:

```text
Throughput
Latency
Concurrency
Reliability
Resource utilization
```

The project is being developed incrementally so that each infrastructure component can be measured and evaluated independently.