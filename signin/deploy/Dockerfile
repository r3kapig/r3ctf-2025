FROM python:3.11-slim

RUN useradd -u 1000 -m user && \
    apt-get update && \
    apt-get install -y curl git socat bsdmainutils && \
    rm -rf /var/cache/apt/lists /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry

ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}

RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

RUN mkdir /project && \
    cd /project && \
    forge init && \
    rm -rf ./src ./script ./test ./foundry.toml

COPY project/foundry.toml /project/foundry.toml
COPY project/src /project/src
COPY project/script /project/script

RUN cd /project && forge build --out /artifacts/out --cache-path /artifacts/cache

COPY proxy.py /proxy.py
COPY init.py /init.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]

EXPOSE 8888