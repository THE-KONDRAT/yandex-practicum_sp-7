1. Установить зависимости
```shell
pip install langchain-text-splitters sentence-transformers chromadb
pip uninstall torch -y
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu126
```
Возможные проблемы:
```shell
Looking in indexes: https://download.pytorch.org/whl/cu126
ERROR: Could not find a version that satisfies the requirement torch (from versions: none)
ERROR: No matching distribution found for torch
```
надо пересоздать venv на python 3.12


2. Создать индексы
```shell
python Task3\build_index.py
```
Ожидается примерно такой вывод:
```shell
python Task3\build_index.py
• STAGE 1 • Chunk generation started. Documents 40
• STAGE 1 • Chunk generation finished. Chunks: 3908 Elapsed: 0.1 s (41310 chunks/s).
Total elapsed: 0.1 s
FP32 data type was selected manually
... (Loading weights: 100% etc.)
• STAGE 2 • Embeddings generation started. Chunks: [3908] Model: [Qwen/Qwen3-Embedding-0.6B] Device: cuda, dtype: float32 Batch: [32]
Batches: 100%|███████████████████████████████████████████████████████████████████████| 123/123 [00:58<00:00,  2.10it/s]
• STAGE 2 • Embeddings generation ended. Embeddings: 3908 x 1024 Elapsed: 58.7 s (66.6 chunks/s).
Total elapsed: 67.7 s
• STAGE 3 • Index creation started.
• STAGE 3 • Index creation finished. Saved to index\chroma_db/ Collection: [knowledge_base] Chunks: [3908]Elapsed: 6.7 s
Total elapsed: 74.5 s
```

3. Проверить поиск по индексам