FROM python:3.10-slim

# Systemd journal python bindings need libsystemd
RUN apt-get update && apt-get install -y \
    python3-systemd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY getSolarData.py /app/getSolarData.py

# Script-Entrypoint
CMD ["python3", "/app/getSolarData.py"]