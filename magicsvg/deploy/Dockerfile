FROM python:3

WORKDIR /

COPY stretch buster bullseye bookworm main.py entrypoint.sh /
RUN chmod 755 stretch buster bullseye bookworm
RUN pip install Pillow
RUN apt update && apt install -y socat

ENTRYPOINT ["/entrypoint.sh"]
