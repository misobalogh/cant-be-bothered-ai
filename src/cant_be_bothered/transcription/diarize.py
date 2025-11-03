import os
import dotenv

import torch
import torchaudio
import warnings

from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore")


torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

dotenv.load_dotenv()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1", token=os.getenv("HF_TOKEN")
)
pipeline.to(torch.device("cuda"))


audio = "audio1.aac"

# Load audio to memory before processing for faster processing
waveform, sample_rate = torchaudio.load(audio)

with ProgressHook() as hook:
    output = pipeline(
        {"waveform": waveform, "sample_rate": sample_rate},
        hook=hook,
        min_speakers=1,
        max_speakers=2,
    )

for turn, speaker in output.speaker_diarization:
    print(f"{speaker} speaks between t={turn.start}s and t={turn.end}s")
