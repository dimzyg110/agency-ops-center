FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y curl && \
    curl -L -o /usr/local/bin/zeroclaw https://github.com/theonlyhennygod/zeroclaw/releases/latest/download/zeroclaw-x86_64-unknown-linux-gnu && \
    chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.yaml /data/config.yaml

ENTRYPOINT ["zeroclaw", "gateway", "--port", "8080"]
