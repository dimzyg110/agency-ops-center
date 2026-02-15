FROM debian:bookworm-slim

COPY zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.yaml /data/config.yaml

ENTRYPOINT ["sh", "-c", "zeroclaw gateway --port ${PORT:-8080}"]
