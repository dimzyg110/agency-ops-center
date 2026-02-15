FROM debian:bookworm-slim

COPY bin/zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.yaml /data/config.yaml

ENTRYPOINT ["zeroclaw", "gateway", "--port", "8080"]
