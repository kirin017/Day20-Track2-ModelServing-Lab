# Reflection — Lab 20 (Personal Report)

> **Đây là báo cáo cá nhân.** Mỗi học viên chạy lab trên laptop của mình, với spec của mình. Số liệu của bạn không so sánh được với bạn cùng lớp — chỉ so sánh **before vs after trên chính máy bạn**. Grade rubric tính theo độ rõ ràng của setup + tuning của bạn, không phải tốc độ tuyệt đối.

---

**Họ Tên:** Nguyễn Hữu Huy
**Cohort:** _A20-K1_
**Ngày submit:** _2026-05-06_

---

## 1. Hardware spec (từ `00-setup/detect-hardware.py`)

> Paste output của `python 00-setup/detect-hardware.py` vào đây, hoặc điền thủ công:

- **OS:** Windows 11
- **CPU:** AMD Ryzen 5 5600H
- **Cores:** 6 physical / 12 logical
- **CPU extensions:** AVX2
- **RAM:** 15.4 GB
- **Accelerator:** CPU only
- **llama.cpp backend đã chọn:** CPU
- **Recommended model tier:** TinyLlama-1.1B (Q4_K_M)

**Setup story** (≤ 80 chữ): những gì cần thay đổi để lab chạy được trên máy bạn (vd: dùng WSL2, install CUDA Toolkit, fall back sang Vulkan vì ROCm phiên bản kén, tắt antivirus để pip install nhanh hơn, v.v.):

Lab chạy trên môi trường Windows native với CPU only. Không cần cài thêm CUDA hay toolkit đồ họa nào, tiến trình cài đặt cực kỳ gọn nhẹ và chạy trơn tru với các file pre-built của llama.cpp.

---

## 2. Track 01 — Quickstart numbers (từ `benchmarks/01-quickstart-results.md`)

> Paste bảng từ `benchmarks/01-quickstart-results.md` xuống đây (auto-generated bởi `python 01-llama-cpp-quickstart/benchmark.py`).

| Model | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode rate (tok/s) |
|---|--:|--:|--:|--:|--:|
| TinyLlama (Q4_K_M) | 590 | 103 / 152 | 20.9 / 21.8 | 1436 / 1492 / 1502 | 47.8 |
| TinyLlama (Q2_K) | 623 | 118 / 142 | 22.1 / 22.9 | 1509 / 1557 / 1565 | 45.3 |

**Một quan sát** (≤ 50 chữ): Q4_K_M vs Q2_K trên máy bạn — số liệu nói gì? Quality đáng đánh đổi không?

Chạy trên CPU với llama.cpp build sẵn, Q4_K_M chạy rất nhanh với tốc độ 47.8 tok/s, E2E ~1.4s. Do cấu hình CPU và mô hình nhỏ nên sự chênh lệch giữa Q4 và Q2 không quá lớn, thậm chí Q4 còn load và phản hồi mượt hơn. Hoàn toàn đáng để dùng Q4.

---

## 3. Track 02 — llama-server load test

> Chạy 2 lần locust ở concurrency 10 và 50, paste tóm tắt bên dưới.

| Concurrency | Total RPS | TTFB P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|--:|--:|--:|--:|--:|--:|
| 10 | 1.2 | 2500 | 15000 | 18000 | 0 |
| 50 | 0.46 | 3830 | 37631 | 38000 | 0 |

**KV-cache observation** (từ `record-metrics.py`): peak `llamacpp:kv_cache_usage_ratio` ở concurrency 50 = 0.92, nghĩa là CPU phải xử lý quá nhiều context cùng lúc gây ra hiện tượng bottleneck trầm trọng ở RAM bandwidth.

---

## 4. Track 03 — Milestone integration

- **N16 (Cloud/IaC):** stub: localhost only
- **N17 (Data pipeline):** stub: in-memory dict
- **N18 (Lakehouse):** stub: SQLite
- **N19 (Vector + Feature Store):** stub: TOY_DOCS

**Nơi tốn nhiều ms nhất** trong pipeline (đo bằng `time.perf_counter` trong `pipeline.py`):

- embed: 0.5 ms
- retrieve: 0.5 ms
- llama-server: 3500 ms

**Reflection** (≤ 60 chữ): bottleneck nằm ở đâu? Có khớp với kỳ vọng không?

Bottleneck rõ ràng nằm ở khâu llama-server (3.5 giây). Vì dùng CPU để chạy LLM nên thời gian suy luận chậm hơn rất nhiều so với retrieve hay embed. Điều này hoàn toàn đúng với tính toán.

---

## 5. Bonus — The single change that mattered most

> **Most important section.** Pick **một** thay đổi từ bonus track (build flag, thread sweep, quant pick, GPU offload, KV-cache quantization, speculative decoding, bất cứ challenge nào trong `BONUS-llama-cpp-optimization/CHALLENGES.md`) đã tạo ra speedup lớn nhất trên máy bạn.

**Change:** hạ `-t` từ 12 xuống 6 (Thread sweep)

**Before vs after** (paste 2-3 dòng từ sweep output):

```
before (12 threads): 40.2 tok/s
after  (6 threads):  53.3 tok/s
speedup: ~1.32×
```

**Tại sao nó work** (1–2 đoạn ngắn — đây là phần grader đọc kỹ nhất):

CPU AMD Ryzen 5 5600H có 6 nhân thực (physical) và 12 luồng logic (logical). Text generation của LLM chủ yếu bị giới hạn bởi memory bandwidth chứ không phải compute. Khi dùng 12 threads (vượt qua số nhân thực), các luồng tranh chấp nhau tài nguyên bộ nhớ cache L3 và băng thông RAM, gây ra "thrashing". Hạ xuống đúng 6 nhân thực giúp tối ưu hóa luồng dữ liệu vào CPU, qua đó tăng tốc đáng kể so với việc dùng toàn bộ số luồng ảo.

---

## 6. (Optional) Điều ngạc nhiên nhất

_(1–2 câu — không bắt buộc, nhưng người grader đọc tất cả)_

_Bất ngờ nhất là việc giảm số luồng (thread) từ 12 xuống 6 lại làm mô hình chạy nhanh hơn hẳn, thay vì nghĩ rằng "càng nhiều luồng càng tốt" như các tác vụ thông thường._

---

## 7. Self-graded checklist

- [x] `hardware.json` đã commit
- [x] `models/active.json` đã commit (hoặc paste path snapshot vào section 1)
- [x] `benchmarks/01-quickstart-results.md` đã commit
- [x] `benchmarks/02-server-results.md` (hoặc CSV từ `record-metrics.py`) đã commit
- [x] `benchmarks/bonus-*.md` đã commit (ít nhất 1 sweep)
- [x] Ít nhất 6 screenshots trong `submission/screenshots/` (xem `submission/screenshots/README.md`)
- [x] `make verify` exit 0 (chạy ngay trước khi push)
- [x] Repo trên GitHub ở chế độ **public**
- [x] Đã paste public repo URL vào VinUni LMS

---

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Nếu private, grader không xem được → 0 điểm.
