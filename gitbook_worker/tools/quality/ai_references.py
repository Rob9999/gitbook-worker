"""AI-assisted reference validation and repair helpers.

The module exposes three core primitives that can be re-used by GitHub
Actions, bespoke scripts, or the bundled CLI:

* :func:`load_reference_tasks` parses Markdown files and extracts reference
  entries that should be validated.
* :func:`call_model` sends a single reference prompt to the configured AI
  backend and returns the parsed response.
* :func:`apply_fixes` updates Markdown files with validated references and
  builds a structured report that can be written to disk.

Running ``python -m gitbook_worker.tools.quality.ai_references`` provides a thin CLI wrapper
around those functions.  It discovers Markdown files via ``SUMMARY.md`` and the
publish manifest, resolves credentials from the environment, and writes a JSON
report that GitHub Actions can surface as annotations.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Sequence

import requests
import tqdm

from gitbook_worker.core.application.ai_reference_check import (
    AI_REFERENCE_FAILURE_EXIT_CODE,
    REDACTED_SECRET,
    RequestThrottle,
    RetryBackoffConfig,
    ThrottleConfig,
    exit_code_for_summary,
    redact_secrets,
    retry_delay_seconds,
    summarize_report,
)
from gitbook_worker.tools.exit_codes import add_exit_code_help, handle_exit_code_help
from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.publishing.gitbook_style import (
    SummaryContext,
    get_summary_layout,
)
from gitbook_worker.tools.quality.sources import extract_sources

LOGGER = get_logger(__name__)

_JSON_BLOCK_RE = re.compile(r"```json\s*(?P<body>.*?)```", re.DOTALL)
_SUMMARY_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]*)?\)")
_SECRET_QUERY_RE = re.compile(r"([?&](?:key|api_key)=)[^&\s]+", re.IGNORECASE)

DEFAULT_PROMPT = "Proof and repair the reference"
DEFAULT_MODEL = "gpt-4"
DEFAULT_GENAI_MODEL = "gemini-2.5-flash"
DEFAULT_PROVIDER = "openai"
DEFAULT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_BASE = 2.0
DEFAULT_RETRY_BACKOFF_MAX = 120.0
DEFAULT_RETRY_BACKOFF_JITTER = 0.0

ENV_URL = "AI_REFERENCE_URL"
ENV_API_KEY = "AI_REFERENCE_API_KEY"
ENV_PROVIDER = "AI_REFERENCE_PROVIDER"
ENV_MODEL = "AI_REFERENCE_MODEL"
ENV_TEMPERATURE = "AI_REFERENCE_TEMPERATURE"
ENV_REQUESTS_PER_MINUTE = "AI_REFERENCE_REQUESTS_PER_MINUTE"
ENV_MIN_REQUEST_INTERVAL = "AI_REFERENCE_MIN_REQUEST_INTERVAL"
ENV_THROTTLE_JITTER = "AI_REFERENCE_THROTTLE_JITTER"
ENV_RETRY_BACKOFF_BASE = "AI_REFERENCE_RETRY_BACKOFF_BASE"
ENV_RETRY_BACKOFF_MAX = "AI_REFERENCE_RETRY_BACKOFF_MAX"
ENV_RETRY_BACKOFF_JITTER = "AI_REFERENCE_RETRY_BACKOFF_JITTER"


@dataclass(frozen=True)
class ReferenceTask:
    """Single reference entry extracted from a Markdown file."""

    file: Path
    title: str
    line: str
    lineno: int
    numbering: Optional[str]

    @property
    def footnote_index(self) -> Optional[int]:
        """Return the numeric index derived from ``numbering`` if available."""

        if not self.numbering:
            return None
        cleaned = self.numbering.strip()
        if cleaned.isdigit():
            return int(cleaned)
        match = re.match(r"(\d+)", cleaned)
        if match:
            return int(match.group(1))
        return None


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for the AI backend."""

    base_url: str
    api_key: Optional[str]
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff_base_seconds: float = DEFAULT_RETRY_BACKOFF_BASE
    retry_backoff_max_seconds: float = DEFAULT_RETRY_BACKOFF_MAX
    retry_backoff_jitter_seconds: float = DEFAULT_RETRY_BACKOFF_JITTER


