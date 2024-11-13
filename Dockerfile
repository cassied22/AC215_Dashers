# Use the Anaconda base image
FROM continuumio/anaconda3:latest

# Set working directory
WORKDIR /app

# Copy the environment.yml and project files
COPY environment.yml /app/
COPY src/genai /app/src/genai
COPY README.md /app/README.md
COPY app.py /app/app.py
COPY .env /app/.env
COPY .streamlit /app/.streamlit

# Ensure the datapipeline folder is copied correctly from src
COPY src/datapipeline /app/datapipeline
COPY src/food_detection /app/food_detection
# Ensure the datapipeline folder is copied from the correct location

# Create the Conda environment
RUN conda env create -f /app/environment.yml

# Install langchain-community within the Conda environment
RUN /opt/conda/envs/discovery-generative-ai/bin/pip install langchain-community

# Install system dependencies using apt-get (protobuf-compiler, libprotobuf-dev, build-essential)
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    libprotobuf-dev \
    build-essential \
    cmake

# Activate the environment and run the app
CMD ["conda", "run", "--no-capture-output", "-n", "discovery-generative-ai", "streamlit", "run", "app.py"]
