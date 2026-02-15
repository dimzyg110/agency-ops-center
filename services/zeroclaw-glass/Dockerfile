FROM debian:bookworm-slim

COPY zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.yaml /data/config.yaml

ENTRYPOINT ["zeroclaw", "gateway", "--host", "0.0.0.0", "--port", "8080"]
