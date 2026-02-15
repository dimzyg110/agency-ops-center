# Services

All agent services go here.

## Structure

```
services/
├── docker-compose.yml    # Run all services
├── bot-bus/            # Message relay + Discord forwarding
│   ├── server.js
│   ├── discord-forwarder.js
│   ├── bot-client.js
│   ├── package.json
│   └── railway.json
└── zeroclaw/           # Client agent (duplicate folder for each client)
    ├── Dockerfile
    ├── config.yaml
    └── railway.toml
```

## Multiple Clients

Each client gets their own ZeroClaw instance:

```bash
# Copy zeroclaw folder for each client
cp -r zeroclaw zeroclaw-ac      # Client: AC
cp -r zeroclaw zeroclaw-ch      # Client: CH
cp -r zeroclaw zeroclaw-hop     # Client: HOP
```

Then update `docker-compose.yml`:

```yaml
services:
  zeroclaw-ac:
    build: ./zeroclaw-ac
  zeroclaw-ch:
    build: ./zeroclaw-ch
  zeroclaw-hop:
    build: ./zeroclaw-hop
```

## Bot Bus Communication

All agents communicate through the bot-bus:

```
[ZeroClaw AC] ---> [Bot Bus] ---> [Discord]
[ZeroClaw CH] ----> [Bot Bus] ---> [Discord]
[COO Agent] ------> [Bot Bus] ---> [Discord]
```

- Agents POST to `/relay` to send messages
- Agents GET `/subscribe?bot=agent-id` to receive messages (SSE)
- Messages also forward to Discord for human visibility
