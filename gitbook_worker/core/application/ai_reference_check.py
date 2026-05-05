"""Application policies for AI-assisted reference checks.

The quality CLI stays responsible for IO and provider calls. This module keeps
cross-cutting runtime policies in the application layer so they can be tested
without network access or Markdown fixtures.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Mapping, MutableMapping, Sequence

AI_REFERENCE_FAILURE_EXIT_CODE = 44
REDACTED_SECRET = "<redacted>"

_SECRET_FIELD_NAMES = {
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
}


@dataclass(frozen=True)
class ThrottleConfig:
    """Rate limiting policy for outbound AI provider calls."""

    requests_per_minute: float | None = None
    min_interval_seconds: float = 0.0
    jitter_seconds: float = 0.0

    @property
    def interval_seconds(self) -> float:
        """Return the effective minimum interval between two requests."""

        intervals = [max(self.min_interval_seconds, 0.0)]
        if self.requests_per_minute and self.requests_per_minute > 0:
            intervals.append(60.0 / self.requests_per_minute)
        return max(intervals)


class RequestThrottle:
    """Small deterministic throttle with injectable clock/sleep for tests."""

    def __init__(
        self,
        config: ThrottleConfig,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self._config = config
        self._clock = clock
        self._sleep = sleep
        self._jitter = jitter
        self._last_request_at: float | None = None

    def wait(self) -> float:
        """Wait if needed and return the delay applied in seconds."""

        interval = self._config.interval_seconds
        delay = 0.0
        now = self._clock()

        if interval > 0 and self._last_request_at is not None:
            elapsed = now - self._last_request_at
            delay = max(0.0, interval - elapsed)
            if delay > 0 and self._config.jitter_seconds > 0:
                delay += self._jitter(0.0, self._config.jitter_seconds)
            if delay > 0:
                self._sleep(delay)
                now = self._clock()

        self._last_request_at = now
        return delay


@dataclass(frozen=True)
class RetryBackoffConfig:
    """Retry delay policy for provider rate limits and transient errors."""

    base_delay_seconds: float = 2.0
    max_delay_seconds: float = 120.0
    jitter_seconds: float = 0.0


def parse_retry_after_header(
    value: str | None,
    *,
    now: datetime | None = None,
) -> float | None:
    """Parse a Retry-After header as seconds or HTTP-date."""

    if not value:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    try:
        seconds = float(cleaned)
    except ValueError:
        seconds = None
    if seconds is not None:
        return max(0.0, seconds)

    try:
        retry_at = parsedate_to_datetime(cleaned)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return max(0.0, (retry_at - reference).total_seconds())


def retry_delay_seconds(
    *,
    attempt: int,
    retry_after: str | None,
    config: RetryBackoffConfig,
    now: datetime | None = None,
    jitter: Callable[[float, float], float] = random.uniform,
) -> float:
    """Return the next retry delay, preferring provider Retry-After hints."""

    provider_delay = parse_retry_after_header(retry_after, now=now)
    if provider_delay is None:
        delay = max(config.base_delay_seconds, 0.0) * (2 ** max(attempt, 0))
    else:
        delay = provider_delay

    capped = min(max(delay, 0.0), max(config.max_delay_seconds, 0.0))
    if capped > 0 and config.jitter_seconds > 0:
        capped += jitter(0.0, config.jitter_seconds)
    return capped


def _is_secret_field(name: str) -> bool:
    lowered = name.lower()
    return lowered in _SECRET_FIELD_NAMES or lowered.endswith("_api_key")


def redact_secrets(value: Any) -> Any:
    """Return ``value`` with secret-looking mapping fields redacted."""

    if isinstance(value, Mapping):
        redacted: MutableMapping[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _is_secret_field(key_text):
                redacted[key_text] = REDACTED_SECRET if item else None
            else:
                redacted[key_text] = redact_secrets(item)
        return dict(redacted)
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item) for item in value)
    return value


@dataclass(frozen=True)
class ReferenceReportSummary:
    """Aggregate counts for an AI reference check report."""

    repaired: int
    validated: int
    failed: int

    @property
    def total(self) -> int:
        return self.repaired + self.validated + self.failed


def summarize_report(report: Sequence[Mapping[str, Any]]) -> ReferenceReportSummary:
    """Return stable counts for report entries."""

    repaired = sum(1 for entry in report if entry.get("success") and entry.get("new"))
    validated = sum(
        1 for entry in report if entry.get("success") and not entry.get("new")
    )
    failed = sum(1 for entry in report if not entry.get("success"))
    return ReferenceReportSummary(repaired=repaired, validated=validated, failed=failed)


def exit_code_for_summary(
    summary: ReferenceReportSummary,
    *,
    fail_on_failed: bool,
) -> int:
    """Return the process exit code implied by the selected failure policy."""

    if fail_on_failed and summary.failed > 0:
        return AI_REFERENCE_FAILURE_EXIT_CODE
    return 0
