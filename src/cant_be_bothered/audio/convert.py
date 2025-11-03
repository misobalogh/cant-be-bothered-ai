from pathlib import Path
from typing import Optional, Union

import torchaudio
import torchaudio.transforms as T


def convert_to_wav(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sample_rate: Optional[int] = None,
    mono: bool = True,
) -> Path:
    """
    Convert an audio file to WAV using torchaudio. Returns the Path to the WAV file.

    - input_path: source audio file
    - output_path: destination .wav path (defaults to input with .wav suffix)
    - sample_rate: if set, resample to this rate (e.g. 16000)
    - mono: if True, force single channel
    - force: if True, convert even if input already .wav

    Returns Path to the converted WAV file.

    Raises
    - FileNotFoundError: if input file does not exist
    - RuntimeError: if torchaudio fails to read or write files
    - Any other exceptions raised by torchaudio.load, torchaudio.save or T.Resample
    """
    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(f"Input not found: {inp}")

    out = Path(output_path) if output_path is not None else inp.with_suffix(".wav")

    waveform, sr = torchaudio.load(str(inp))  # channels_first: (channels, samples)

    # convert to mono if requested
    if mono and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # resample if requested and different sample rates
    target_sr = sr
    if sample_rate is not None and sample_rate != sr:
        resampler = T.Resample(orig_freq=sr, new_freq=sample_rate)
        waveform = resampler(waveform)
        target_sr = sample_rate

    torchaudio.save(str(out), waveform, target_sr)

    return out
