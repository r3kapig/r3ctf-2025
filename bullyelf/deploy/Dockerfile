FROM python:3-alpine

RUN apk add --no-cache socat libcap
RUN mkdir /work /work/cwd /work/dev \
 && mknod /work/dev/null c 1 3 \
 && chmod 666 /work/dev/null \
 && adduser -H -D ctf \
 && touch /work/cwd/elf \
 && chown ctf /work/cwd/elf

RUN mkdir /app
COPY server.py /app
COPY start.sh /

CMD ["/start.sh"]
