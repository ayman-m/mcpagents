FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY start.sh .
COPY icon.png .
RUN chmod +x start.sh

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
ENV PYTHONPATH=/app/src
CMD ["./start.sh"]
