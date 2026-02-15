# ZeroClaw Agents

Easily create new ZeroClaw agents by copying the template folder.

## Quick Start

```bash
# Copy template for a new agent
cp -r zeroclaw-template zeroclaw-roviq
cp -r zeroclaw-template zeroclaw-glass
cp -r zeroclaw-template zeroclaw-ac
```

## Included Templates

### zeroclaw-template
Base template - copy this to create new agents

### zeroclaw-roviq
Roviq agency operations agent

### zeroclaw-glass
GLASS data/operations agent

## Each Agent Folder Contains

```
zeroclaw-[name]/
├── Dockerfile
├── config.yaml       # Edit name and settings
└── railway.toml     # Railway deploy config
```

## Configuration

Edit `config.yaml` for each agent:

```yaml
[core]
name = "zeroclaw-roviq"  # Change this
```

## Adding to Docker Compose

```yaml
services:
  zeroclaw-roviq:
    build: ./zeroclaw-roviq
    env_file:
      - ../.env
    volumes:
      - ../data/zeroclaw-roviq:/data

  zeroclaw-glass:
    build: ./zeroclaw-glass
    # ...
```

## Railway Deployment

Each folder has its own `railway.toml` - deploy individually to Railway.
