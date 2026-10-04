# Benchmark-something

## Install dependencies
```
cd ~/mycode/vllm
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements/cpu.txt
uv pip install -e .
```

## Run the server locally
```
VLLM_CPU_KVCACHE_SPACE=8 vllm serve Qwen/Qwen2-0.5B \
  --dtype float16 --max-model-len 2048 --max-num-seqs 16
```

* `VLLM_CPU_KVCACHE_SPACE` specifies the size of the KV cache.

* On macOS only float16 and float32 are supported, hence we explicitly use float16 instead of letting vLLM fall back or fail.

* `--max-model-len` specifies the max length of a request.

* `--max-num-seqs` specified the max number of requests in a batch.

Once successful, we'll see something like -

![Server](./resources/server-success.png)

Note this

> CPU KV cache size: 699,008 tokens, Maximum concurrency for 2,048 tokens per request: 341.31x

How is `699008` derived? Let's do some arithmetic:
```
KV per token = 2 (K and V) * 24 layers * 2 heads * 64 dims * 2 bytes = 12 KB

8GB = 1024 * 1024 * 8 KB = 8388608 KB

8388608 / 12 = 699050.6666666666
```
Why vLLM gave us a number slightly smaller than 699050? This is because it allocates **per block**, not **per token**, and on CPU the default is 128 tokens per block.

```
699050 / 128 = 5461.33 blocks

5461 blocks * 128 = 699008 tokens 

699008 tokens / 2,048 tokens per request = 341.31
```

Test the server locally
```
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2-0.5B",
    "prompt": "The capital of France is",
    "max_tokens": 30,
    "temperature": 0
  }'

{"id":"cmpl-adb0bea38c70d633","object":"text_completion","created":1790552018,"model":"Qwen/Qwen2-0.5B","choices":[{"index":0,"text":" Paris. It is the largest city in France and the second largest in Europe. It is the capital of the Fifth Republic, the country's second largest","logprobs":null,"finish_reason":"length","stop_reason":null,"token_ids":null,"prompt_logprobs":null,"prompt_token_ids":null,"routed_experts":null}],"service_tier":null,"system_fingerprint":"vllm-0.1.dev21981+ge440b75bb-8893dc75","usage":{"prompt_tokens":5,"total_tokens":35,"completion_tokens":30,"prompt_tokens_details":null,"completion_tokens_details":null},"kv_transfer_params":null,"ec_transfer_params":null,"metrics":null}% 
```

## Benchmark and lessons 
In a second terminal, point to the venv of our local vLLM (on my machine I have conda installed and loaded by default, deactivate to keep things clean):
```
cd ~/mycode/vllm
conda deactivate
source .venv/bin/activate
```
Then run
```
vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
  --random-input-len 256 --random-output-len 128 \
  --num-prompts 20 --max-concurrency 1 \
  --save-result --result-dir bench_results/
```
| Argument                      | Meaning                                                           |
| ----------------------------- | ----------------------------------------------------------------- |
| `vllm bench serve`            | Benchmark a **running inference server**                          |
| `--model Qwen/Qwen2-0.5B`     | Tell the benchmark you're testing the Qwen2 0.5B model            |
| `--dataset-name random`       | Generate synthetic/random prompts instead of using a real dataset |
| `--random-input-len 256`      | Each prompt is approximately **256 tokens long**                  |
| `--random-output-len 128`     | Request approximately **128 generated tokens**                    |
| `--num-prompts 20`            | Send **20 requests total**                                        |
| `--max-concurrency 1`         | Only **one request is in flight at a time**                       |
| `--save-result`               | Save benchmark statistics                                         |
| `--result-dir bench_results/` | Put the result files in this directory                            |

