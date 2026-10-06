## Подготовка окружения

```bash
nvidia-smi
```

Ожидается что-то вроде этого:
```bash
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.178.01             Driver Version: 582.78         CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce GTX 1080 Ti     On  |   00000000:0A:00.0  On |                  N/A |
| 32%   57C    P0             67W /  250W |    4094MiB /  11264MiB |      4%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

```bash
python3 -m venv ~/venv-emb
source ~/venv-emb/bin/activate
pip install -U pip
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install sentence-transformers
```


Создать скрипт бенчмарка:
```bash
sudo nano bench_embeddings.py
```

```python
#!/usr/bin/env python3
import argparse, gc, json, os, random, time

os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "10")  # до импорта HF-библиотек

import torch
from sentence_transformers import SentenceTransformer

RESULTS_FILE = "bench_results.json"

WORDS = ("quantum forge digital twin gateway chevron naquadah hyperdrive ansible kafka "
         "pipeline vector index retrieval token transformer attention embedding sparse dense "
         "quantization cache cluster shard replica latency throughput benchmark").split()


def make_chunks(n, approx_words=400, seed=42):
    rng = random.Random(seed)
    return [" ".join(rng.choices(WORDS, k=approx_words + rng.randint(-50, 50))) for _ in range(n)]


def load_model(model_id, device):
    ts = lambda: time.strftime("%H:%M:%S")
    print(f"[{ts()}] загрузка {model_id} на {device} ...", flush=True)
    model = SentenceTransformer(model_id, device=device)
    if device == "cuda":
        cc = torch.cuda.get_device_capability(0)
        if cc[0] >= 7:
            model = model.half()
        else:
            print(f"[{ts()}] compute capability {cc[0]}.{cc[1]}", flush=True)
    model.eval()
    if device == "cpu":
        torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", os.cpu_count() or 8)))
        n = torch.get_num_threads()
        print(f"[{ts()}] torch CPU threads после загрузки модели: {n}", flush=True)
        g = torch.randn(2000, 2000)
        t = time.perf_counter()
        for _ in range(3):
            g = g @ g
        print(f"[{ts()}] preflight GEMM (3x2000^3): {time.perf_counter()-t:.2f}s", flush=True)
    return model


def cleanup_model(model, device):
    del model
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()


