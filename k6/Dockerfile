FROM golang:1.23 AS builder
RUN go install go.k6.io/xk6/cmd/xk6@latest
RUN xk6 build --with github.com/grafana/xk6-mcp@latest --output /k6

FROM grafana/k6:latest
COPY --from=builder /k6 /usr/local/bin/k6
