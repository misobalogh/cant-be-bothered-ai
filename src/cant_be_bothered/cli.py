from pathlib import Path
from typing import Optional

import tempfile

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from cant_be_bothered.summarization.gemini_client import GeminiClient
from cant_be_bothered.transcription.transcriber import transcribe_audio
from cant_be_bothered.audio.convert import convert_to_wav
from cant_be_bothered.audio.cut import cut_audio_segment

app = typer.Typer(
    name="transcribe",
    help="Transcribe audio files to text using Whisper",
    add_completion=False,
)
console = Console()


def fail(message: str) -> None:
    console.print(f":x: [bold red]Error:[/bold red] {message}")


def success(message: str) -> None:
    console.print(f":white_check_mark: [bold green]Success:[/bold green] {message}")


@app.command()
def main(
    audio_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to audio file (mp3, wav, m4a, etc.)",
    ),
    cut_start: Optional[str] = typer.Option(
        None,
        "--start",
        help="Start time to cut audio (format: hh:mm:ss|mm:ss|ss)",
    ),
    cut_end: Optional[str] = typer.Option(
        None,
        "--end",
        help="End time to cut audio (format: hh:mm:ss|mm:ss|ss)",
    ),
    no_cleanup: bool = typer.Option(
        False,
        "--no-cleanup",
        help="Do not delete temporary files after processing (default: cleanup enabled)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: same name as input with .txt/.md extension)",
    ),
    model: str = typer.Option(
        "large-v3",
        "--model",
        "-m",
        help="Whisper model size: tiny, base, small, medium, large-v3",
    ),
    device: str = typer.Option(
        "auto",
        "--device",
        "-d",
        help="Device to use for transcription: auto, cpu, cuda",
    ),
    language: str = typer.Option(
        "sk",
        "--language",
        "-l",
        help="Language code (sk for Slovak)",
    ),
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Generate formatted meeting minutes using Gemini AI",
    ),
    simple: bool = typer.Option(
        False,
        "--simple",
        help="Generate simple bullet-point summary (instead of full minutes)",
    ),
) -> None:
    console.print("[bold green]Cant Be Bothered AI - Transcription CLI[/bold green]\n")
    console.print(f"[dim]Input file: {audio_file}[/dim]")

    tmp_context = None
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Preparing audio file...", total=None)

            #######################################################
            # Setup temporary working directory
            #######################################################
            if no_cleanup:
                work_dir = Path(tempfile.mkdtemp(prefix="cbb_"))
                console.print(f"[dim]Temporary files are stored in: {work_dir}[/dim]")
            else:
                tmp_context = tempfile.TemporaryDirectory(prefix="cbb_")
                work_dir = Path(tmp_context.name)

            working_file = Path(audio_file)

            #######################################################
            # Cut audio segment if specified
            #######################################################
            if cut_start or cut_end:
                console.print(
                    f"[dim]Cutting audio segment: start={cut_start or '0:00'} end={cut_end or 'end'}[/dim]"
                )

                out_cut = work_dir / f"cut_{working_file.stem}.wav"

                cut_audio_segment(
                    input_path=audio_file,
                    output_path=out_cut,
                    start=cut_start,
                    end=cut_end,
                )
                working_file = out_cut

            #######################################################
            # Convert to WAV
            #######################################################
            if working_file.suffix.lower() != ".wav":
                console.print("[dim]Converting to WAV format...[/dim]")

                out_wav = work_dir / f"{working_file.stem}.wav"

                convert_to_wav(
                    input_path=working_file,
                    output_path=out_wav,
                )

                working_file = out_wav
            else:
                console.print(
                    "[dim]Audio already in WAV format, skipping conversion[/dim]"
                )

            progress.update(task, description="Audio file ready.")

        console.print(f"[bold blue]Transcribing:[/bold blue] {working_file.name}")
        console.print(
            f"[dim]Model: {model} | Language: {language} | Device: {device}[/dim] \n"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Transcribing audio...", total=None)

            transcript = transcribe_audio(
                audio_path=working_file,
                model_size=model,
                language=language,
                device=device,
            )

            progress.update(task, description="Transcription complete!")

        if output is None:
            # Default output directory
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Determine output file extension based on summarization
            if summarize:
                output = output_dir / audio_file.with_suffix(".md").name
            else:
                output = output_dir / audio_file.with_suffix(".txt").name

        # Save raw transcript
        if not summarize:
            output.write_text(transcript, encoding="utf-8")
            success(f"Saved to: {output}")
            console.print(f"[dim]Saved to: {output}[/dim]\n")
            console.print("[bold]Transcript:[/bold]")
            console.print(f"[cyan]{transcript}[/cyan]")
        else:
            # Generate meeting minutes with Gemini
            console.print("\n[bold blue]Generating meeting minutes...[/bold blue]")

            try:
                gemini_client = GeminiClient()

                token_count = gemini_client.count_tokens(transcript)
                console.print(f"[dim]Transcript tokens: {token_count:,}[/dim]")

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Processing with Gemini AI...", total=None)

                    if simple:
                        summary = gemini_client.generate_simple_summary(transcript)
                    else:
                        summary = gemini_client.generate_meeting_minutes(transcript)

                    progress.update(task, description="Minutes generated!")

                # Save markdown output
                output.write_text(summary, encoding="utf-8")

                success(f"Meeting minutes saved to: {output}")
                console.print()

                # Display formatted markdown
                md = Markdown(summary)
                console.print(md)

            except ValueError as e:
                fail(f"{e}\n\nSet GEMINI_API_KEY in .env file or environment variable.")
                fail("Get your free API key at: https://aistudio.google.com/api-keys")
                raise typer.Exit(code=1)
            except Exception as e:
                fail(f"Gemini API error: {e}")
                raise typer.Exit(code=1)

    except Exception as e:
        fail(str(e))
        raise typer.Exit(code=1)

    finally:
        if tmp_context is not None:
            tmp_context.cleanup()


if __name__ == "__main__":
    app()
