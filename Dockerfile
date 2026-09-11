# Multi-stage production build for MEDHĀ IDE
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# Runner stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Install essential dev toolchains and PySide6/Qt runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gdb \
    git \
    cmake \
    make \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies
COPY --from=builder /install /usr/local

# Security hardening: create non-root user
RUN useradd -u 10001 -m -s /bin/bash medhauser && \
    mkdir -p /workspace && \
    chown -R medhauser:medhauser /workspace /app

# Copy application source
COPY --chown=medhauser:medhauser medha /app/medha
COPY --chown=medhauser:medhauser main.py /app/main.py
COPY --chown=medhauser:medhauser README.md /app/README.md

USER medhauser
WORKDIR /workspace
ENV PYTHONPATH=/app
ENV QT_QPA_PLATFORM=offscreen

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -m medha health || exit 1

ENTRYPOINT ["python3", "-m", "medha"]
