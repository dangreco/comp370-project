FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -1sLf 'https://dl.cloudsmith.io/public/task/task/setup.deb.sh' | bash \
    && apt-get install -y --no-install-recommends task

COPY src ./src
COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen

RUN curl -L -o en_core_web_sm.tar.gz https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz \
    && mkdir -p /app/models/spacy/en_core_web_sm \
    && tar -xzf en_core_web_sm.tar.gz -C /app/models/spacy/en_core_web_sm --strip-components=3 \
    && rm en_core_web_sm.tar.gz

RUN mkdir -p /app/models/nltk/punkt_tab \
    && uv run python -m nltk.downloader -d /app/models/nltk/punkt_tab punkt_tab

RUN mkdir -p /app/models/nltk/averaged_perceptron_tagger_eng \
    && uv run python -m nltk.downloader -d /app/models/nltk/averaged_perceptron_tagger_eng averaged_perceptron_tagger_eng

COPY public/ ./public
COPY scripts/ ./scripts
COPY tasks/ ./tasks
COPY Taskfile.yml ./

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DIR_NLTK=/app/models/nltk
ENV DIR_SPACY=/app/models/spacy

CMD ["sh", "scripts/run.sh"]
