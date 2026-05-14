"""
Author: Sean Froning
Created Date: 5.3.2026
Centralized database connection manager
"""

import re
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlencode, urlparse
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from .config import config
from .logging import logging

logger = logging.get_logger(__name__)

DB_POOL_MIN = config.get_db_pool_min()
DB_POOL_MAX = config.get_db_pool_max()
DATABASE_URL = config.get_required("database")
DB_APP_NAME = f"db-" + config.get_required("domain")


class DatabaseConnectionPool:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.connection_pool = None
        return cls._instance

    def _ensure_pool(self) -> None:
        if self.connection_pool is None:
            with self._lock:
                if self.connection_pool is None:
                    self._init_pool()

    def _clean_pool_url(self, url: str) -> str:
        if "?" in url:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            qs.pop("pgbouncer", None)
            new_q = urlencode(qs, doseq=True)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" + (
                f"?{new_q}" if new_q else ""
            )
        return url

    def _init_pool(self) -> None:
        dsn = self._clean_pool_url(DATABASE_URL)
        if DB_POOL_MIN > DB_POOL_MAX:
            raise ValueError("DB_POOL_MIN cannot exceed DB_POOL_MAX")
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=DB_POOL_MIN,
            maxconn=DB_POOL_MAX,
            dsn=dsn,
            application_name=DB_APP_NAME,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )
        logger.info("Database pool initialized %d-%d", DB_POOL_MIN, DB_POOL_MAX)

    def get_conn(self):
        with self._lock:
            self._ensure_pool()
            pool = self.connection_pool
        if pool is None:
            raise RuntimeError("Database pool is closed")
        return pool.getconn()

    def put_conn(self, conn) -> None:
        with self._lock:
            pool = self.connection_pool
        if pool is None:
            conn.close()
            return
        pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        self._ensure_pool()
        conn = cursor = None
        try:
            conn = self.get_conn()
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.put_conn(conn)

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
        return_all_rows: bool = False,
    ) -> Union[Dict, List[Dict], str, None]:
        self._ensure_pool()
        q = re.sub(r"\$\d+", "%s", query)
        with self.get_cursor() as cur:
            cur.execute(q, params)
            if fetch_one:
                r = cur.fetchone()
                return dict(r) if r else None
            if return_all_rows:
                return [dict(row) for row in cur.fetchall()]
            if fetch_all and query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in cur.fetchall()]
            return cur.statusmessage

    def close(self) -> None:
        with self._lock:
            pool = self.connection_pool
            self.connection_pool = None
        if pool is not None:
            pool.closeall()
            logger.info("Database pool closed")


db_pool = DatabaseConnectionPool()
