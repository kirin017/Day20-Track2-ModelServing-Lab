# Track 02 — llama-server load test

| Concurrency | Total RPS | TTFB P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|--:|--:|--:|--:|--:|--:|
| 10 | 1.2 | 2500 | 15000 | 18000 | 0 |
| 50 | 0.46 | 3830 | 37631 | 38000 | 0 |

**KV-cache observation** (từ `record-metrics.py`): peak `llamacpp:kv_cache_usage_ratio` ở concurrency 50 = 0.92, nghĩa là CPU phải xử lý quá nhiều context cùng lúc gây ra hiện tượng bottleneck trầm trọng ở RAM bandwidth.
