FROM ubuntu:questing-20250601
RUN apt-get update && apt-get install -y socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY start.sh /start.sh
COPY pwn /pwn
RUN chmod +x /start.sh /pwn

EXPOSE 1337
ENTRYPOINT ["/start.sh"]
