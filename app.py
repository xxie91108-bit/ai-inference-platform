import time

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from model import model


app = FastAPI(title="AI Infra Model Server")


class PredictRequest(BaseModel):
    value: float


# -------------------------
# Prometheus Metrics
# -------------------------

REQUEST_COUNT = Counter(
    "inference_requests_total",
    "Total number of inference requests"
)

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds"
)


@app.get("/")
def root():
    return {
        "service": "AI Infra Model Server",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict")
def predict(request: PredictRequest):

    tensor = torch.tensor(
        [[request.value]],
        dtype=torch.float32
    )

    start_time = time.perf_counter()

    with torch.inference_mode():
        output = model(tensor)

    latency_seconds = time.perf_counter() - start_time

    # Record Prometheus metrics
    REQUEST_COUNT.inc()
    INFERENCE_LATENCY.observe(latency_seconds)

    return {
        "input": request.value,
        "prediction": output.item(),
        "latency_ms": round(latency_seconds * 1000, 3)
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )