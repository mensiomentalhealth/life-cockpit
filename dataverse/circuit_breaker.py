#!/usr/bin/env python3
"""
Circuit Breaker for Dataverse calls
"""
from __future__ import annotations

import time
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

import httpx
import structlog


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_s: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_s)
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self.logger = structlog.get_logger(__name__)

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            now = datetime.now()
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and now - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.logger.info("dv_circuit_half_open")
                else:
                    raise httpx.TransportError("Circuit OPEN - failing fast")

            try:
                result = fn(*args, **kwargs)
                self._on_success()
                return result
            except httpx.HTTPError as exc:
                self._on_failure()
                raise

        return wrapper

    def _on_success(self) -> None:
        if self.state != CircuitState.CLOSED:
            self.logger.info("dv_circuit_closed")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.logger.warning("dv_circuit_open", failures=self.failure_count)
            self.state = CircuitState.OPEN


# Singleton breaker for Dataverse
dataverse_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout_s=30)


