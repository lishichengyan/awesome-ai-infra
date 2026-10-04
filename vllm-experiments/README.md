# Benchmark something
Notes and results: [benchmark-something.md](benchmark-something/benchmark-something.md)

Parameters to explore:

| Parameter | Set on | What it tests | Expected effect | Status |
| --- | --- | --- | --- | --- |
| `--max-concurrency` | client | Batch size and queueing | Throughput ↑, TPOT ↑, TTFT ↑ once requests queue | Done |
| `--random-input-len` | client | Prefill work | TTFT ↑, decode barely changes | Done |
| `--random-output-len` | client | Decode work | Total time ↑, TTFT unchanged | Done |
| `--max-num-seqs` | server | Batch size cap | Throughput ↑ up to a knee, TPOT ↑, TTFT ↓ | Done |
| `--max-num-batched-tokens` | server | Tokens per step (prefill chunk size) | Small: lower p99 ITL, higher TTFT. Large: the reverse | TODO |
| `VLLM_CPU_KVCACHE_SPACE` | server | KV cache memory limit | Too small: preemption, throughput ↓ | TODO |
| `--max-model-len` | server | Worst-case memory per request | Changes how many requests fit in KV memory | TODO |
| Prefix caching on vs. off | server | Skipping repeated prefill | TTFT ↓ for shared prefixes, TPOT unchanged | TODO |
| `--request-rate` | client | Requests at a fixed rate, like real users | Past capacity, the queue and TTFT keep growing | TODO |
| `VLLM_CPU_OMP_THREADS_BIND` | server | CPU cores (compute per step) | Fewer cores: slower steps, TPOT ↑ | TODO |
| `--dtype float16` vs. `float32` | server | Bytes per weight and KV entry | float32: TPOT ↑, half the KV capacity | TODO |
| `--enforce-eager` | server | torch.compile on vs. off | Eager: slower steps, faster startup | TODO |
| Qwen2-0.5B vs. Qwen2-1.5B | server | Model size | Larger: every step slower | TODO |

# Trace a request
TBA

# Make some trouble
TBA

# Support miniGPT
TBA
