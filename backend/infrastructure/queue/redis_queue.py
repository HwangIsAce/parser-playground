"""Redis Queue configuration."""
from redis import Redis
from rq import Queue
from config import settings

# Redis connection
redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=False  # RQ requires bytes
)

# Default queue for parsing tasks
default_queue = Queue('parse_queue', connection=redis_conn)
