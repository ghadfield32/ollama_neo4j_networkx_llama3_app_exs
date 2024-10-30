#!/bin/bash

# Create and set up log directory
LOG_DIR=/workspace/logs
mkdir -p $LOG_DIR
exec > >(tee -i $LOG_DIR/start_services_$(date +%Y%m%d_%H%M%S).log) 2>&1

echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting services..."

# Activate the Mamba environment
source /opt/conda/etc/profile.d/conda.sh
mamba activate data_science_ollama

# Set environment variables for Ollama
export OLLAMA_MODELS=/workspace/data/ollama_models

# Start Ollama service
echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting Ollama service..."
ollama serve --models-path $OLLAMA_MODELS > /workspace/ollama.log 2>&1 &
ollama_pid=$!

# Wait for Ollama to be ready
echo "$(date +'%Y-%m-%d %H:%M:%S') - Waiting for Ollama to start..."
max_attempts=30
attempt=0
while ! curl -s http://localhost:11434/api/tags > /dev/null && [ $attempt -lt $max_attempts ]; do
    sleep 1
    attempt=$((attempt+1))
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Attempt $attempt of $max_attempts"
done

if [ $attempt -eq $max_attempts ]; then
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Ollama failed to start after $max_attempts attempts"
    echo "Ollama log:"
    cat /workspace/ollama.log
    exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') - Ollama is ready!"

# Start the Streamlit app
echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting Streamlit app..."
streamlit run /workspace/src/llm_engineer/app.py --server.port 8501 --server.address 0.0.0.0 > /workspace/streamlit.log 2>&1 &
streamlit_pid=$!

# Wait for Streamlit to start
max_attempts=30
attempt=0
while ! curl -s http://localhost:8501 > /dev/null && [ $attempt -lt $max_attempts ]; do
    sleep 1
    attempt=$((attempt+1))
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Attempt $attempt of $max_attempts"
done

if [ $attempt -eq $max_attempts ]; then
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Streamlit failed to start after $max_attempts attempts"
    echo "Streamlit log:"
    cat /workspace/streamlit.log
    exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') - Streamlit is ready!"

# Monitor and restart services if they fail
while true; do
    if ! kill -0 $ollama_pid 2>/dev/null; then
        echo "$(date +'%Y-%m-%d %H:%M:%S') - Ollama process died. Restarting..."
        ollama serve --models-path $OLLAMA_MODELS > /workspace/ollama.log 2>&1 &
        ollama_pid=$!
    fi

    if ! kill -0 $streamlit_pid 2>/dev/null; then
        echo "$(date +'%Y-%m-%d %H:%M:%S') - Streamlit process died. Restarting..."
        streamlit run /workspace/src/llm_engineer/app.py --server.port 8501 --server.address 0.0.0.0 > /workspace/streamlit.log 2>&1 &
        streamlit_pid=$!
    fi

    sleep 10
done
