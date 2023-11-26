# dialogue-draft
This is a transcription application using [openai-whisper](https://github.com/openai/whisper) and [gradio](https://github.com/gradio-app/gradio).

## Setup(Ubuntu)
### Install ffmpeg
```bash
sudo apt update && sudo apt install ffmpeg
```
### Install poetry
https://python-poetry.org/docs/#installation

### Activate virtual environment
```bash
poetry shell
```
### Install dependencies
```bash
poetry install
```

## Usage
```bash
gradio app.py
```
