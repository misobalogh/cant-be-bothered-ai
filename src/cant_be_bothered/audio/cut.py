from pathlib import Path
from typing import Optional, Union
import torchaudio
from .utils import parse_time_str


def get_range_output_path(input_path: Path, start_sec: float, end_sec: float) -> Path:
    return input_path.with_name(
        f"{input_path.stem}_cut_{int(start_sec)}-{int(end_sec)}.wav"
    )


def cut_audio(
    input_path: Union[str, Path],
    start: str,
    end: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Cut an audio file between start and end times and save as WAV.
    - start, end: time strings in 'hh:mm:ss', 'mm:ss' or 'ss' (end can be None to cut to end)
    - output_path: optional output path (defaults to input_stem_cut.wav)

    Returns Path to the saved file.

    Raises
    - FileNotFoundError: if input file does not exist
    - ValueError: if start/end times are invalid
    - Any other exceptions raised by torchaudio.load or torchaudio.save
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    waveform, sr = torchaudio.load(str(input_path))

    duration_sec = waveform.shape[1] / sr

    start_sec = parse_time_str(start)

    end_sec = duration_sec if end is None else parse_time_str(end)

    if start_sec < 0 or end_sec <= start_sec:
        raise ValueError(f"Invalid start/end times: start={start_sec}, end={end_sec}")
    if start_sec >= duration_sec:
        raise ValueError(
            f"Start time {start_sec}s is beyond file duration {duration_sec}s"
        )

    # clamp end and duration
    end_sec = min(end_sec, duration_sec)

    start_sample = int(round(start_sec * sr))
    end_sample = int(round(end_sec * sr))

    cut_waveform = waveform[:, start_sample:end_sample]

    if output_path is None:
        out = get_range_output_path(input_path, start_sec, end_sec)
    else:
        out = Path(output_path)

    torchaudio.save(str(out), cut_waveform, sr)

    return out
