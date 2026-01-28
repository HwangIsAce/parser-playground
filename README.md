# Playground

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

**Enhanced Mode (Chandra Parser) - Multi-Worker Support:**

The Chandra parser loads a large model (~13-16GB GPU memory) per worker process. The system now supports multiple workers with automatic GPU memory management:

- **File locking**: Prevents multiple workers from loading the model simultaneously
- **GPU memory check**: Each worker checks available GPU memory before loading (requires ~16GB free)
- **Automatic queuing**: Workers wait for other workers to finish if memory is insufficient

**Recommended worker count:**
- GPU with 32GB: Up to 2 workers
- GPU with 64GB: Up to 4 workers
- Calculate: `max_workers = GPU_total_memory_GB / 16`

In separate terminals, start RQ workers:
```bash
cd backend
uv run rq worker parse_queue
```

You can run multiple workers, but ensure total GPU memory usage doesn't exceed available memory.

**Note:** If you see "CUDA out of memory" errors:
1. Check GPU memory: `nvidia-smi`
2. Reduce the number of workers
3. Workers will automatically wait if memory is insufficient

## Example

This section will be updated
