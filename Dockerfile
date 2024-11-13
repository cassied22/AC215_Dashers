# Use an official Python runtime as a parent image
FROM python:3.9.18-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (for compiling dependencies)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install "poetry==1.5.1"

# Set the working directory in the Docker image
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# Copy source code into the container
COPY src/genai  /app/src/genai
COPY README.md /app/README.md
COPY app.py /app/app.py

# Don't push the image to Dockerhub
COPY .env /app/.env
COPY .streamlit /app/.streamlit

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Expose port for Streamlit
EXPOSE 8501

# Command to run Streamlit app
CMD ["streamlit", "run", "app.py"]
