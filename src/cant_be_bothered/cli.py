from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from cant_be_bothered.summarization.gemini_client import GeminiClient

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

from cant_be_bothered.transcription.transcriber import transcribe_audio  # noqa: E402


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
    console.print(f"[bold blue]Transcribing:[/bold blue] {audio_file.name}")
    console.print(
        f"[dim]Model: {model} | Language: {language} | Device: {device}[/dim] \n"
    )

    try:
        # Transcribe audio (progress bar is handled inside transcribe_audio)
        transcript = transcribe_audio(
            audio_path=audio_file,
            model_size=model,
            language=language,
            device=device,
        )

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
                console.print("Get your free API key at: https://aistudio.google.com/api-keys")
                raise typer.Exit(code=1)
            except Exception as e:
                fail(f"Gemini API error: {e}")
                raise typer.Exit(code=1)

    except Exception as e:
        fail(str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
