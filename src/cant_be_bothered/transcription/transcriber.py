from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console

console = Console()


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str = "sk",
    device: str = "cuda",
    compute_type: str = "float16",
    output_file: Optional[Path] = Path("output/transcript.txt"),
) -> str:
    # Load model (will download on first run)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Loading Whisper model...", total=None)

        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type if device in ["cuda", "auto"] else "int8",
        )

        progress.remove_task(task)
        console.print(":white_check_mark: [green]Whisper model loaded![/green]")

    # Transcribe
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,  # Voice activity detection - removes silence
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    transcript_parts = []

    # Create file where the transcript will be saved incrementally by each segment
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Calculate approximate total segments based on audio duration
    # This is an estimate since segments are generated dynamically
    estimated_duration = info.duration
    estimated_segments = int(estimated_duration / 5)  # Rough estimate: ~5 seconds per segment

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "[cyan]Transcribing audio...",
            total=estimated_segments if estimated_segments > 0 else 100
        )

        with open(output_file, "w", encoding="utf-8") as f:
            segment_count = 0
            for segment in segments:
                text = segment.text.strip()
                transcript_parts.append(text)
                # Write to file immediately, so that if the process is interrupted, we still have partial results
                f.write(text + " ")
                f.flush()

                segment_count += 1
                progress.update(task, advance=1)

        progress.update(task, completed=progress.tasks[task].total)

    console.print(":white_check_mark: [green]Transcription complete![/green]")

    full_transcript = " ".join(transcript_parts)

    return full_transcript
