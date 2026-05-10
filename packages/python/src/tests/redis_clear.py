"""
Author: Sean Froning
Created Date: 5.9.2026
Shared redis cleanup for tests
"""
from ..focus_python import config, queue  # pyright: ignore[reportMissingImports]


def clear_redis_queue() -> None:
    """Flush the RQ queue for this worker domain"""
    print("Clearing Redis queue")
    try:
        redis_connection = queue.get_connection()
        qname = config.get_required("domain")
        redis_connection.delete(f"rq:queue:{qname}")
        redis_connection.delete(f"rq:queue:{qname}:queued")
        print("Redis queue cleared")
    except Exception as e:
        print(f"Error clearing Redis queue: {str(e)}")
