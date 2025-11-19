FROM ghcr.io/astral-sh/uv:alpine

COPY .cache/ /app/.cache/
COPY src /app/src
COPY public /app/public
COPY scripts/python/seed.py /app/scripts/python/seed.py
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY README.md /app/README.md

WORKDIR /app

# Install dependencies
RUN uv sync --frozen

# Seed database
RUN uv run python scripts/python/seed.py
RUN rm -rf .cache

# Expose port 8000 for the API
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Start the application
CMD ["uv", "run", "comp370"]
