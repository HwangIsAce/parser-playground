# Playground

## Overview
Document parsing and extraction playground with extensible parser architecture.


## Getting Started

### Backend

1. Install and start Redis:
```bash
# Install Redis (if not already installed)
sudo apt-get install -y redis-server

# Start Redis server
redis-server --daemonize yes
```

2. Start the API server:
```bash
cd backend
uv sync --all-extras
uv run uvicorn main:app --reload
```

3. Start the RQ worker (in a separate terminal):
```bash
cd backend
uv run rq worker parse_queue
```

### Frontend

```
cd frontend
npm install
npm run dev
```

## Example

This section will be updated
