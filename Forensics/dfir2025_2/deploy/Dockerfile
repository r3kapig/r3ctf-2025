FROM python:3-alpine

WORKDIR /opt/challenge

COPY server.py .
COPY answers.json .

EXPOSE 10001
CMD ["python", "-u", "server.py"]
