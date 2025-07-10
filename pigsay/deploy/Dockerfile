FROM python:3.14.0b2-alpine3.21

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers
RUN addgroup -S r3ctf && \
    adduser -S r3ctf -G r3ctf -s /bin/sh && \
    chown r3ctf:r3ctf /app

COPY start.sh /start.sh
COPY app.py /app/
COPY upgrade.sh /app/
COPY pyproject.toml /app/
COPY public /app/public/
COPY static /app/static/

RUN chmod 755 /start.sh && \
    chmod 744 /app/app.py && \
    chmod 755 /app/upgrade.sh

USER r3ctf
RUN uv tool install pigsay && uv sync

USER root
ENTRYPOINT ["/start.sh"]