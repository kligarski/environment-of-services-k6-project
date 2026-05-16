FROM golang:1.25 AS builder
RUN go install go.k6.io/xk6/cmd/xk6@v0.20.1
RUN xk6 build --with github.com/dgzlopes/xk6-mcp@v0.0.3 --output /tmp/k6

FROM grafana/k6:latest
COPY --from=builder /tmp/k6 /usr/local/bin/k6
