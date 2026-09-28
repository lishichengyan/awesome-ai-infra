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

## Benchmark
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
--max-concurrency 1, 2, 4, 8, 16
--random-input-len 128, 512, 1024
--random-output-len 32, 128, 512
Restart the server with --max-num-seqs 4 vs 16
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