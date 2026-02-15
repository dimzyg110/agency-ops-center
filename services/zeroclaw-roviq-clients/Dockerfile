FROM debian:bookworm-slim

COPY zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

RUN mkdir -p /root/.zeroclaw
COPY config.toml /root/.zeroclaw/config.toml

ENTRYPOINT ["sh", "-c", "zeroclaw gateway --port ${PORT:-8080}"]