@dataclass
class ReferenceResult:
    """Result of validating a single reference."""

    task: ReferenceTask
    success: bool
    response: Mapping[str, Any] | str | None
    error: Optional[str] = None

    def to_report_entry(self) -> Mapping[str, Any]:
        """Return a serialisable report entry."""

        data: MutableMapping[str, Any] = {
            "file": str(self.task.file),
            "lineno": self.task.lineno,
            "orig": self.task.line,
            "title": self.task.title,
        }
        if isinstance(self.response, Mapping):
            data.update(self.response)
        if self.error:
            data["error"] = self.error
        data["success"] = bool(data.get("success")) and self.success
        if data["success"] and data.get("new"):
            data["action"] = "link_repaired"
        elif data["success"]:
            data["action"] = "link_check_succeeded"
        else:
            data["action"] = "link_repair_failed"
        return data


def _discover_summary(context: SummaryContext) -> Path:
    summary = context.summary_path
    if not summary.exists():
        raise FileNotFoundError(f"SUMMARY.md not found at {summary}")
    return summary


def _extract_markdown_from_summary(summary: Path) -> List[Path]:
    text = summary.read_text(encoding="utf-8")
    candidates: set[Path] = set()
    for raw in _SUMMARY_LINK_RE.findall(text):
        cleaned = raw.strip()
        if not cleaned:
            continue
        normalised = cleaned.replace("\\", "/")
        if normalised.startswith("./"):
            normalised = normalised[2:]
        candidate = (summary.parent / normalised).resolve()
        if candidate.suffix.lower() != ".md":
            continue
        if candidate.exists():
            candidates.add(candidate)
        else:
            LOGGER.debug("Skipping missing summary entry: %s", candidate)
    return sorted(candidates)


def _resolve_manifest_roots(manifest: Optional[Path]) -> List[Path]:
    if manifest is None:
        return []
    try:
        from gitbook_worker.tools.publishing.publisher import get_publish_list
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Cannot import publishing helpers: %s", exc)
        return []

    try:
        entries = get_publish_list(str(manifest))
    except Exception as exc:  # pragma: no cover - manifest parsing failures
        LOGGER.warning("Failed to parse publish manifest %s: %s", manifest, exc)
        return []

    roots: List[Path] = []
    for entry in entries:
        raw_path = entry.get("path")
        if not raw_path:
            continue
        candidate = (manifest.parent / raw_path).resolve()
        roots.append(candidate)
    return roots


def _filter_files_by_roots(files: Iterable[Path], roots: List[Path]) -> List[Path]:
    if not roots:
        return sorted(set(files))
    filtered: set[Path] = set()
    for file in files:
        for root in roots:
            try:
                file.relative_to(root)
            except ValueError:
                continue
            filtered.add(file)
            break
    return sorted(filtered)


def discover_markdown_files(
    *,
    root: Path,
    manifest: Optional[Path] = None,
    summary: Optional[Path] = None,
    explicit_files: Optional[Sequence[Path]] = None,
) -> List[Path]:
    """Return Markdown files that should be inspected for references."""

    if explicit_files:
        files = [
            file if file.is_absolute() else (root / file).resolve()
            for file in explicit_files
        ]
        return sorted(
            {file for file in files if file.exists() and file.suffix.lower() == ".md"}
        )

    if summary is not None:
        summary_path = summary
    else:
        context = get_summary_layout(root)
        summary_path = _discover_summary(context)
    files = _extract_markdown_from_summary(summary_path)
    roots = _resolve_manifest_roots(manifest)
    filtered = _filter_files_by_roots(files, roots)
    if not filtered:
        LOGGER.info("No Markdown files matched the manifest filters; using summary set")
        return files
    return filtered


def load_reference_tasks(
    md_files: Iterable[Path],
    *,
    language: str = "de",
    max_level: int = 6,
) -> List[ReferenceTask]:
    """Extract reference entries from ``md_files``.

    Returns a list of :class:`ReferenceTask` instances that the caller can feed
    into :func:`call_model`.
    """

    extracted = extract_sources(md_files, language=language, max_level=max_level)
    tasks: List[ReferenceTask] = []
    for file_name, entries in extracted.items():
        path = Path(file_name)
        for entry in entries:
            for title, metadata in entry.items():
                if not metadata:
                    continue
                line = str(metadata.get("line") or "").strip()
                if not line:
                    continue
                numbering = metadata.get("numbering")
                if isinstance(numbering, str):
                    numbering_value: Optional[str] = numbering
                else:
                    numbering_value = str(numbering) if numbering else None
                tasks.append(
                    ReferenceTask(
                        file=path,
                        title=title,
                        line=line,
                        lineno=int(metadata.get("lineno", 0) or 0),
                        numbering=numbering_value,
                    )
                )
    return tasks


