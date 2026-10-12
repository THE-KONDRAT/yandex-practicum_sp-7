from faster_whisper import WhisperModel


class SpeechTranscriber:
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        self.model = WhisperModel(model_size, device=device,
                                  compute_type="float16" if device == "cuda" else "int8")

    def transcribe(self, audio_path: str, language: str | None = None) -> str:
        segments, _ = self.model.transcribe(audio_path, language=language)
        return " ".join(seg.text for seg in segments).strip()