Results
```
(MainProcess pid=39376) INFO 09-27 16:47:52 [utils.py:88] Sampling input_len from [256, 256] and output_len from [128, 128]
WARNING: vllm bench serve no longer sets temperature==0 (greedy) in requests by default. The default will be determined on the server side and can be model/API specific. For the old behavior, include --temperature=0.
Starting initial single prompt test run...
Skipping endpoint ready check.
Starting main benchmark run...
Traffic request rate: inf
Burstiness factor: 1.0 (Poisson process)
Maximum request concurrency: 1
100%|███████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [01:05<00:00,  3.28s/it]
tip: install termplotlib and gnuplot to plot the metrics
============ Serving Benchmark Result ============
Successful requests:                     20        
Failed requests:                         0         
Maximum request concurrency:             1         
Benchmark duration (s):                  65.68     
Total input tokens:                      5120      
Total generated tokens:                  2560      
Request throughput (req/s):              0.30      
Output token throughput (tok/s):         38.98     
Peak output token throughput (tok/s):    46.00     
Peak concurrent requests:                2.00      
Total token throughput (tok/s):          116.94    
---------------Time to First Token----------------
Mean TTFT (ms):                          466.97    
Median TTFT (ms):                        425.14    
P99 TTFT (ms):                           1190.31   
-----Time per Output Token (excl. 1st token)------
Mean TPOT (ms):                          22.18     
Median TPOT (ms):                        22.16     
P99 TPOT (ms):                           22.50     
---------------Inter-token Latency----------------
Mean ITL (ms):                           22.18     
Median ITL (ms):                         22.06     
P99 ITL (ms):                            24.47     
==================================================
```

* Time to First Token: how long does it take to respond with the first token? -> How long until I see something?

* Time per Output Token: measures how long the model takes, on average, to produce each new token after the first token has been generated. -> How fast is generation overall?

* Inter-token Latency: is the actual time gap between two consecutive output tokens arriving. -> How consistently do tokens arrive?

Let's try to tweak the parameters and see what will happen - 
```
Task 1: --max-concurrency 1, 2, 4, 8, 16

Task 2: --random-input-len 128, 512, 1024

Task 3: --random-output-len 32, 128, 512

Task 4: Restart the server with --max-num-seqs 4 vs 16 vs 32

Task 5 (optional): Restart the server with --max-num-batched-tokens small vs large

Task 6 (optional): Restart the server with a smaller VLLM_CPU_KVCACHE_SPACE until requests get preempted

--dataset-name prefix_repetition, with prefix caching on vs --no-enable-prefix-caching
```
### "Throughput-vs-latency tradeoff"
Increase CPU cores:
```
for c in 1 2 4 8 16; do
  vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
    --random-input-len 256 --random-output-len 128 \
    --num-prompts $((c * 8)) --max-concurrency $c \
    --save-result --result-dir bench_results/ --result-filename conc_$c.json
done
```

| Concurrency | Output tok/s | Speedup | Median TTFT | P99 TTFT | Median TPOT | P99 TPOT |
| ----------: | -----------: | ------: | ----------: | -------: | ----------: | -------: |
|           1 |         40.7 |    1.0× |      226 ms |   234 ms |     23.1 ms |  23.3 ms |
|           2 |         73.5 |    1.8× |      350 ms |   471 ms |     24.7 ms |  25.6 ms |
|           4 |        111.9 |    2.8× |      764 ms | 1,550 ms |     27.8 ms |  37.2 ms |
|           8 |        145.4 |    3.6× |    1,614 ms | 2,929 ms |     38.6 ms |  58.7 ms |
|          16 |        184.1 |    4.5× |    2,797 ms | 5,461 ms |     57.6 ms |  94.5 ms |

### "Prefill" vs "Decode" balance
Increase the input length:
```
# warm-up - the intention is to get the server / model 
# into a warmed-up state before taking measurements
# for example, avoiding some first-run initialization effects.

vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
  --random-input-len 1024 --random-output-len 32 --num-prompts 4

for len in 128 512 1024; do
  vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
    --random-input-len $len --random-output-len 128 \
    --num-prompts 32 --max-concurrency 4 \
    --save-result --result-dir bench_results/ --result-filename in${len}_c4.json
done
```
This will mainly affect the TTFT because it needs more time to "prefill" as the prompt length increases.