def _extract_json_from_text(generated_text: str) -> tuple[bool, Any]:
    text = (generated_text or "").strip()
    if not text:
        return False, generated_text

    block = _JSON_BLOCK_RE.search(text)
    if block:
        text = block.group("body").strip()

    if text.startswith("```json"):
        text = text[7:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    text = text.strip().strip("'").strip('"')

    try:
        return True, json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        unescaped = ast.literal_eval(text)
        unescaped = ast.literal_eval(unescaped)
        return True, json.loads(unescaped)
    except Exception:
        LOGGER.warning("JSON parsing failed for AI response. Returning raw text.")
        return False, generated_text


def _build_prompt(task: ReferenceTask, base_prompt: str) -> str:
    json_hint = """
{
    "success": true|false,
    "org": "<Originalquelle>",
    "new": "<neue Zitationszeile oder null>",
    "error": "<Fehlermeldung oder null>",
    "hint": "<Hinweis oder null>",
    "validation_date": "YYYY-MM-DD",
    "type": "internal reference" | "external url" | "external reference" | "?"
}
    """.strip()

    index = task.footnote_index
    reference_label = f"Quelle [{index}]" if index is not None else "Quelle"
    return (
        f"{base_prompt}\n\n"
        f"{reference_label}: {task.line}\n\n"
        f"Generate a structured JSON according to:\n{json_hint}"
    )


def call_model(
    task: ReferenceTask, prompt: str, config: ModelConfig
) -> ReferenceResult:
    """Send ``task`` to the configured AI backend and return the response."""

    provider = (config.provider or DEFAULT_PROVIDER).lower()
    prompt_text = _build_prompt(task, prompt)
    headers = {"Content-Type": "application/json"}
    if config.api_key and provider not in {"genai", "google-genai"}:
        headers["Authorization"] = f"Bearer {config.api_key}"

    for attempt in range(config.max_retries + 1):
        try:
            if provider in {"openai", "openai-compatible", "azure-openai"}:
                payload = {
                    "model": config.model or DEFAULT_MODEL,
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": config.temperature,
                }
                response = requests.post(
                    config.base_url or DEFAULT_URL,
                    headers=headers,
                    json=payload,
                    timeout=config.timeout,
                )
                response.raise_for_status()
                data = response.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                parsed_ok, parsed = _extract_json_from_text(content)
                if not parsed_ok:
                    return ReferenceResult(
                        task, False, parsed, "AI response did not return JSON"
                    )
                return ReferenceResult(task, True, parsed)

            if provider in {"genai", "google-genai"}:
                payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                url = _build_genai_url(config)
                if config.api_key:
                    connector = "&" if "?" in url else "?"
                    url = f"{url}{connector}key={config.api_key}"
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=config.timeout,
                )
                response.raise_for_status()
                data = response.json()
                generated = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                parsed_ok, parsed = _extract_json_from_text(generated)
                if not parsed_ok:
                    return ReferenceResult(
                        task, False, parsed, "AI response did not return JSON"
                    )
                return ReferenceResult(task, True, parsed)

            payload = {
                "prompt": prompt_text,
                "model": config.model,
                "temperature": config.temperature,
            }
            response = requests.post(
                config.base_url,
                headers=headers,
                json=payload,
                timeout=config.timeout,
            )
            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                return ReferenceResult(
                    task, False, response.text, f"Invalid JSON response: {exc}"
                )

            if isinstance(data, Mapping):
                if {"success", "org", "validation_date", "type"} <= set(data):
                    return ReferenceResult(task, True, data)
                content = (
                    data.get("content")
                    if isinstance(data.get("content"), str)
                    else None
                )
                if content:
                    parsed_ok, parsed = _extract_json_from_text(content)
                    if parsed_ok:
                        return ReferenceResult(task, True, parsed)
                    return ReferenceResult(
                        task, False, parsed, "AI content missing JSON"
                    )
            return ReferenceResult(task, False, data, "Unsupported response format")

        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else None
            if status == 429 and attempt < config.max_retries:
                retry_after = (
                    exc.response.headers.get("Retry-After")
                    if exc.response is not None
                    else None
                )
                wait_time = retry_delay_seconds(
                    attempt=attempt,
                    retry_after=retry_after,
                    config=_retry_backoff_config(config),
                )
                source = "Retry-After" if retry_after else "exponential backoff"
                LOGGER.warning(
                    "Rate limited by provider – retrying in %.2f seconds (%s)",
                    wait_time,
                    source,
                )
                time.sleep(wait_time)
                continue
            return ReferenceResult(
                task,
                False,
                None,
                _sanitize_error_message(f"HTTP error: {exc}", config),
            )
        except requests.RequestException as exc:
            if attempt < config.max_retries:
                wait_time = random.randint(1, 5)
                LOGGER.warning(
                    "Request failed (%s), retrying in %s seconds", exc, wait_time
                )
                time.sleep(wait_time)
                continue
            return ReferenceResult(
                task,
                False,
                None,
                _sanitize_error_message(f"Request error: {exc}", config),
            )
    return ReferenceResult(task, False, None, "Maximum retries exceeded")


