"""
Author: Sean Froning
Created Date: 6.3.2026
Process-local async lazy singleton resource loader
"""

import asyncio
from typing import Awaitable, Callable, Optional


class AsyncLazyResource[T]:
    """Asyncio-safe, run-once lazy singleton for async resources"""

    def __init__(self, factory: Callable[[], Awaitable[T]]) -> None:
        self._factory = factory
        self._value: Optional[T] = None
        self._lock = asyncio.Lock()

    @property
    def is_set(self) -> bool:
        """Whether the resource has been resolved"""
        return self._value is not None

    async def get(self) -> T:
        """Resolve the resource, awaiting the factory once on first access"""
        if self._value is None:
            async with self._lock:
                if self._value is None:
                    self._value = await self._factory()
        return self._value

    async def pop(self) -> Optional[T]:
        """Atomically clear and return the resource for teardown"""
        async with self._lock:
            value = self._value
            self._value = None
            return value

    async def reset(self) -> None:
        """Drop the cached resource so the next access rebuilds it"""
        async with self._lock:
            self._value = None
