from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import pytest
import requests

from gitbook_worker.core.application.ai_reference_check import (
    AI_REFERENCE_FAILURE_EXIT_CODE,
    RequestThrottle,
    RetryBackoffConfig,
    ThrottleConfig,
    exit_code_for_summary,
    parse_retry_after_header,
    redact_secrets,
    retry_delay_seconds,
    summarize_report,
)
from gitbook_worker.tools.quality import ai_references


def test_request_throttle_waits_between_calls() -> None:
    current_time = 100.0
    slept: list[float] = []

    def clock() -> float:
        return current_time

    def sleep(delay: float) -> None:
        nonlocal current_time
        slept.append(delay)
        current_time += delay

    throttle = RequestThrottle(
        ThrottleConfig(requests_per_minute=60),
        clock=clock,
        sleep=sleep,
        jitter=lambda _start, _end: 0.0,
    )

    assert throttle.wait() == 0.0
    assert throttle.wait() == pytest.approx(1.0)
    assert slept == [pytest.approx(1.0)]


def test_redact_secrets_masks_api_key() -> None:
    payload = {
        "model_config": {
            "api_key": "secret-value",
            "provider": "genai",
            "nested": {"token": "also-secret"},
        }
    }

    redacted = redact_secrets(payload)

    assert redacted["model_config"]["api_key"] == "<redacted>"
    assert redacted["model_config"]["nested"]["token"] == "<redacted>"
    assert redacted["model_config"]["provider"] == "genai"


def test_retry_after_header_accepts_seconds() -> None:
    assert parse_retry_after_header("7") == pytest.approx(7.0)


def test_retry_after_header_accepts_http_date() -> None:
    now = datetime(2026, 5, 5, 12, 0, tzinfo=timezone.utc)
    retry_at = format_datetime(now + timedelta(seconds=11), usegmt=True)

    assert parse_retry_after_header(retry_at, now=now) == pytest.approx(11.0)


def test_retry_delay_uses_header_before_exponential_backoff() -> None:
    config = RetryBackoffConfig(base_delay_seconds=2, max_delay_seconds=60)

    assert retry_delay_seconds(attempt=3, retry_after="9", config=config) == 9


def test_retry_delay_caps_exponential_backoff() -> None:
    config = RetryBackoffConfig(base_delay_seconds=2, max_delay_seconds=5)

    assert retry_delay_seconds(attempt=4, retry_after=None, config=config) == 5


def test_genai_url_uses_current_model() -> None:
    config = ai_references.ModelConfig(
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key="secret",
        provider="genai",
        model="gemini-2.5-flash",
    )

    assert ai_references._build_genai_url(config).endswith(
        "/models/gemini-2.5-flash:generateContent"
    )


def test_genai_provider_uses_gemini_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AI_REFERENCE_URL", raising=False)
    monkeypatch.delenv("AI_REFERENCE_MODEL", raising=False)
    args = ai_references.build_arg_parser().parse_args(
        ["--ai-provider", "genai", "--no-env-file"]
    )

    config = ai_references._resolve_model_config(args)

    assert config.base_url == "https://generativelanguage.googleapis.com/v1beta"
    assert config.model == "gemini-2.5-flash"


def test_provider_error_messages_are_redacted() -> None:
    config = ai_references.ModelConfig(
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key="secret-token",
        provider="genai",
        model="gemini-2.5-flash",
    )

    message = "403 for url: https://example.test?key=secret-token"

    assert "secret-token" not in ai_references._sanitize_error_message(message, config)


