```
HTTP request
  → FastAPI handler (OpenAIServingChat)   turns JSON into a prompt and SamplingParams
  → AsyncLLM.generate()                   async generator that yields outputs
  → EngineCore (a separate process)       schedules requests and runs the GPU
  ← tokens stream back                     the handler turns them into JSON or SSE
```

api server
- `vllm/entrypoints/launchers/api_server/entry.py`
- The one thing to understand: the API server is a thin HTTP layer in front of AsyncLLM. It never runs the model itself.

AsyncLLM

```
┌──────── API server process ────────┐        ┌── EngineCore process ──┐
│ FastAPI → AsyncLLM → AsyncMPClient │ ◄ZMQ►  │ EngineCore → GPU       │
└────────────────────────────────────┘        └────────────────────────┘

```

EngineCore
- EngineCoreProc
- Scheduler (chunked prefill happens here)
- KV cache manager (paged attention)
- Executor → Worker → ModelRunner (actually running the model)