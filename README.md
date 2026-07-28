# Awesome AI Infrastructure

> A curated guide to modern AI infrastructure—from a user request to GPU execution and production deployment.

---

# 🗺️ Learning Roadmap

```text
                User Request
                     │
                     ▼
          API Gateway & Routing
                     │
                     ▼
           Retrieval / RAG (Optional)
                     │
                     ▼
        LLM Serving & Inference Runtime
                     │
                     ▼
        GPU Runtime & Parallelism
                     │
                     ▼
      Cluster Orchestration (Kubernetes)
                     │
                     ▼
      Observability & Production Ops
```

---

# 1. LLM Serving & Inference Runtime

> How do modern inference engines efficiently serve many concurrent LLM requests?

### Scheduling
- [ ] Continuous Batching
- [ ] Chunked Prefill
- [ ] Prefill vs Decode
- [ ] TTFT / ITL / TPS Metrics

### Memory Management
- [ ] KV Cache
- [ ] PagedAttention
- [ ] Prefix / Prompt Cache
- [ ] Context Window Management

### Inference Optimization
- [ ] Speculative Decoding
- [ ] Structured Outputs
- [ ] Dynamic Batching
- [ ] Streaming Responses

### Model Optimization
- [ ] FP16 / BF16 / FP8
- [ ] GPTQ
- [ ] AWQ
- [ ] LoRA
- [ ] QLoRA
- [ ] Unsloth

### Runtime Implementations
- [ ] vLLM
- [ ] SGLang
- [ ] TensorRT-LLM
- [ ] llama.cpp

---

# 2. GPU Systems & Distributed Inference

> How do multiple GPUs serve one large model?

### GPU Fundamentals
- [ ] CUDA Basics
- [ ] GPU Memory Hierarchy
- [ ] CUDA Streams
- [ ] CUDA Graphs
- [ ] FlashAttention

### Parallelism
- [ ] Tensor Parallelism
- [ ] Pipeline Parallelism
- [ ] Data Parallelism
- [ ] Expert Parallelism (MoE)
- [ ] Context Parallelism

### Multi-Node Inference
- [ ] NCCL
- [ ] RDMA / InfiniBand
- [ ] Multi-Node Deployment
- [ ] Elastic Scaling

---

# 3. Retrieval & RAG Infrastructure

> How do LLMs retrieve external knowledge?

### Embeddings
- [ ] Embedding Models
- [ ] Chunking Strategies
- [ ] Metadata Filtering

### Vector Search
- [ ] ANN Fundamentals
- [ ] HNSW
- [ ] IVF
- [ ] Product Quantization (PQ)
- [ ] Hybrid Search

### RAG Pipeline
- [ ] Query Rewriting
- [ ] Reranking
- [ ] Context Construction
- [ ] Semantic Cache

### Vector Databases
- [ ] Milvus
- [ ] Qdrant
- [ ] pgvector
- [ ] Weaviate

---

# 4. AI Gateway & Production Services

> Everything before the request reaches the model.

### API Gateway
- [ ] Authentication
- [ ] Rate Limiting
- [ ] Token-based Quotas
- [ ] Retry & Circuit Breakers

### Traffic Management
- [ ] Load Balancing
- [ ] Model Routing
- [ ] A/B Testing
- [ ] Canary Deployments
- [ ] Multi-Region Failover

### Caching
- [ ] Prompt Cache
- [ ] Semantic Cache
- [ ] Response Cache
- [ ] Redis

---

# 5. Kubernetes & Cloud Infrastructure

> How do we deploy and scale AI systems?

### Kubernetes Fundamentals
- [ ] Pods
- [ ] Deployments
- [ ] Services
- [ ] StatefulSets

### GPU Scheduling
- [ ] NVIDIA Device Plugin
- [ ] MIG
- [ ] GPU Time Slicing

### Scaling
- [ ] HPA
- [ ] KEDA
- [ ] Cluster Autoscaler

### AI Frameworks
- [ ] Ray
- [ ] KubeRay
- [ ] Ray Serve

### Storage
- [ ] Persistent Volumes
- [ ] Model Weight Caching
- [ ] Fast Checkpoint Loading

---

# 6. Observability & Reliability

> How do we operate AI systems in production?

### Metrics
- [ ] TTFT
- [ ] ITL
- [ ] Throughput
- [ ] Queue Length
- [ ] GPU Utilization
- [ ] KV Cache Usage

### Monitoring
- [ ] Prometheus
- [ ] Grafana
- [ ] OpenTelemetry

### Logging & Tracing
- [ ] Distributed Tracing
- [ ] Request Logs
- [ ] Token-Level Metrics

### Reliability
- [ ] SLOs
- [ ] Error Budgets
- [ ] Health Checks
- [ ] Load Testing

---

# 📚 Learning Resources

## Papers

### Inference
- [ ] TBD

### Distributed Systems
- [ ] TBD

### Retrieval
- [ ] TBD

---

## Engineering Blogs

### OpenAI
- [ ] TBD

### Anthropic
- [ ] TBD

### NVIDIA
- [ ] TBD

### vLLM
- [ ] TBD

### Databricks
- [ ] TBD

---

## Source Code

- [ ] vLLM
- [ ] SGLang
- [ ] TensorRT-LLM
- [ ] Ray
- [ ] KubeRay

---

## Books

- [ ] Designing Data-Intensive Applications
- [ ] Kubernetes in Action
- [ ] CUDA Programming Guide

---

# 🛠️ Hands-on Projects

## Beginner

- [ ] Deploy vLLM locally
- [ ] Benchmark different quantization methods
- [ ] Build a simple RAG service

## Intermediate

- [ ] Deploy vLLM on Kubernetes
- [ ] Build an AI Gateway with rate limiting
- [ ] Configure autoscaling based on queue length

## Advanced

- [ ] Multi-node Tensor Parallel deployment
- [ ] Production monitoring dashboard
- [ ] Benchmark continuous batching strategies
- [ ] Build a high-throughput LLM serving platform