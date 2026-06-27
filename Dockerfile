# ─────────────────────────────────────────────────────────────────────────────
# RescueMind AI – Dockerfile
# Multi-stage build for lean production image
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1: Builder – install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# System dependencies for cryptography & other compiled packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install to a prefix so we can copy cleanly to runtime image
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime – minimal final image
FROM python:3.11-slim AS runtime

LABEL maintainer="RescueMind AI Team"
LABEL description="Multi-Agent Disaster Response & Emergency Coordination System"
LABEL version="1.0.0"

WORKDIR /app

# Non-root user for security
RUN groupadd -r rescuemind && useradd -r -g rescuemind -d /app -s /sbin/nologin rescuemind

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=rescuemind:rescuemind . .

# Create required directories
RUN mkdir -p /app/data /app/logs /app/database \
    && chown -R rescuemind:rescuemind /app

# Initialize database as non-root
USER rescuemind

# Initialize the SQLite database on first run
RUN python -c "from database.schema import initialize_database; initialize_database()" \
    || echo "Database will be initialized on first start"

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
