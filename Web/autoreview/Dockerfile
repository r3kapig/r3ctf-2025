FROM golang:1.24 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM gcr.io/distroless/static
WORKDIR /root/
COPY --from=builder /app/main .
COPY .env .env
EXPOSE 8080
CMD ["./main", "server"]