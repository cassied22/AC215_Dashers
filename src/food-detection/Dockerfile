# Use an official Python runtime as a base image
FROM python:3.9-slim

ENV PYENV_SHELL=/bin/bash

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git ffmpeg && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

# Set the working directory in the container
WORKDIR /app

# Install python packages
ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

# Copy the current directory contents into the container
ADD . /app

# Entry point
ENTRYPOINT ["/bin/bash"]

# Get into the pipenv shell
CMD ["-c", "pipenv shell"]
