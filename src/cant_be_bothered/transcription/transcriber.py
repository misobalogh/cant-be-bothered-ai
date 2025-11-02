from pathlib import Path

from faster_whisper import WhisperModel


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str = "sk",
    device: str = "cuda",
    compute_type: str = "float16",
) -> str:
    # Load model (will download on first run)
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type if device in ["cuda", "auto"] else "int8",
    )

    # Transcribe
    segments, _ = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,  # Voice activity detection - removes silence
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    # Combine all segments into full text
    full_transcript = " ".join(segment.text.strip() for segment in segments)

    return full_transcript
