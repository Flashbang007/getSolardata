FROM python:3.10-slim

# Systemd journal python bindings benötigen libsystemd
RUN apt-get update && apt-get install -y \
    python3-systemd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY getSolarData.py /app/getSolarData.py

# Falls du requirements.txt hättest – optional
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Script-Entrypoint
CMD ["python3", "/app/getSolarData.py"]