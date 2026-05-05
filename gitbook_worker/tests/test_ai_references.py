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


def test_mistral_provider_uses_mistral_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AI_REFERENCE_URL", raising=False)
    monkeypatch.delenv("AI_REFERENCE_MODEL", raising=False)
    args = ai_references.build_arg_parser().parse_args(
        ["--ai-provider", "mistral", "--no-env-file"]
    )

    config = ai_references._resolve_model_config(args)

    assert config.base_url == "https://api.mistral.ai/v1/chat/completions"
    assert config.model == "mistral-small-latest"


def test_mistral_provider_uses_mistral_api_key_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AI_REFERENCE_API_KEY", raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "mistral-secret")
    args = ai_references.build_arg_parser().parse_args(
        ["--ai-provider", "mistral", "--no-env-file"]
    )

    config = ai_references._resolve_model_config(args)

    assert config.api_key == "mistral-secret"


def test_customer_env_aliases_are_used(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "AI_REFERENCE_API_KEY",
        "AI_REFERENCE_PROVIDER",
        "AI_REFERENCE_URL",
        "AI_API_KEY",
        "AI_PROVIDER",
        "AI_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AI_API_KEY", "alias-secret")
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_URL", "https://api.example.test/chat")
    args = ai_references.build_arg_parser().parse_args(["--no-env-file"])

    config = ai_references._resolve_model_config(args)

    assert config.api_key == "alias-secret"
    assert config.provider == "openai-compatible"
    assert config.base_url == "https://api.example.test/chat"


def test_customer_throttle_and_429_aliases_are_used() -> None:
    args = ai_references.build_arg_parser().parse_args(
        [
            "--delay-seconds",
            "3",
            "--jitter-seconds",
            "0.5",
            "--cooldown-on-429-seconds",
            "9",
            "--max-consecutive-429",
            "2",
            "--no-env-file",
        ]
    )

    throttle = ai_references._resolve_throttle_config(args)
    config = ai_references._resolve_model_config(args)

    assert throttle.min_interval_seconds == pytest.approx(3.0)
    assert throttle.jitter_seconds == pytest.approx(0.5)
    assert config.max_retries == 2
    assert config.retry_backoff_base_seconds == pytest.approx(9.0)
    assert config.retry_backoff_max_seconds == pytest.approx(9.0)


def test_build_prompt_uses_as_of_date_and_uncertainty_rule() -> None:
    task = ai_references.ReferenceTask(
        file=Path("refs.md"),
        title="Quelle",
        line="1. Quelle ohne Datum",
        lineno=1,
        numbering="1",
    )

    prompt = ai_references._build_prompt(
        task,
        "Proof and repair the reference",
        as_of_date="2026-05-05",
    )

    assert "Use validation_date exactly as 2026-05-05" in prompt
    assert '"validation_date": "2026-05-05"' in prompt
    assert "Do not invent access dates" in prompt
    assert "success=false" in prompt


def test_call_model_forces_as_of_date_in_response(
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
    )

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            content = (
                '{"success": true, "org": "x", '
                '"validation_date": "YYYY-MM-DD", "type": "external url"}'
            )
            return {"choices": [{"message": {"content": content}}]}

    monkeypatch.setattr(
        ai_references.requests, "post", lambda *args, **kwargs: FakeResponse()
    )

    result = ai_references.call_model(
        task,
        "Prompt",
        config,
        as_of_date="2026-05-05",
    )

    assert result.success is True
    assert isinstance(result.response, dict)
    assert result.response["validation_date"] == "2026-05-05"


def test_placeholder_validation_date_requires_manual_review() -> None:
    response = ai_references._normalize_reference_response(
        {"success": True, "validation_date": "YYYY-MM-DD", "type": "external url"},
        None,
    )

    assert response["success"] is False
    assert response["requires_manual_review"] is True
    assert response["reason"] == "placeholder_validation_date"


def test_inline_reference_extraction_merges_wrapped_bare_url(tmp_path: Path) -> None:
    markdown = tmp_path / "refs.md"
    markdown.write_text(
        "# Text\n\n[1] Quelle Titel\n<https://example.com/source>\n",
        encoding="utf-8",
    )

    tasks = ai_references.load_inline_reference_tasks([markdown])

    assert len(tasks) == 1
    assert tasks[0].lineno == 3
    assert tasks[0].numbering == "1"
    assert tasks[0].line == "[1] Quelle Titel <https://example.com/source>"


def test_markdown_links_are_optional_for_inline_reference_extraction(
    tmp_path: Path,
) -> None:
    markdown = tmp_path / "refs.md"
    markdown.write_text("Ein [Link](https://example.com/source).\n", encoding="utf-8")

    assert ai_references.load_inline_reference_tasks([markdown]) == []

    tasks = ai_references.load_inline_reference_tasks(
        [markdown], include_markdown_links=True
    )
    assert len(tasks) == 1
    assert tasks[0].title == "Markdown link: Link"


