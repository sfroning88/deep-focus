"""
Author: Sean Froning
Created Date: 6.3.2026
Process-local sync lazy singleton resource loader
"""

import threading
from typing import Callable, Optional


class SyncLazyResource[T]:
    """Thread-safe, run-once lazy singleton for sync resources"""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._value: Optional[T] = None
        self._lock = threading.Lock()

    @property
    def is_set(self) -> bool:
        """Whether the resource has been resolved"""
        return self._value is not None

    def get(self) -> T:
        """Resolve the resource, building it once on first access"""
        if self._value is None:
            with self._lock:
                if self._value is None:
                    self._value = self._factory()
        return self._value

    def pop(self) -> Optional[T]:
        """Atomically clear and return the resource for teardown"""
        with self._lock:
            value = self._value
            self._value = None
            return value

    def reset(self) -> None:
        """Drop the cached resource so the next access rebuilds it"""
        with self._lock:
            self._value = None
