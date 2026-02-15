# Build stage - compile ZeroClaw from source
FROM rust:1.75-bookworm AS builder

RUN apt-get update && apt-get install -y curl git
RUN git clone https://github.com/theonlyhennygod/zeroclaw.git /build
WORKDIR /build
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

COPY --from=builder /build/target/release/zeroclaw /usr/local/bin/
RUN chmod +x /usr/local/bin/zeroclaw

WORKDIR /data

COPY config.yaml /data/config.yaml

ENTRYPOINT ["zeroclaw", "gateway", "--port", "8080"]
