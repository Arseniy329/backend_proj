# ============================================================
# Stage 1 — Builder: compile wheels so the runtime image
#            never needs gcc or other build-time tooling.
# ============================================================
FROM python:3.13-slim AS builder

WORKDIR /wheels

# Install wheel-building utilities
RUN pip install --upgrade pip build wheel

# Copy only the dependency manifest first for better layer caching
COPY requirements.txt .

# Compile every dependency into a .whl file
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ============================================================
# Stage 2 — Runtime: lean image that runs in production.
# ============================================================
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create a non-root system user for security hardening
RUN addgroup --system appgroup && \
    adduser  --system --ingroup appgroup appuser

# Install the pre-compiled wheels (no build deps needed, no cache)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index \
        --find-links=/wheels /wheels/*.whl && \
    rm -rf /wheels

# Copy application source code
COPY . .

# Collect static files at build time (WhiteNoise will serve them)
# SECRET_KEY is required by Django even during collectstatic.
RUN SECRET_KEY=build-time-placeholder-not-used-in-production \
    python manage.py collectstatic --noinput

# Drop to non-root for all runtime operations
USER appuser

EXPOSE 8000

# 3 Gunicorn workers; timeout kept short to respect Render's health-check grace period
CMD ["gunicorn", "education_plat.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "30"]