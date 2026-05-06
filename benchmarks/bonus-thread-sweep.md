# Bonus — Thread sweep

Model: `tinyllama-1.1b-chat-v0.3.Q4_K_S.gguf`  ·  GPU layers: `0`

| threads | tg64 (tok/s) |
|---:|---:|
| 1 | 27.7 |
| 2 | 42.7 |
| 3 | 49.9 |
| 6 | 53.3 |
| 12 | 40.2 |
| 24 | 29.6 |

**Best**: `-t 6` at 53.3 tok/s.

Look at the curve. If it peaks around your **physical** core count and drops as you go higher, that's the memory-bandwidth ceiling: extra threads fight over the same memory channels and slow each other down.
