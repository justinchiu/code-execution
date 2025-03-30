FROM python:3.10-slim

# Install g++ and other necessary packages
RUN apt-get update && apt-get install -y \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --no-cache-dir -e . && \
    pip install --no-cache-dir uvicorn

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Set up a non-root user for security
RUN useradd -m appuser
USER appuser

# Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]