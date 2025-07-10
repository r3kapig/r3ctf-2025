FROM golang:tip-bookworm AS base
WORKDIR /app

RUN apt update && apt install -y socat

COPY --chmod=555 app.py run
COPY entrypoint.sh entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
