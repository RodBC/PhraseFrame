FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PHRASEFRAME_DATA_DIR=/data

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install .

RUN mkdir -p /data/documents \
    && useradd --create-home --uid 10001 phraseframe \
    && chown -R phraseframe:phraseframe /data

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health')"

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["sh", "-c", "uvicorn phraseframe.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
