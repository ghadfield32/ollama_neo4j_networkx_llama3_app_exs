# Base image with CUDA support
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set environment variables and arguments
ARG ENV_NAME=data_science_ollama
ARG PYTHON_VER=3.10
ENV ENV_NAME=$ENV_NAME
ENV PYTHON_VER=$PYTHON_VER
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies and required libraries
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    gnupg \
    git \
    vim \
    build-essential \
    libxml2 \
    libarchive-dev \
    libc6 \
    && rm -rf /var/lib/apt/lists/*


# Install Miniconda and Mamba
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-$(uname -m).sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p $CONDA_DIR \
    && rm ~/miniconda.sh \
    && $CONDA_DIR/bin/conda clean -a -y \
    && $CONDA_DIR/bin/conda install -n base -c conda-forge mamba -y \
    && $CONDA_DIR/bin/conda clean -a -y

# Update Conda and Mamba
RUN mamba update -n base -c defaults conda mamba -y

# Create the environment using Mamba
COPY .devcontainer/environment.yml /tmp/environment.yml
RUN mamba env create -f /tmp/environment.yml && \
    mamba clean -a -y

RUN ldconfig

# Activate the Conda environment and install torch and other pip packages
RUN /bin/bash -c "source $CONDA_DIR/etc/profile.d/conda.sh && conda activate $ENV_NAME && \
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118"

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Set working directory
WORKDIR /workspace

# Expose ports for services
EXPOSE 11434 8501 8100 8080

# Debugging: Print the current directory and list its contents
RUN echo "Current working directory is:" && pwd
RUN echo "Listing current directory contents:" && ls -l

# Copy start_services script and debug path
COPY scripts/start_services.sh /workspace/start_services.sh

# Debug: List files after COPY
RUN echo "Listing contents of /workspace after copying start_services.sh:" && ls -l /workspace

# Make start_services.sh executable
RUN chmod +x /workspace/start_services.sh && \
    echo "Permissions after chmod:" && ls -l /workspace/start_services.sh

# Entry point to start services
ENTRYPOINT ["/workspace/start_services.sh"]
