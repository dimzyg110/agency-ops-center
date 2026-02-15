FROM debian:bookworm-slim

COPY zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.toml /data/config.toml

ENTRYPOINT ["sh", "-c", "zeroclaw gateway --port ${PORT:-8080}"]
