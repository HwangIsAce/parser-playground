"""Tests for Redis Queue."""
import pytest

try:
    from redis import Redis
    from rq import Queue
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis/RQ not installed")
class TestRedisQueue:
    """Test Redis Queue configuration."""
    
    def test_redis_connection(self):
        """Test Redis connection."""
        from infrastructure.queue.redis_queue import redis_conn
        
        # Try to ping Redis
        try:
            redis_conn.ping()
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
    
    def test_queue_creation(self):
        """Test queue creation."""
        from infrastructure.queue.redis_queue import default_queue
        
        assert default_queue is not None
        assert isinstance(default_queue, Queue)
        assert default_queue.name == "parse_queue"