def _build_genai_url(config: ModelConfig) -> str:
    """Return a Gemini generateContent URL from a base URL or full endpoint."""

    base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta"
    if ":generateContent" in base_url:
        return base_url

    clean = base_url.rstrip("/")
    model = config.model or DEFAULT_GENAI_MODEL
    if clean.endswith("/models"):
        return f"{clean}/{model}:generateContent"
    if "/models/" in clean:
        return f"{clean}:generateContent"
    return f"{clean}/models/{model}:generateContent"


def _sanitize_error_message(message: str, config: ModelConfig) -> str:
    """Remove provider secrets from error strings before logging/reporting."""

    sanitized = _SECRET_QUERY_RE.sub(rf"\1{REDACTED_SECRET}", message)
    if config.api_key:
        sanitized = sanitized.replace(config.api_key, REDACTED_SECRET)
    return sanitized


def _retry_backoff_config(config: ModelConfig) -> RetryBackoffConfig:
    return RetryBackoffConfig(
        base_delay_seconds=config.retry_backoff_base_seconds,
        max_delay_seconds=config.retry_backoff_max_seconds,
        jitter_seconds=config.retry_backoff_jitter_seconds,
    )


def apply_fixes(
    results: Iterable[ReferenceResult],
    *,
    write_changes: bool = True,
) -> List[Mapping[str, Any]]:
    """Apply successful fixes to disk and return a structured report."""

    grouped: MutableMapping[Path, List[tuple[int, str, str]]] = {}
    report: List[Mapping[str, Any]] = []

    for result in results:
        report_entry = result.to_report_entry()
        report.append(report_entry)

        if not result.success or not isinstance(result.response, Mapping):
            continue

        if not result.response.get("success"):
            continue

        new_value = result.response.get("new")
        if not new_value:
            continue

        grouped.setdefault(result.task.file, []).append(
            (result.task.lineno, result.task.line, str(new_value))
        )

    for file, replacements in grouped.items():
        if not file.exists():
            LOGGER.warning("Cannot update missing file: %s", file)
            continue
        try:
            lines = file.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            LOGGER.warning("Failed to read %s: %s", file, exc)
            continue

        changed = False
        for lineno, old, new in replacements:
            index = max(lineno - 1, 0)
            if index >= len(lines):
                LOGGER.warning("Line %s out of range for %s", lineno, file)
                continue
            original = lines[index]
            updated = original.replace(old, new)
            if original == updated:
                LOGGER.warning("Reference not found on line %s in %s", lineno, file)
                continue
            lines[index] = updated
            changed = True
            if write_changes:
                LOGGER.info("Repaired reference in %s (line %s)", file, lineno)
            else:
                LOGGER.info("Prepared reference repair in %s (line %s)", file, lineno)

        if changed and write_changes:
            try:
                file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            except OSError as exc:
                LOGGER.warning("Failed to write %s: %s", file, exc)

    return report


