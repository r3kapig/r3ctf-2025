FROM golang:1.24.0-bookworm@sha256:b970e6d47c09fdd34179acef5c4fecaf6410f0b597a759733b3cbea04b4e604a AS builder

WORKDIR /build

COPY app/go.mod app/go.sum ./

RUN go mod download

COPY app/ .

RUN GO111MODULE=on GOOS=linux GOARCH=amd64 CGO_ENABLED=1 go build -ldflags '-s -w' .

FROM debian:bookworm-slim@sha256:6ac2c08566499cc2415926653cf2ed7c3aedac445675a013cc09469c9e118fdd as puppeteer

ADD node-v22.17.0-linux-x64.tar.xz /opt/

RUN ln -s /opt/node-v22.17.0-linux-x64/bin/node /usr/bin/node &&\
    ln -s /opt/node-v22.17.0-linux-x64/bin/npm /usr/bin/npm &&\
    ln -s /opt/node-v22.17.0-linux-x64/bin/npx /usr/bin/npx

ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_CACHE_DIR=/build/puppeteer_cache

WORKDIR /build
COPY bot/package.json /build/
RUN npm i && npx puppeteer browsers install chrome

FROM nginx:1.29.0-bookworm@sha256:93230cd54060f497430c7a120e2347894846a81b6a5dd2110f7362c5423b4abc

RUN apt-get update && \ 
    apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libasound2 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

ADD node-v22.17.0-linux-x64.tar.xz /opt/

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /build/ /app/
COPY --from=puppeteer /build/ /bot/
COPY bot/ /bot/
COPY start.sh /start.sh

RUN ln -s /opt/node-v22.17.0-linux-x64/bin/node /usr/bin/node &&\
    ln -s /opt/node-v22.17.0-linux-x64/bin/npm /usr/bin/npm &&\
    ln -s /opt/node-v22.17.0-linux-x64/bin/npx /usr/bin/npx &&\
    ln -s /opt/node-v22.17.0-linux-x64/bin/corepack /usr/bin/corepack &&\
    useradd -r --no-create-home -s /sbin/nologin app &&\
    useradd -r --no-create-home -s /sbin/nologin bot &&\
    mkdir -p /var/log/nginx &&\
    mkdir -p /var/log/app &&\
    mkdir -p /var/log/bot &&\
    mkdir -p /app &&\
    mkdir -p /bot &&\
    chown -R app:app /app &&\
    chown -R bot:bot /bot &&\
    chmod 700 /app /bot &&\
    chmod 700 /start.sh

CMD ["/start.sh"]