FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

# Install g++ and other necessary packages
RUN apt-get update -yqq && apt-get install -yqq g++
RUN apt-get install -yqq libboost-all-dev
RUN apt-get install -yqq python3.11 python3-pip
RUN rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install uv
RUN uv pip install . --system

# Expose port
EXPOSE 8080

# Run the server
#CMD uvicorn main:app --host 0.0.0.0 --port 8080 --workers 16
CMD uv run gunicorn -g 16 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8080
