"""
Author: Sean Froning
Created Date: 5.3.2026
Redis queue manager with connection pooling
"""

import time
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from redis import Redis, ConnectionPool
from rq import Queue
from rq.job import Job
from .config import config
from .logging import logging

logger = logging.get_logger(__name__)

QUEUE_NAME = config.get_required("domain")
JOB_TIMEOUT = 3600


class _Queue:
    _init_lock = threading.Lock()
    _instance: Optional["_Queue"] = None
    _connection_pool: Optional[ConnectionPool] = None
    _rq_queue: Optional[Queue] = None

    def __new__(cls) -> "_Queue":
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _get_connection(self) -> Redis:
        if self._connection_pool is None:
            with self._init_lock:
                if self._connection_pool is None:
                    self._connection_pool = ConnectionPool.from_url(
                        config.get_required("redis"),
                        max_connections=20,
                        retry_on_timeout=True,
                        socket_keepalive=True,
                    )
                    Redis(connection_pool=self._connection_pool).ping()
        return Redis(connection_pool=self._connection_pool)

    def get_connection(self) -> Redis:
        return self._get_connection()

    def _get_rq_queue(self) -> Queue:
        if self._rq_queue is None:
            with self._init_lock:
                if self._rq_queue is None:
                    self._rq_queue = Queue(
                        QUEUE_NAME, connection=self._get_connection()
                    )
        return self._rq_queue

    def enqueue_jobs(self, jobs: List[Dict[str, Any]]) -> List[Job]:
        enqueued, failures = [], []
        rq = self._get_rq_queue()
        for job_data in jobs:
            try:
                func = job_data["func"]
                args = job_data.get("args", [])
                job_id = job_data.get("job_id")
                tags = job_data.get("tags")
                metadata = job_data.get("metadata")
                job_kwargs = {
                    "job_timeout": job_data.get("job_timeout", JOB_TIMEOUT),
                    "job_id": job_id,
                    "meta": metadata or {},
                }
                job_kwargs_clean = {k: v for k, v in job_kwargs.items() if k != "tags"}
                if tags:
                    job = rq.enqueue(func, *args, tags=tags, **job_kwargs_clean)
                else:
                    job = rq.enqueue(func, *args, **job_kwargs_clean)
                func_name = (
                    getattr(func, "__name__", None)
                    or getattr(func, "__qualname__", None)
                    or str(func)
                )
                logger.info(f"Job enqueued: {job.id} | {QUEUE_NAME} | {func_name}")
                enqueued.append(job)
            except Exception as e:
                failures.append({"job_id": job_data.get("job_id"), "error": str(e)})
                logger.error(
                    "job_enqueue_failed", job_id=job_data.get("job_id"), error=str(e)
                )
        if failures:
            raise RuntimeError(f"{len(failures)} jobs failed to enqueue")
        return enqueued

    def enqueue_chunked_jobs(
        self,
        items: List[Any],
        chunk_size: int,
        func: Any,
        job_id_prefix: str,
        extra_args: Tuple[Any, ...] = (),
        job_timeout: Optional[int] = None,
    ) -> List[Job]:
        """Enqueue one RQ job per chunk of items with a shared timestamp in each job_id"""
        if not items:
            return []
        if chunk_size < 1:
            raise ValueError("chunk_size must be at least 1")
        timeout = job_timeout if job_timeout is not None else JOB_TIMEOUT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        specs: List[Dict[str, Any]] = []
        chunk_idx = 0
        for i in range(0, len(items), chunk_size):
            chunk = items[i : i + chunk_size]
            specs.append(
                {
                    "func": func,
                    "args": (chunk,) + extra_args,
                    "job_id": f"{job_id_prefix}_{timestamp}_{chunk_idx}",
                    "job_timeout": timeout,
                }
            )
            chunk_idx += 1
        return self.enqueue_jobs(specs)

    def close(self) -> None:
        if self._connection_pool is not None:
            self._connection_pool.disconnect()
            self._connection_pool = None
            self._rq_queue = None
            logger.info("Redis connection pool closed")

    def health_check(self) -> Dict[str, Any]:
        try:
            conn = self._get_connection()
            start = time.time()
            conn.ping()
            ping_ms = (time.time() - start) * 1000
            rq = self._get_rq_queue()
            queued = len(rq)
            failed = len(rq.failed_job_registry)
            status = (
                "healthy" if failed < 50 else "warning" if failed < 100 else "critical"
            )
            return {
                "status": status,
                "redis": {"connected": True, "ping_ms": round(ping_ms, 2)},
                "queued": queued,
                "failed": failed,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


queue = _Queue()
