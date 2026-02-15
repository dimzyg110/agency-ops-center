FROM rust:1.75-slim AS builder
RUN cargo build --release --target x86_64-unknown-linux-gnu

FROM debian:bookworm-slim
COPY --from=builder /target/x86_64-unknown-linux-gnu/release/zeroclaw /usr/local/bin/
ENTRYPOINT ["zeroclaw"]
