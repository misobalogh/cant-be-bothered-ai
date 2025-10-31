# cant-be-bothered-ai

Sooo, I had to write meeting minutes once. Got bored after first half, so I made this tool to automate this task using Whisper and Gemini AI.
No more writing boring minutes! From now on, just record the meeting and let the AI do the work.

## Quick Start

### 1. Install dependencies

```bash
git clone git@github.com:misobalogh/cant-be-bothered-ai.git
cd cant-be-bothered-ai
uv sync
```

### 2. Setup Gemini API Key (for summarization)

1. Get free API key: https://aistudio.google.com/app/apikey
2. Create `.env` file and add your key:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Transcribe audio

```bash
# Basic transcription only
uv run transcribe meeting.mp3

# With AI-generated meeting minutes
uv run transcribe meeting.mp3 --summarize

# Simple bullet-point summary
uv run transcribe meeting.mp3 --summarize --simple
```

---

## Usage

### Basic transcription (no AI)

```bash
uv run transcribe meeting.wav
# Output: output/meeting.txt (raw transcript)
```

### Generate meeting minutes with Gemini

```bash
uv run transcribe meeting.mp3 --summarize
# Output: output/meeting.md (formatted minutes)
```

### Simple summary

```bash
uv run transcribe meeting.mp3 -s --simple
# Output: output/meeting.md (bullet points)
```

### Custom output file

```bash
uv run transcribe meeting.mp3 -o my_notes.txt
uv run transcribe meeting.mp3 --summarize -o minutes.md
```

### Use different Whisper model

```bash
# Faster but less accurate
uv run transcribe audio.mp3 -m base

# Best quality (recommended for Slovak)
uv run transcribe audio.mp3 -m large-v3 --summarize
```

### Available Whisper models:
- `tiny`
- `base`
- `small`
- `medium`
- `large-v3` - **best quality for Slovak** (~8 VRAM)

---

## Requirements

- Python 3.12+
- NVIDIA GPU with CUDA (8GB VRAM recommended)
- Gemini API key (free tier available)
- Windows/Linux/macOS

---

##  Architecture

```
Audio Input → Whisper STT → [Optional: Gemini AI] → Text/Markdown Output
```

```
┌─────────────────┐
│  Audio Input    │ (mp3/wav)
└────────┬────────┘
         │
    ┌────▼─────────────────────────┐
    │  Audio Preprocessing         │
    │  (normalization, conversion) │
    └────┬─────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │  Parallel Processing:         │
    │  ┌─────────────┬─────────────┐│
    │  │ STT Module  │ Diarization ││
    │  │  (Whisper)  │  (Pyannote) ││
    │  └──────┬──────┴──────┬──────┘│
    └─────────┼─────────────┼───────┘
              │             │
    ┌─────────▼─────────────▼───────┐
    │  Alignment & Merging Module   │
    │  (merging timestamps)         │
    └─────────┬─────────────────────┘
              │
    ┌─────────▼─────────────────────┐
    │  Structured Transcript        │
    │  (speaker + text + time)      │
    └─────────┬─────────────────────┘
              │
    ┌─────────▼─────────────────────┐
    │  LLM Processing Module        │
    │  (Gemini API)                 │
    └─────────┬─────────────────────┘
              │
    ┌─────────▼─────────────────────┐
    │  Output Formatter             │
    │  (markdown/docx export)       │
    └───────────────────────────────┘
```

---

## Roadmap

- [x] Basic Whisper transcription
- [x] Gemini AI meeting minutes generation
- [x] Markdown export
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Speaker diarization (Pyannote)
- [ ] Speaker name mapping
- [ ] Timestamp preservation
- [ ] Nice CLI interface
- [ ] Specific to our use case - output the minutes to our page repository and publish automatically

---

## Troubleshooting

### Universal fix
If you encounter errors related to something else then dependencies, try to use CPU only mode:
```bash
uv run transcribe audio.mp3 --device cpu --summarize
```

### CuDNN errors
If you see `cudnn_ops64_9.dll` errors:
```bash
uv pip install nvidia-cudnn-cu12
```
If that doesnt work, try installing it manually from:
https://developer.nvidia.com/cudnn-downloads

Then, add the `bin` folder to your `PATH` environment variable.
(Probably just ask ChatGPT for help with this one if its your first time xD)

### Out of memory
Use smaller Whisper model:
```bash
uv run transcribe audio.mp3 -m base --summarize
```

### Gemini API errors
Make sure your `.env` file contains valid API key:
```bash
GEMINI_API_KEY=AIza...
```

---

**Status:**

MVP v3 - Transcription + AI Minutes + Markdown export
