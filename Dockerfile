FROM ubuntu:22.04

# ----------------
# Install packages
# ----------------
# Disable time zone prompts when installing tzdata
ENV DEBIAN_FRONTEND=noninteractive
# Install packages
RUN apt update && apt upgrade -y \
    && apt install -y \
        curl \
        ffmpeg \
        locales \
        python3.10 \
        tzdata \
        vim \
    && rm -rf /var/lib/apt/lists/*

# ----------------
# Install poetry
# ----------------
# Reference: https://python-poetry.org/docs/
RUN curl -sSL https://install.python-poetry.org | python3.10 -
ENV PATH /root/.local/bin:$PATH
RUN poetry config virtualenvs.in-project true

# ----------------
# Locale and language settings
# ----------------
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# ----------------
# Install dependencies
# ----------------
# Reference: https://python-poetry.org/docs/basic-usage/
WORKDIR /opt/dialogue-draft
COPY app.py poetry.lock poetry.toml pyproject.toml /opt/dialogue-draft/
RUN poetry install
