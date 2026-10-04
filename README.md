# Lecture Voice-to-Notes: Local AI Study Workspace

A local-first Streamlit app that turns lecture material into a complete study workspace: notes, transcripts, quizzes, flashcards, mini exams, practice tasks, PDF exports, and an AI tutor.

This fork can run locally with Ollama and Faster-Whisper, so the core workflow does not require paid OpenAI or Groq API keys.

## What It Can Do

- Transcribe lecture audio locally with Faster-Whisper.
- Generate structured notes in the same language as the lecture.
- Accept audio, images, pasted text, PDF, DOCX, and PPTX files.
- Merge multiple lecture sources into one lecture workspace.
- Generate interactive quizzes with scoring and explanations.
- Generate flip-based flashcards.
- Generate mini exams and grade text/photo/file solutions locally.
- Generate extra practice tasks by topic or keywords.
- Provide a right-side AI tutor that can answer questions in context.
- Let the AI tutor edit notes, quizzes, flashcards, and exams.
- Save lectures locally in folders.
- Export notes as TXT, Markdown, and styled PDF.

## Requirements

You need:

- Python 3.10 or newer. Python 3.11 or 3.12 is recommended.
- Git.
- Ollama for local text and vision models.
- ffmpeg for audio processing.
- Enough disk space for local models. Plan for at least 15 GB free.

## Local Models Used

Default models:

- `llama3.1:8b` for text generation.
- `qwen2.5vl:7b` for image understanding and photo/file solution checking.
- Faster-Whisper `medium` for local speech transcription.

Ollama models are downloaded with `ollama pull`. Faster-Whisper downloads its model automatically the first time transcription runs.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/meosn/lecture-voice-to-notes.git
cd lecture-voice-to-notes
```

If you want this exact development branch:

```bash
git checkout local-ai-study-workspace
```

### 2. Install Ollama

Download and install Ollama:

https://ollama.com/download

Then pull the required models:

```bash
ollama pull llama3.1:8b
ollama pull qwen2.5vl:7b
```

Check that Ollama is running:

```bash
ollama list
```

You should see `llama3.1:8b` and `qwen2.5vl:7b`.

### 3. Install ffmpeg

macOS with Homebrew:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

Windows:

Install ffmpeg from:

https://ffmpeg.org/download.html

Then make sure `ffmpeg` is available in your PATH.

### 4. Create a Python Environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the App

macOS/Linux:

```bash
streamlit run app.py --server.port 8501 --server.address localhost
```

Windows PowerShell:

```powershell
streamlit run app.py --server.port 8501 --server.address localhost
```

Open:

```text
http://localhost:8501
```

## Optional Environment Variables

The app works with defaults, but you can customize models with a `.env` file:

```env
DEFAULT_PROVIDER=ollama
DEFAULT_TRANSCRIPTION_PROVIDER=local
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=qwen2.5vl:7b
LOCAL_WHISPER_MODEL=medium
OLLAMA_HOST=http://localhost:11434
```

Smaller transcription model if your machine is slow:

```env
LOCAL_WHISPER_MODEL=small
```

Larger transcription model if you want better quality and have enough resources:

```env
LOCAL_WHISPER_MODEL=large-v3
```

## How to Use

### Create Notes from Lecture Material

1. Open `http://localhost:8501`.
2. Use `Create New Lecture` if you want a fresh lecture workspace.
3. Upload audio, image, PDF, DOCX, PPTX, or paste text.
4. Click `Start Processing`.
5. Open the tabs for transcription, notes, quiz, flashcards, and mini exam.

### Add More Material to an Existing Lecture

If a lecture is already open and you upload another source, the app merges the new source into the current lecture context instead of replacing it.

This is useful when you have:

- lecture audio,
- lecture slides,
- screenshots,
- PDF handouts,
- your own pasted notes.

### Use the AI Tutor

The right-side AI tutor can:

- answer questions about the current lecture,
- use selected text or selected question/card/task context,
- edit notes,
- edit quizzes,
- edit flashcards,
- edit mini exams.

Use `Ask` for questions and `Edit current section` when you want it to change the current material.

### Generate Extra Tasks

Use the top switch:

```text
Конспекты / Задачи
```

In `Задачи`, enter a topic or keywords, choose difficulty, and generate:

- quick-answer tasks,
- photo/file solution tasks.

Each block can be regenerated independently.

## Data Storage

Saved lectures are stored locally in:

```text
saved_lectures/
```

Temporary files are stored in:

```text
temp/
tmp/
output/
```

These folders are ignored by Git and should not be committed.

## Troubleshooting

### `Connection refused` or Ollama errors

Make sure Ollama is installed and running:

```bash
ollama list
```

If models are missing:

```bash
ollama pull llama3.1:8b
ollama pull qwen2.5vl:7b
```

### App does not open

Run it again:

```bash
streamlit run app.py --server.port 8501 --server.address localhost
```

If port `8501` is busy:

```bash
streamlit run app.py --server.port 8502 --server.address localhost
```

Then open:

```text
http://localhost:8502
```

### Audio processing fails

Install ffmpeg and make sure it is available:

```bash
ffmpeg -version
```

### First transcription is slow

Faster-Whisper downloads the selected model on first use. Later runs should start faster.

### Local generation is slow

Local AI speed depends on your computer. Try:

- using a smaller Whisper model, such as `small`,
- closing other heavy apps,
- using a smaller Ollama text model if needed.

## Main Dependencies

- Streamlit
- Ollama Python client
- Faster-Whisper
- pydub / librosa / soundfile
- pypdf
- python-docx
- python-pptx
- reportlab

## Notes for Contributors

This fork is a larger feature expansion of the original project. If contributing upstream, it may be easier to split changes into smaller PRs:

1. Local Ollama + Faster-Whisper support.
2. Additional input formats.
3. Saved lecture library.
4. Interactive quiz and flashcards.
5. AI tutor panel.
6. Practice tasks and mini exam workflow.
7. PDF export and formatting improvements.

## License

This project follows the license of the original repository.
