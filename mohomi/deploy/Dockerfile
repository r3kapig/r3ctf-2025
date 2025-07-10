FROM golang:alpine AS mihomo-builder

RUN apk add --no-cache git

ARG MIHOMO_BRANCH=v1.19.11
RUN git clone https://github.com/MetaCubeX/mihomo.git -b ${MIHOMO_BRANCH} --depth 1 /src
WORKDIR /src

RUN --mount=type=cache,id=go-mod,target=/go/pkg/mod \
    go mod download
RUN --mount=type=cache,id=go-build,target=/root/.cache/go-build \
    --mount=type=cache,id=go-mod,target=/go/pkg/mod \
    go build -tags with_gvisor -o mihomo -ldflags "-w -s" -v .

FROM alpine:latest AS final

RUN apk add --no-cache socat runit tini bash
RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app -s /bin/bash app

COPY --from=mihomo-builder /src/mihomo /usr/bin/mihomo
COPY ./service/ /etc/service/
COPY ./entrypoint.sh /sbin/entrypoint.sh
COPY ./config.yaml /etc/mihomo/config.yaml

EXPOSE 1337
ENTRYPOINT ["/sbin/entrypoint.sh"]