def _parse_float(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _resolve_model_config(args: argparse.Namespace) -> ModelConfig:
    provider = args.ai_provider or os.getenv(ENV_PROVIDER) or DEFAULT_PROVIDER
    provider_normalized = provider.lower()
    raw_base_url = args.ai_url or os.getenv(ENV_URL)
    if raw_base_url:
        base_url = raw_base_url
    elif provider_normalized in {"genai", "google-genai"}:
        base_url = "https://generativelanguage.googleapis.com/v1beta"
    else:
        base_url = DEFAULT_URL
    api_key = args.ai_api_key or os.getenv(ENV_API_KEY)
    if not api_key and provider_normalized in {"genai", "google-genai"}:
        api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GENAI_API_KEY")
            or os.getenv("GOOGLE_GENAI_API_KEY")
        )
    model = args.model or os.getenv(ENV_MODEL)
    if model is None:
        model = (
            DEFAULT_GENAI_MODEL
            if provider_normalized in {"genai", "google-genai"}
            else DEFAULT_MODEL
        )
    temperature_env = os.getenv(ENV_TEMPERATURE)
    temperature = (
        args.temperature
        if args.temperature is not None
        else _parse_float(temperature_env, DEFAULT_TEMPERATURE)
    )
    timeout = args.timeout if args.timeout is not None else DEFAULT_TIMEOUT
    max_retries = (
        args.max_retries if args.max_retries is not None else DEFAULT_MAX_RETRIES
    )
    retry_backoff_base = (
        args.retry_backoff_base
        if args.retry_backoff_base is not None
        else _parse_float(os.getenv(ENV_RETRY_BACKOFF_BASE), DEFAULT_RETRY_BACKOFF_BASE)
    )
    retry_backoff_max = (
        args.retry_backoff_max
        if args.retry_backoff_max is not None
        else _parse_float(os.getenv(ENV_RETRY_BACKOFF_MAX), DEFAULT_RETRY_BACKOFF_MAX)
    )
    retry_backoff_jitter = (
        args.retry_backoff_jitter
        if args.retry_backoff_jitter is not None
        else _parse_float(
            os.getenv(ENV_RETRY_BACKOFF_JITTER), DEFAULT_RETRY_BACKOFF_JITTER
        )
    )
    return ModelConfig(
        base_url=base_url,
        api_key=api_key,
        provider=provider,
        model=model,
        temperature=temperature,
        timeout=timeout,
        max_retries=max_retries,
        retry_backoff_base_seconds=retry_backoff_base,
        retry_backoff_max_seconds=retry_backoff_max,
        retry_backoff_jitter_seconds=retry_backoff_jitter,
    )