def test_call_model_waits_for_retry_after_on_429(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = ai_references.ReferenceTask(
        file=Path("refs.md"),
        title="Quelle",
        line="1. Quelle. https://example.com",
        lineno=1,
        numbering="1",
    )
    config = ai_references.ModelConfig(
        base_url="https://api.example.test/chat",
        api_key="secret-token",
        provider="openai",
        model="test-model",
        max_retries=1,
        retry_backoff_base_seconds=2,
        retry_backoff_max_seconds=60,
    )
    calls = 0
    slept: list[float] = []

    class FakeResponse:
        def __init__(
            self, status_code: int, payload: dict, headers: dict | None = None
        ):
            self.status_code = status_code
            self._payload = payload
            self.headers = headers or {}
            self.text = json.dumps(payload)

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError("rate limited", response=self)

        def json(self) -> dict:
            return self._payload

    def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        if calls == 1:
            return FakeResponse(429, {}, {"Retry-After": "6"})
        return FakeResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"success": true, "org": "x", "validation_date": "2026-05-05", "type": "external url"}'
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(ai_references.requests, "post", fake_post)
    monkeypatch.setattr(ai_references.time, "sleep", slept.append)

    result = ai_references.call_model(task, "Prompt", config)

    assert result.success is True
    assert calls == 2
    assert slept == [pytest.approx(6.0)]


def test_env_file_is_loaded_without_overriding_existing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AI_REFERENCE_PROVIDER=genai\nAI_REFERENCE_API_KEY=from-file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_REFERENCE_API_KEY", "already-set")
    monkeypatch.delenv("AI_REFERENCE_PROVIDER", raising=False)

    ai_references._load_env_file(env_file)

    assert ai_references.os.environ["AI_REFERENCE_PROVIDER"] == "genai"
    assert ai_references.os.environ["AI_REFERENCE_API_KEY"] == "already-set"


def _write_reference_file(tmp_path: Path) -> Path:
    markdown = tmp_path / "refs.md"
    markdown.write_text(
        "# Quellen-Test\n\n## Quellen\n\n1. Kaputte Quelle ohne URL\n",
        encoding="utf-8",
    )
    return markdown


def test_main_is_report_only_by_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = _write_reference_file(tmp_path)
    report_path = tmp_path / "report.json"

    def fake_call_model(task, prompt, config):  # type: ignore[no-untyped-def]
        return ai_references.ReferenceResult(
            task,
            True,
            {
                "success": True,
                "org": task.line,
                "new": "1. Reparierte Quelle. https://example.com/reference",
                "validation_date": "2026-05-04",
                "type": "external url",
            },
        )

    monkeypatch.setattr(ai_references, "call_model", fake_call_model)
    monkeypatch.setenv("AI_REFERENCE_API_KEY", "super-secret")

    exit_code = ai_references.main(
        [
            "--root",
            str(tmp_path),
            "--files",
            str(markdown),
            "--json-report",
            str(report_path),
            "--no-progress",
        ]
    )

    assert exit_code == 0
    assert "Kaputte Quelle" in markdown.read_text(encoding="utf-8")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["model_config"]["api_key"] == "<redacted>"
    assert report["results"][0]["action"] == "link_repaired"


def test_main_apply_writes_confirmed_fix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = _write_reference_file(tmp_path)

    def fake_call_model(task, prompt, config):  # type: ignore[no-untyped-def]
        return ai_references.ReferenceResult(
            task,
            True,
            {
                "success": True,
                "org": task.line,
                "new": "1. Reparierte Quelle. https://example.com/reference",
                "validation_date": "2026-05-04",
                "type": "external url",
            },
        )

    monkeypatch.setattr(ai_references, "call_model", fake_call_model)

    exit_code = ai_references.main(
        [
            "--root",
            str(tmp_path),
            "--files",
            str(markdown),
            "--apply",
            "--no-progress",
        ]
    )

    assert exit_code == 0
    assert "Reparierte Quelle" in markdown.read_text(encoding="utf-8")


def test_fail_on_failed_returns_dedicated_exit_code() -> None:
    summary = summarize_report([{"success": False}])

    assert (
        exit_code_for_summary(summary, fail_on_failed=True)
        == AI_REFERENCE_FAILURE_EXIT_CODE
    )
    assert exit_code_for_summary(summary, fail_on_failed=False) == 0