| Input Length | Output tok/s | Total tok/s | Median TTFT | Mean TTFT | Median TPOT | P99 TPOT |
| -----------: | -----------: | ----------: | ----------: | --------: | ----------: | -------: |
|          128 |        116.7 |         233 |      751 ms |    630 ms |     28.7 ms |  33.5 ms |
|          512 |        100.6 |         503 |    1,439 ms |  1,192 ms |     28.7 ms |  39.2 ms |
|         1024 |         79.5 |         715 |    2,979 ms |  2,288 ms |     28.7 ms |  48.7 ms |

Change output length:
```
for len in 128 512 1024; do
  vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
    --random-input-len $len --random-output-len 128 \
    --num-prompts 32 --max-concurrency 4 --seed $((1000 + len)) \
    --save-result --result-dir bench_results/ --result-filename in${len}_c4_clean.json
done
```
| Output Length | Median TTFT | Median TPOT | Total Latency | Output tok/s | Share of Time in Prefill |
| ------------: | ----------: | ----------: | ------------: | -----------: | -----------------------: |
|            32 |    1,401 ms |     28.2 ms |        2.29 s |         56.2 |                      61% |
|           128 |    1,411 ms |     28.5 ms |        5.04 s |        101.6 |                      28% |
|           512 |    1,454 ms |     28.7 ms |       16.09 s |        126.8 |                       9% |


The key observation is that output length mostly changes how long you spend decoding, not prefill.

### Batching helps, up to a point
`--max-num-seqs` sets how many requests the server batches together. Raising it trades per-token speed for throughput and shorter queues. On a GPU the first part of that trade is nearly free, because decode is limited by memory bandwidth. On CPU it isn't, as the results below show.

The server has to restart for each value, so stop the server in the other terminal first (it holds port 8000). Client concurrency is fixed at 32, so the server always has more requests than batch slots.
```
for s in 4 16 32; do
  VLLM_CPU_KVCACHE_SPACE=8 vllm serve Qwen/Qwen2-0.5B \
    --dtype float16 --max-model-len 2048 --max-num-seqs $s > server_seqs$s.log 2>&1 &
  SERVER_PID=$!
  echo "Starting server with --max-num-seqs $s (log: server_seqs$s.log)..."
  until curl -sf http://localhost:8000/health > /dev/null; do
    kill -0 $SERVER_PID 2>/dev/null || { echo "Server died, see server_seqs$s.log"; break 2; }
    sleep 2
  done
  echo "Server ready, benchmarking..."

  # warm-up
  vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
    --random-input-len 256 --random-output-len 32 --num-prompts 4

  vllm bench serve --model Qwen/Qwen2-0.5B --dataset-name random \
    --random-input-len 256 --random-output-len 128 \
    --num-prompts 96 --max-concurrency 32 --seed 42 \
    --save-result --result-dir bench_results/ --result-filename seqs${s}_c32.json

  kill $SERVER_PID; wait $SERVER_PID 2>/dev/null
done
```

| Max Num Seqs | Output tok/s | Speedup | Median TTFT | P99 TTFT | Median TPOT | P99 TPOT | P99 ITL | Duration |
| -----------: | -----------: | ------: | ----------: | -------: | ----------: | -------: | ------: | -------: |
|            4 |         98.9 |    1.0× |     36.9 s |   38.3 s |     32.2 ms |  40.2 ms |   46 ms |  124.2 s |
|           16 |        161.8 |    1.6× |     15.2 s |   18.0 s |     80.3 ms |  97.6 ms |  484 ms |   75.9 s |
|           32 |        176.6 |    1.8× |      5.7 s |   11.1 s |    135.8 ms | 177.3 ms | 2,737 ms |   69.6 s |

