# Use the official Debian-hosted Python image
FROM python:3.12-slim-bookworm

ARG DEBIAN_PACKAGES="build-essential git screen vim"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1

# Add CI environment variable (defaults to false)
ENV CI=false

# Add DEV environment variable (defaults to 0)
ENV DEV=0

# Ensure we have an up to date baseline, install dependencies and
# create a user so we don't run the app as root
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    mkdir -p /app/.pytest_cache && \
    chown app:app /persistent && \
    chown -R app:app /app && \
    chmod -R 777 /app/.pytest_cache

# Switch to the new user
USER app
WORKDIR /app

# Install python packages
ADD --chown=app:app Pipfile Pipfile.lock /app/

# Install both default and development dependencies
RUN pipenv sync --dev

# Add the rest of the source code
ADD --chown=app:app . /app

# Make sure the entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh

# Entry point
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]