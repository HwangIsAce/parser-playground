# Playground

## Demo

![Playground Demo](assets/playground.gif)

## Overview
Document parsing and extraction playground with extensible parser architecture.


## Getting Started

### Backend

```
cd backend
uv sync --all-extras
uv run uvicorn main:app --reload
```

### Frontend

```
cd frontend
npm install
npm run dev
```

### Redis & RQ Worker

```bash
# Install Redis (if not already installed)
sudo apt-get update
sudo apt-get install -y redis-server

# Start Redis server (if not already running)
redis-server --daemonize yes
```

In separate terminals, start RQ workers:
```bash
cd backend
uv run rq worker parse_queue
```