def test_frontmatter_dois_are_optional_for_inline_reference_extraction(
    tmp_path: Path,
) -> None:
    markdown = tmp_path / "refs.md"
    markdown.write_text(
        "---\ntitle: Test\ndoi: 10.1234/example.1\n---\n\n# Text\n",
        encoding="utf-8",
    )

    assert ai_references.load_inline_reference_tasks([markdown]) == []

    tasks = ai_references.load_inline_reference_tasks(
        [markdown], include_frontmatter_dois=True
    )
    assert len(tasks) == 1
    assert tasks[0].title == "Frontmatter DOI"


def test_deterministic_precheck_detects_doi_and_confidence(tmp_path: Path) -> None:
    task = ai_references.ReferenceTask(
        file=tmp_path / "refs.md",
        title="Quelle",
        line="Quelle https://doi.org/10.1234/example.1",
        lineno=1,
        numbering=None,
    )

    precheck = ai_references.deterministic_precheck(
        task, root=tmp_path, as_of_date="2026-05-05"
    )

    assert precheck["success"] is True
    assert precheck["type"] == "external reference"
    assert precheck["evidence_url_status"] == "doi_syntax_valid"
    assert precheck["confidence"] == 0.85


def test_files_list_and_resume_success_keys(tmp_path: Path) -> None:
    markdown = tmp_path / "refs.md"
    markdown.write_text("# Text\n", encoding="utf-8")
    files_list = tmp_path / "files.txt"
    files_list.write_text("# comment\nrefs.md\n", encoding="utf-8")
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "file": str(markdown),
                        "lineno": 7,
                        "orig": "Quelle",
                        "success": True,
                        "status": "validated",
                    },
                    {
                        "file": str(markdown),
                        "lineno": 8,
                        "orig": "Rate Limit",
                        "success": False,
                        "status": "rate_limited",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    assert ai_references.load_files_list(tmp_path, files_list) == [markdown.resolve()]
    keys = ai_references.load_resume_success_keys(report)
    assert (str(markdown.resolve()), 7, "Quelle") in keys
    assert (str(markdown.resolve()), 8, "Rate Limit") not in keys


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


def test_call_model_sends_mistral_chat_completion_request(
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
        base_url="https://api.mistral.ai/v1/chat/completions",
        api_key="mistral-secret",
        provider="mistral",
        model="mistral-small-latest",
    )
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"success": true, "org": "x", "validation_date": "2026-05-05", "type": "external url"}'
                        }
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):  # type: ignore[no-untyped-def]
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(ai_references.requests, "post", fake_post)

    result = ai_references.call_model(task, "Prompt", config)

    assert result.success is True
    assert captured["url"] == "https://api.mistral.ai/v1/chat/completions"
    assert captured["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "Bearer mistral-secret",
    }
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "mistral-small-latest"


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

    def fake_call_model(task, prompt, config, **kwargs):  # type: ignore[no-untyped-def]
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
    assert report["results"][0]["status"] == "suggested"
    assert report["results"][0]["action"] == "link_repair_suggested"


def test_main_precheck_only_skips_ai_calls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = tmp_path / "refs.md"
    markdown.write_text(
        "# Quellen-Test\n\n## Quellen\n\n1. Quelle. https://example.com/ref\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.json"

    def fail_call_model(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("AI call should not run in precheck-only mode")

    monkeypatch.setattr(ai_references, "call_model", fail_call_model)

    exit_code = ai_references.main(
        [
            "--root",
            str(tmp_path),
            "--files",
            str(markdown),
            "--precheck-only",
            "--json-report",
            str(report_path),
            "--as-of-date",
            "2026-05-05",
            "--no-progress",
        ]
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["as_of_date"] == "2026-05-05"
    assert report["results"][0]["status"] == "validated"
    assert report["results"][0]["evidence_url_status"] == "url_syntax_valid"


def test_main_apply_writes_confirmed_fix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = _write_reference_file(tmp_path)

    def fake_call_model(task, prompt, config, **kwargs):  # type: ignore[no-untyped-def]
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


def test_summary_distinguishes_suggested_and_rate_limited() -> None:
    summary = summarize_report(
        [
            {"success": True, "status": "suggested", "new": "x"},
            {"success": True, "status": "validated"},
            {"success": False, "status": "rate_limited", "rate_limited": True},
        ]
    )

    assert summary.repaired == 0
    assert summary.suggested == 1
    assert summary.validated == 1
    assert summary.rate_limited == 1
    assert summary.failed == 0
    assert (
        exit_code_for_summary(summary, fail_on_failed=True)
        == AI_REFERENCE_FAILURE_EXIT_CODE
    )
