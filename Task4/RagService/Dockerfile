FROM python:3.12-slim

WORKDIR /app
ENV RAG_DEVICE=cuda \
    RAG_DTYPE_EMBED=float32 \
    RAG_DTYPE_LLM=float16 \
    HF_HOME=/app/.hf-cache \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PIP_TIMEOUT=240 \
    PIP_RETRIES=10

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install torch==2.14.1 torchaudio==2.11.0  --index-url https://download.pytorch.org/whl/cu126
COPY Task4/RagService/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY terms_map.json ./
COPY knowledge_base/ ./knowledge_base/
COPY index/ ./index/
COPY Task4/RagService/ ./

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]