import os
from pathlib import Path
from typing import Optional

import dotenv
import torch
import torchaudio
import warnings

from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore")

console = Console()


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str = "sk",
    device: str = "cuda",
    compute_type: str = "float16",
    output_file: Optional[Path] = Path("output/transcript.txt"),
    enable_diarization: bool = False,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
) -> str:
    # Load model (will download on first run)
    device = (
        device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Loading Whisper model...", total=None)

        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type if device == "cuda" else "int8",
        )

        progress.remove_task(task)
        console.print(":white_check_mark: [green]Whisper model loaded![/green]")

    diarization_output = None
    if enable_diarization:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Loading diarization model...", total=None)
            dotenv.load_dotenv()

            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1", token=os.getenv("HF_TOKEN")
            )
            diarization_pipeline.to(torch.device(device))

            progress.remove_task(task)
            console.print(":white_check_mark: [green]Diarization model loaded![/green]")

        console.print("[cyan]Performing speaker diarization...[/cyan]")
        waveform, sample_rate = torchaudio.load(audio_path)
        diarization_params = {"waveform": waveform, "sample_rate": sample_rate}
        kwargs = {}
        if min_speakers is not None:
            kwargs["min_speakers"] = min_speakers
        if max_speakers is not None:
            kwargs["max_speakers"] = max_speakers

        with ProgressHook() as hook:
            diarization_output = diarization_pipeline(
                diarization_params,
                hook=hook,
                **kwargs,
            )

        console.print(":white_check_mark: [green]Diarization complete![/green]")

    # Transcribe
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,  # Voice activity detection - removes silence
        vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=False,  # Enable word timestamps for better speaker alignment
    )

    transcript_parts = []

    # Create file where the transcript will be saved incrementally by each segment
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Calculate approximate total segments based on audio duration
    # This is an estimate since segments are generated dynamically
    estimated_duration = info.duration
    ESTIMATE_SEGMENT_LENGTH = 5  # Rough estimate: ~5 seconds per segment
    estimated_segments = int(estimated_duration / ESTIMATE_SEGMENT_LENGTH)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "[cyan]Transcribing audio...",
            total=estimated_segments if estimated_segments > 0 else 100,
        )

        with open(output_file, "w", encoding="utf-8") as f:
            current_speaker = None
            speaker = None

            for segment in segments:
                text = segment.text.strip()

                # Determine speaker for the segment if diarization is enabled
                if enable_diarization and diarization_output:
                    segment_midpoint = (segment.start + segment.end) / 2.0
                    for turn, turn_speaker in diarization_output.speaker_diarization:
                        if turn.start <= segment_midpoint <= turn.end:
                            speaker = turn_speaker
                            break

                # If speaker changed, add a new speaker label
                if enable_diarization and speaker != current_speaker:
                    current_speaker = speaker
                    speaker_label = format_speaker_label(
                        current_speaker, template="\n\n[{}]\n"
                    )
                    f.write(speaker_label)
                    transcript_parts.append(speaker_label)

                transcript_parts.append(text)
                f.write(text + " ")

                # Write to file immediately, so that if the process is interrupted, we still have partial results
                f.flush()

                progress.update(task, advance=1)

        progress.update(task, completed=progress.tasks[task].total)

    console.print(":white_check_mark: [green]Transcription complete![/green]")

    full_transcript = "".join(transcript_parts)

    return full_transcript


def format_speaker_label(speaker_id: str, template: str = "\n\n[{}]\n") -> str:
    """Format speaker label for transcript.

    This function is here for future, because different LLMs might work better with different speaker label formats.
    For example, some studies show that using Markdown format might improve model performance.
    """
    return template.format(speaker_id)