def _resolve_throttle_config(args: argparse.Namespace) -> ThrottleConfig:
    requests_per_minute = (
        args.requests_per_minute
        if args.requests_per_minute is not None
        else _parse_float(os.getenv(ENV_REQUESTS_PER_MINUTE), 0.0)
    )
    min_interval = (
        args.min_request_interval
        if args.min_request_interval is not None
        else _parse_float(os.getenv(ENV_MIN_REQUEST_INTERVAL), 0.0)
    )
    jitter = (
        args.throttle_jitter
        if args.throttle_jitter is not None
        else _parse_float(os.getenv(ENV_THROTTLE_JITTER), 0.0)
    )
    return ThrottleConfig(
        requests_per_minute=requests_per_minute or None,
        min_interval_seconds=min_interval,
        jitter_seconds=jitter,
    )


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs from ``path`` without overriding env vars."""

    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        LOGGER.warning("Failed to read env file %s: %s", path, exc)
        return

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _write_json_report(
    report: List[Mapping[str, Any]],
    destination: Path,
    *,
    prompt: str,
    config: ModelConfig,
    throttle: ThrottleConfig,
    files: Sequence[Path],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "model_config": redact_secrets(asdict(config)),
        "throttle": asdict(throttle),
        "files": [str(path) for path in files],
        "results": report,
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    LOGGER.info("JSON report written to %s", destination)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-assisted reference repair")
    add_exit_code_help(parser)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--manifest", type=Path, help="Path to publish.yml")
    parser.add_argument("--summary", type=Path, help="Path to SUMMARY.md")
    parser.add_argument(
        "--files", type=Path, nargs="*", help="Explicit Markdown files to process"
    )
    parser.add_argument(
        "--language", default="de", help="Source section language (default: de)"
    )
    parser.add_argument(
        "--max-level",
        type=int,
        default=6,
        help="Maximum heading level to inspect for sources",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Base prompt for the AI service"
    )
    parser.add_argument(
        "--env-file", type=Path, help="Load API settings from this .env file"
    )
    parser.add_argument(
        "--no-env-file", action="store_true", help="Do not auto-load <root>/.env"
    )
    parser.add_argument("--ai-url", dest="ai_url", help="AI endpoint URL")
    parser.add_argument(
        "--ai-api-key", dest="ai_api_key", help="API key for the AI provider"
    )
    parser.add_argument(
        "--ai-provider", dest="ai_provider", help="AI provider identifier"
    )
    parser.add_argument("--model", help="Model name to request from the provider")
    parser.add_argument("--temperature", type=float, help="Sampling temperature")
    parser.add_argument("--timeout", type=float, help="Request timeout in seconds")
    parser.add_argument(
        "--max-retries", type=int, help="Maximum number of retries for rate limits"
    )
    parser.add_argument(
        "--retry-backoff-base",
        type=float,
        help="Base seconds for exponential retry backoff when no Retry-After header is sent",
    )
    parser.add_argument(
        "--retry-backoff-max",
        type=float,
        help="Maximum seconds to wait for provider retry backoff",
    )
    parser.add_argument(
        "--retry-backoff-jitter",
        type=float,
        help="Additional random jitter in seconds for retry backoff",
    )
    parser.add_argument(
        "--requests-per-minute", type=float, help="Throttle provider calls to this rate"
    )
    parser.add_argument(
        "--min-request-interval",
        type=float,
        help="Minimum seconds between provider calls",
    )
    parser.add_argument(
        "--throttle-jitter", type=float, help="Additional random jitter in seconds"
    )
    parser.add_argument(
        "--json-report", type=Path, help="Write a JSON report to this path"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply accepted AI fixes to Markdown files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Deprecated alias for report-only mode"
    )
    parser.add_argument(
        "--fail-on-failed",
        action="store_true",
        help=f"Exit with {AI_REFERENCE_FAILURE_EXIT_CODE} when at least one reference fails",
    )
    parser.add_argument(
        "--no-progress", action="store_true", help="Disable progress bar output"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    handle_exit_code_help(args, component="ai_references")

    root = args.root.resolve()
    manifest = args.manifest.resolve() if args.manifest else None
    summary = args.summary.resolve() if args.summary else None

    if not args.no_env_file:
        env_file = args.env_file.resolve() if args.env_file else root / ".env"
        _load_env_file(env_file)

    files = discover_markdown_files(
        root=root,
        manifest=manifest,
        summary=summary,
        explicit_files=args.files,
    )
    if not files:
        LOGGER.info("No Markdown files discovered – exiting")
        return 0

    tasks = load_reference_tasks(
        files, language=args.language, max_level=args.max_level
    )
    if not tasks:
        LOGGER.info("No reference entries found in the selected files")
        return 0

    config = _resolve_model_config(args)
    throttle_config = _resolve_throttle_config(args)
    throttle = RequestThrottle(throttle_config)
    if not config.api_key and config.provider not in {
        "local",
        "custom",
        "genai",
        "google-genai",
    }:
        LOGGER.warning(
            "No API key provided – requests may fail depending on the provider"
        )

    results: List[ReferenceResult] = []
    progress = not args.no_progress
    iterator = tqdm.tqdm(tasks, desc="References", unit="ref", disable=not progress)
    for task in iterator:
        throttle.wait()
        result = call_model(task, args.prompt, config)
        results.append(result)
        if result.error:
            LOGGER.warning(
                "AI validation failed for %s:%s – %s",
                task.file,
                task.lineno,
                result.error,
            )

    write_changes = bool(args.apply and not args.dry_run)
    report = apply_fixes(results, write_changes=write_changes)

    if args.json_report:
        _write_json_report(
            report,
            args.json_report.resolve(),
            prompt=args.prompt,
            config=config,
            throttle=throttle_config,
            files=files,
        )

    summary_counts = summarize_report(report)
    LOGGER.info(
        "AI reference check finished – %s repaired, %s validated, %s failed",
        summary_counts.repaired,
        summary_counts.validated,
        summary_counts.failed,
    )
    return exit_code_for_summary(summary_counts, fail_on_failed=args.fail_on_failed)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
