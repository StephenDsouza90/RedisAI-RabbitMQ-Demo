# AIMQ Demo - RedisAI | RabbitMQ

## Overview

Scalable ML Pipeline with **RabbitMQ** (message queueing) & **RedisAI** (model caching and inference)

## Key Features

- ✅ **Asynchronous Processing** - Decoupled microservices via RabbitMQ
- ✅ **Low-Latency Inference** - RedisAI-accelerated model serving
- ✅ **Benchmark Ready** - Compare ONNX vs Pickle performance
- ✅ **Production-Grade** - Dockerized with health checks

## Architecture Components

![design](assets/architecture/app-architecture.jpg)

### 1. **Interface Service**

**Responsibilities**:

- REST API for file uploads/downloads and predicts
- Publishes messages to RabbitMQ exchange
- Local filesystem storage

**Tech**: Go, Gin framework, RabbitMQ client

### 2. **Batch Processor**

**Workflow**:

- Consumes messages from queue
- Transforms Excel → Pandas DataFrame
- Calls ML Service via HTTP with payload
- Saves predictions back to storage

**Tech**: Python, Pandas, Pika (RabbitMQ client)

### 3. **ML Service**

**Core Functions**:

- `/predict/onnx`: Uses RedisAI-cached models (fast)
- `/predict/pickle`: Traditional disk-loaded models (slow)
- Auto-caches models at startup
- Rate-limited API endpoints

**Tech**: Python, FastAPI, RedisAI, ONNX runtime, Scikit-learn

## Benchmark Results

**Multiple (1000) Request**

| Endpoint        | Seconds |
|-----------------|---------|
| /predict/onnx   | 4.36    |
| /predict/pickle	| 222.69  |

## Tech Stack

- **Messaging**: RabbitMQ
- **AI Caching**: Redis, RedisAI
- **Languages**: Go (API), Python (ML/Batch)
- **Storage**: (Local)
- **Containerization**: Docker
- **Orchestration**: Docker Compose, Kubernetes

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.12

## Detailed Documentation

### 1. **Interface Service**

The Interface Service serves as the system’s entry point, handling both batch and real-time prediction workflows. For batch processing, it accepts file uploads, stores them in persistent storage, and publishes structured messages to RabbitMQ containing file metadata. This decoupled approach ensures reliable processing even if downstream services are temporarily unavailable. For low-latency needs, it also provides a synchronous prediction endpoint that directly queries the ML Service, bypassing the queue. RabbitMQ was chosen for its message durability, support for backpressure handling, and ability to decouple producers from consumers—critical for maintaining system resilience during peak loads or service restarts.

### 2. **Batch Processor**

The Batch Processor subscribes to RabbitMQ, processing files asynchronously by converting them into structured DataFrames, enriching them with predictions from the ML Service, and saving the results. It implements robust error handling, including dead-letter queues for failed messages and automatic retries with exponential backoff. Performance optimizations include batch message prefetching and parallel processing for independent files. By isolating file parsing and data preparation in this service, the ML Service remains focused on inference, improving scalability.


### 3. **ML Service**

The ML Service handles both ETL and inference. During ETL, it preprocesses training data (e.g., encoding categorical features) and exports models to `ONNX` format, which is optimized for RedisAI’s tensor-based execution. Two inference endpoints showcase the performance impact of caching: the `/predict/onnx` endpoint leverages RedisAI’s in-memory models for predictions, while `/predict/pickle` serves as a baseline, loading models from disk with higher latency. RedisAI’s tensor operations enable efficient batch predictions, and models are preloaded at startup to eliminate cold starts. Rate limiting protects against overload, with dynamic adjustments based on system health.

## Quick Start with Docker Compose (Locally)

1. **Clone the repository:**

```
git clone https://github.com/StephenDsouza90/RedisAI-RabbitMQ-Demo.git
cd RedisAI-RabbitMQ-Demo
```

2. **Run ETL Pipeline to create models:**

```python
# Install packages and dependencies
pip install -r requirements.txt

# Generate ML artifacts
python ml/etl/main.py
```

3. **Start all services:**

```docker
# Launch all services
docker-compose up --build -d

# Verify services (Should show 6 containers)
docker ps
```

4. **Usage Examples - Interface Service:**

```
# Upload file for batch processing
curl -X POST http://localhost:8080/upload -F "file=@assets/sample_files/1_row.xlsx"

# Real-time prediction
curl -X POST http://localhost:8080/predict \
-H "Content-Type: application/json" \
-d '{
  "model_group": "A",
  "model": 180,
  "kilometers": 5000,
  "fuel_type": "Diesel",
  "gear_type": "Manual",
  "vehicle_type": "Sedan Car",
  "age_in_months": 12,
  "color": "Black",
  "line": "Sportline",
  "doors": "4 to 5",
  "seats": "1 to 3",
  "climate": "Air Conditioning"
}'
```

5. **Monitoring (If needed):**

| Service     | URL                        |
|-------------|----------------------------|
| RabbitMQ UI | http://localhost:15672     |
| ML API Docs | http://localhost:5001/docs |

6. **Stop services:**

```
docker-compose down
docker-compose down -v
```

## Quick Start with Kubernetes (Locally)

## Testing
