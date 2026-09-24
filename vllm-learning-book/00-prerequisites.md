
## lifecycle of a request
`vllm/v1/engine/llm_engine.py`
- `add_request`: adds a request
- request datatype - `EngineCoreRequest`

`vllm/v1/engine/core_client.py`
- `InprocClient`: inter-process client

`vllm/v1/engine/core.py`
- TBA

`vllm/v1/core/sched/scheduler.py`
- TBA
  
`vllm/v1/worker/gpu_model_runner.py`
- TBA

## concepts
- auto-regressive
- why kv-cache is necessary? (To avoid recomputing the K and V representations of all previous tokens during autoregressive decoding. For a sequence t1 t2 t3 t4, when generating/processing t5, the K/V values of t1–t4 have already been computed and can be reused from the KV cache. We only need to compute the new Q/K/V for t5.)
- prefill vs decode (compute-bound vs memory bound)
- roofline model (arithmetic intensity = flops / bytes read or write, higher => compute-bound, lower => memory bound)
- DP, TP, PP
  - DP: data parallel, distribute the same model across GPUs
  - TP: tensor parallel, distribute the weights of the same layer across GPUs
  - PP: pipeline parallel,  distribute the layers of the same model across GPUs
- Metrics
  - TTFT: is it "sluggish"?
  - TPOT (time per output token): how smooth is it?
  - throughput: tokens per sec, requests per sec