def append_result(res):
    results = []
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, encoding="utf-8") as f:
                results = json.load(f)
        except json.JSONDecodeError:
            pass
    results.append(res)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def bench(model, model_id, device, chunks, batch_size):
    ts = lambda: time.strftime("%H:%M:%S")
    sync = (lambda: torch.cuda.synchronize()) if device == "cuda" else (lambda: None)

    print(f"[{ts()}] warmup ({batch_size} чанков)...", flush=True)
    model.encode(chunks[:batch_size], batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
    sync()

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    print(f"[{ts()}] кодирование {len(chunks)} чанков, batch={batch_size} ...", flush=True)
    t0 = time.perf_counter()
    embs = model.encode(chunks, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
    sync()
    dt = time.perf_counter() - t0

    res = {
        "model": model_id, "device": device, "batch": batch_size,
        "chunks": len(chunks), "dims": int(embs.shape[1]),
        "seconds": round(dt, 1), "chunks_per_s": round(len(chunks) / dt, 1),
        "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2) if device == "cuda" else None,
    }
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res, embs


def bench_search(embs, n_queries=100, k=5):
    try:
        import faiss
    except ImportError:
        print("faiss-cpu не установлен — поисковый бенчмарк пропущен", flush=True)
        return {}
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    t0 = time.perf_counter()
    index.add(embs)
    add_dt = time.perf_counter() - t0
    q = embs[:n_queries]
    index.search(q, k)
    t0 = time.perf_counter()
    index.search(q, k)
    search_dt = time.perf_counter() - t0
    return {
        "faiss_add_s": round(add_dt, 3),
        "faiss_add_est_100k_s": round(add_dt * (100000 / len(embs)), 1),
        "faiss_search_ms": round(search_dt / n_queries * 1000, 3),
    }


def bench_query_latency(model, chunks, n=30):
    texts = chunks[:n]
    model.encode(texts[:4], batch_size=1, show_progress_bar=False, normalize_embeddings=True)
    t0 = time.perf_counter()
    for txt in texts:
        model.encode([txt], batch_size=1, show_progress_bar=False, normalize_embeddings=True)
    dt = time.perf_counter() - t0
    return {"query_embed_ms": round(dt / n * 1000, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["Qwen/Qwen3-Embedding-0.6B"])
    ap.add_argument("--device", choices=["cpu", "cuda", "both"], default="cuda")
    ap.add_argument("--chunks", type=int, default=5000)
    ap.add_argument("--batch", type=int, default=None, help="по умолчанию: 128 на CPU, 32 на CUDA")
    ap.add_argument("--compare-batches", action="store_true", help="прогнать batch 8/32/128 на GPU")
    args = ap.parse_args()

    devices = ["cpu", "cuda"] if args.device == "both" else [args.device]
    if torch.cuda.is_available() and "cuda" in devices:
        print(torch.cuda.get_device_name(0), flush=True)
    chunks = make_chunks(args.chunks)

    for mid in args.models:
        for dev in devices:
            if dev == "cuda" and not torch.cuda.is_available():
                print("CUDA недоступна, пропуск", flush=True)
                continue
            default_bs = args.batch or (128 if dev == "cpu" else 32)
            batches = [8, 32, 128] if (args.compare_batches and dev == "cuda") else [default_bs]
            try:
                model = load_model(mid, dev)
            except Exception as e:
                print(f"ОШИБКА загрузки {mid}: {e}", flush=True)
                continue
            try:
                for bs in batches:
                    try:
                        res, embs = bench(model, mid, dev, chunks, bs)
                        res.update(bench_search(embs))
                        append_result(res)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache()
                        err = {"model": mid, "device": dev, "batch": bs, "error": "CUDA OOM"}
                        print(json.dumps(err, ensure_ascii=False), flush=True)
                        append_result(err)
                    except Exception as e:
                        err = {"model": mid, "device": dev, "batch": bs, "error": str(e)[:200]}
                        print(json.dumps(err, ensure_ascii=False), flush=True)
                        append_result(err)
                try:
                    qres = {"model": mid, "device": dev}
                    qres.update(bench_query_latency(model, chunks))
                    append_result(qres)
                except Exception as e:
                    print(f"query-latency пропущен: {e}", flush=True)
            finally:
                cleanup_model(model, dev)


if __name__ == "__main__":
    main()
```

Запустить бенчмарк

```bash
python bench_embeddings.py --device both --models Qwen/Qwen3-Embedding-0.6B Qwen/Qwen3-Embedding-4B --compare-batches
```

Я проверял на:
```bash
OMP_NUM_THREADS=7 python bench_embeddings.py --device cuda --models Qwen/Qwen3-Embedding-0.6B --compare-batches
```
```bash
OMP_NUM_THREADS=7 python bench_embeddings.py --device cpu  --models Qwen/Qwen3-Embedding-0.6B --batch 32 --chunks 500
```

И сравнил с BGE-M3
```bash
OMP_NUM_THREADS=7 python bench_embeddings.py --device cuda --models BAAI/bge-m3 --batch 32 --chunks 2000
```

Результаты дописываются в `bench_results.json` после каждой конфигурации после каждого прогона, OOM не приводит к потере предыдущих результатов.
Модели можно сравнивать между собой только при одинаковых chunks/batch/device.

Интересующие поля:
- `seconds`, `chunks_per_s` - время и скорость кодирования
- `peak_vram_gb` - пик потребления VRAM при кодировании позволяет примерно оценить необходимую видеопамять или размер batch
`faiss_add_s` - время добавления N векторов в FAISS
`faiss_search_ms` - среднее время поиска top-5