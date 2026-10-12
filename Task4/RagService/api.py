import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag.config import SETTINGS
from rag.pipeline import RagPipeline
from rag.stt import SpeechTranscriber
from rag.voice import VoiceSynthesizer


class AskRequest(BaseModel):
    question: str
    voice: bool = False


class AskResponse(BaseModel):
    answer: str
    internal_query: str
    internal_answer: str
    dist_top1: float
    sources: list[dict]
    audio_url: str | None = None


pipeline: RagPipeline = None
stt: SpeechTranscriber | None = None
tts: VoiceSynthesizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, stt, tts
    pipeline = RagPipeline(SETTINGS)
    stt = SpeechTranscriber(os.getenv("RAG_STT_MODEL", "base"), device=SETTINGS.device) \
        if os.getenv("RAG_STT_ENABLE", "false").lower() == "true" else None
    tts = VoiceSynthesizer(engine=SETTINGS.tts_engine, piper_model=os.getenv("RAG_PIPER_MODEL"),
                           silero_speaker=os.getenv("RAG_SILERO_SPEAKER", "aidar"))
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "tts": SETTINGS.tts_engine,
            "stt": stt is not None}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    r = pipeline.answer(req.question)
    audio_url = None
    if req.voice:
        ogg = tts.synthesize(r["answer"])
        if ogg:
            audio_url = f"/audio/{Path(ogg).name}"
            Path("static").mkdir(exist_ok=True)
    return AskResponse(**r, audio_url=audio_url)


@app.post("/ask/audio")
async def ask_audio(file: UploadFile = File(...)):
    if stt is None:
        return {"error": "STT disabled"}, 400
    tmp = Path("tmp") / file.filename
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_bytes(await file.read())
    question = stt.transcribe(str(tmp))
    return pipeline.answer(question)

@app.get("/audio/reply.ogg")
def get_audio():
    return FileResponse("audio/reply.ogg", media_type="audio/ogg")