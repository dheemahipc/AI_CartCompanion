# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY diet_agent/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

# These labels are overridden at build-time by docker/metadata-action in CI.
LABEL org.opencontainers.image.source="https://github.com/rani700/DietDoctorAI"
LABEL org.opencontainers.image.description="Diet Expert AI – Agentic health & fitness system built with Google ADK"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY diet_agent/ ./diet_agent/

# Create directories for persistent data
RUN mkdir -p /app/user_data /app/conversation_data

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose the default ADK dev-server port
EXPOSE 8000

# Default: start the FastAPI production server
CMD ["uvicorn", "diet_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
