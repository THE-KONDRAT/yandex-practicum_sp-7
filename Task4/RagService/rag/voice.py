from pathlib import Path
import subprocess
import torchaudio

class VoiceSynthesizer:
    # available silero voices: aidar, baya, kseniya, xenia, eugene
    def __init__(self, engine: str = "none", piper_model: str | None = None, silero_speaker: str = "baiya"):
        if engine not in ("none", "piper", "silero"):
            raise ValueError(f"unknown tts engine: {engine}")
        self.engine = engine
        self.piper_model = piper_model
        self.silero_speaker = silero_speaker
        self._silero = None

    def synthesize(self, text: str, out_dir: str = "audio") -> str | None:
        if self.engine == "none":
            return None
        Path(out_dir).mkdir(exist_ok=True)
        wav = str(Path(out_dir) / "reply.wav")
        ogg = str(Path(out_dir) / "reply.ogg")

        if self.engine == "piper":
            if not self.piper_model:
                raise RuntimeError("piper: .onnx-model path was not specified (RAG_PIPER_MODEL)")
            subprocess.run(["piper", "--model", self.piper_model,
                            "--output_file", wav], input=text, text=True, check=True)
        else:
            if self._silero is None:
                import torch
                self._silero, _ = torch.hub.load(repo_or_dir="snakers4/silero-models", model="silero_tts",
                    #language="ru", speaker="v5_cis_base")
                    language="ru", speaker="v5_1_ru")
            audio = self._silero.apply_tts(text=text, speaker=self.silero_speaker, sample_rate=48000)
            import torch
            torchaudio.save(wav, audio.unsqueeze(0), 48000)

        subprocess.run(["ffmpeg", "-y", "-i", wav, "-c:a", "libopus", ogg], check=True)
        return ogg