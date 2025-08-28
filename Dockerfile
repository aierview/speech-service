FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install uv

WORKDIR /app
COPY . /app

EXPOSE 4000
CMD ["uv", "run", "app.py"]