All 96 requests completed at every setting, and the server logs show no preemption, so KV memory was never the limit.

* **Throughput levels off.** Going from 4 to 16 adds 64%, but going from 16 to 32 adds only 9%. On this CPU the knee is around 16.
* **TTFT drops a lot.** With 4 slots, 28 of the 32 in-flight requests wait in the server's queue, so the median wait for the first token is 37 s. More slots means less queueing.
* **TPOT rises a lot.** Each token takes 4.2× longer at 32 than at 4. The CPU is limited by compute, so every extra sequence in the batch adds real work to each step. This is the part that would be much cheaper on a GPU.
* **P99 ITL spikes to 2.7 s at 32.** When new requests join the batch, their prefill runs in the same step as everyone else's decode, so running requests occasionally stall for seconds.

```
larger --max-num-seqs → more sequences per step → each step does more work → each step takes longer (TPOT goes up) → throughput stops improving once the step time grows about as fast as the batch size, because the hardware is fully busy
```

The takeaway: a small `--max-num-seqs` gives fast tokens but long queues, and a large one gives short queues but slow, jittery tokens. Throughput only improves up to the knee.

### Prefix caching speeds up prefill, not decode
We'll skip the last experiment, but the idea is -

Prefix caching makes repeated prompts start faster, but it doesn't make generation faster.

* It only speeds up the start. If many requests begin with the same text, like a system prompt, few-shot examples, or earlier turns of a chat, the server computes that part once and reuses it. That cuts TTFT. Once tokens start coming out, the speed is the same as without caching.

* The gain depends on how much is shared. A 1,000-token shared prefix with a 50-token question saves most of the prefill. A 50-token shared prefix with a 1,000-token question saves almost nothing.

* It only works while the cache holds the prefix. Cached prefixes take KV memory. With too many different prefixes, or too little memory, old ones get evicted and you're back to full prefill.

## Summary
Almost every result we've seen follows from one simple model of how the server works.

**1. The server works in steps.** At each step it runs the model once over everything in the batch: a few new tokens for each running request, plus chunks of prompts being prefilled.

**2. A step costs a fixed part plus a per-token part.**

```
step time ≈ fixed cost + per-token cost × tokens in the step
```
- **Fixed cost:** reading the model weights, which happens once per step no matter the batch size.
- **Per-token cost:** the math for each token in the batch, plus reading its KV cache.

**3. Everything you measure comes from that step time.**
- **TPOT** ≈ step time (each running request gets one token per step)
- **TTFT** ≈ time waiting in the queue + time to prefill the prompt
- **Throughput** ≈ tokens per step ÷ step time

**4. Two limits apply on top.**
- **Queueing:** if requests arrive faster than the server can handle, they wait, and TTFT grows.
- **Memory:** the KV cache caps how many requests can be in flight at once.

To reason about any knob, ask three questions:
1. Does it change **prefill** work, **decode** work, or both?
2. Does it change the **fixed** cost or the **per-token** cost?
3. Does it create a **queue** or use up **memory**?

Here's how your experiments fit:

| Experiment | What changed | Result |
|---|---|---|
| More concurrency | More tokens per step, so the fixed cost is shared | Throughput ↑, TPOT ↑ a bit, TTFT ↑ once it queues |
| Longer input | More prefill work | TTFT ↑; decode barely changes |
| Longer output | More decode steps | Total time ↑; TTFT unchanged |
| Larger max-num-seqs | Bigger batch, shorter queue | Throughput ↑ to the knee, TPOT ↑, TTFT ↓ |
| Prefix caching | Less prefill work | TTFT ↓; decode unchanged |

The CPU vs. GPU difference is just which part of the step cost dominates. On a GPU the **fixed** part dominates, so adding requests to a batch is nearly free. On your CPU the **per-token** part dominates, so each added request slows every step. That's why your max-num-seqs results looked less "free" than the usual GPU explanation.
