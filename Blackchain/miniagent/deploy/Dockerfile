FROM python:3.11.6-slim

RUN true && \
    useradd -u 1000 -m user && \
    apt-get update && \
    apt-get install -y curl git socat bsdmainutils && \
    rm -rf /var/cache/apt/lists /var/lib/apt/lists/* && \
    true

# Install Foundry
ENV FOUNDRY_DIR=/opt/foundry

ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}

RUN true && \
    curl -L https://foundry.paradigm.xyz | bash && \
    foundryup && \
    true


COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY proxy.py /proxy.py
COPY init.py /init.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY project /project

RUN true && \
    cd /project && \
    forge build --out /artifacts/out --cache-path /artifacts/cache && \
    true

CMD ["/entrypoint.sh"]

EXPOSE 8888