# dialogue-draft
This is a transcription application using [openai-whisper](https://github.com/openai/whisper) and [gradio](https://github.com/gradio-app/gradio).

![transcription](https://github.com/kyashy/dialogue-draft/assets/98370541/7c4d297a-90aa-4f7b-96b2-28ab505dcb57)

## Setup
1. Install Docker Engine on Ubuntu

    https://docs.docker.com/engine/install/ubuntu/

2. Install the Compose plugin

    https://docs.docker.com/compose/install/linux/

3. Install NVIDIA Container Toolkit

    https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

4. Build docker image

    ```bash
    docker compose build
    ```

## Usage

1. Start application

    ```bash
    docker compose up -d
    ```
    Running on local URL:  http://localhost:7860

2. Stop application

    ```bash
    docker compose down
    ```

## Setup without Docker
1. Install ffmpeg

    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

2. Install poetry

    https://python-poetry.org/docs/#installation

3. Install dependencies

    ```bash
    poetry install
    ```

## Usage without Docker
1. Start application

    ```bash
    poetry run gradio app.py
    ```
    Running on local URL:  http://localhost:7860

2. Stop application

    Press `CTRL+C` on the terminal

## License

This application includes components licensed under the Apache License, Version 2.0 (https://github.com/gradio-app/gradio) and the MIT License (https://github.com/openai/whisper).
