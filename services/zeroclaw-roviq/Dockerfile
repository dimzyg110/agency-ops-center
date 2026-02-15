FROM debian:bookworm-slim

COPY zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

RUN mkdir -p /root/.zeroclaw
COPY config.toml /root/.zeroclaw/config.toml

ENTRYPOINT ["sh", "-c", "if [ -n \"$OPENROUTER_API_KEY\" ]; then sed -i \"s|^api_key = .*|api_key = \\\"$OPENROUTER_API_KEY\\\"|\" /root/.zeroclaw/config.toml; fi; zeroclaw daemon --host 0.0.0.0 --port ${PORT:-8080}"]
