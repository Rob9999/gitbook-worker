#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
BUILD_DIR="$ROOT_DIR/build"

mkdir -p "$BUILD_DIR"
cd "$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR/.github:$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

python -m tools.emoji.scan_emojis \
  --sources content docs publish \
  --output "$BUILD_DIR/emoji-report.json" \
  --samples-output "$BUILD_DIR/emoji-samples.json"

python -m tools.emoji.scan_fonts \
  --sources assets docs content publish \
  --output "$BUILD_DIR/font-report.json"

python - <<'PY'
import json
from pathlib import Path

root = Path(".")
build = root / "build"
report = json.loads((build / "emoji-report.json").read_text(encoding="utf-8"))
samples = json.loads((build / "emoji-samples.json").read_text(encoding="utf-8"))
template = (root / "harness" / "emoji-harness.md").read_text(encoding="utf-8")

records = report.get("emojis", [])
lines = ["| Emoji | Codepoints | CLDR-Name | Vorkommen |", "| --- | --- | --- | --- |"]
for item in records:
    lines.append(
        f"| {item['emoji']} | {item['codepoints']} | {item['name']} | {item['count']} |"
    )
if len(lines) == 2:
    lines.append("| (keine) | – | – | 0 |")
inventory = "\n".join(lines)

sample_emojis = samples.get("samples", ["🙂", "🚀", "⚙"])
inline_snippet = samples.get("inline", "🙂 🚀 ⚙")
heading = f"Emoji-Überschrift {inline_snippet}"
list_line = " ".join(sample_emojis[:3])
alternate_line = " ".join(sample_emojis[3:6] or sample_emojis[:3])
blockquote = f"Zitat mit {inline_snippet}"
code = "-".join(sample_emojis[:2])
matrix = inline_snippet

content = template
content = content.replace("{{EMOJI_INVENTORY_TABLE}}", inventory)
content = content.replace("{{EMOJI_SAMPLE_INLINE}}", f"Im Fließtext: {inline_snippet}")
content = content.replace("{{EMOJI_SAMPLE_HEADING}}", heading)
content = content.replace("{{EMOJI_SAMPLE_LIST}}", f"Listenpunkt {list_line}")
content = content.replace(
    "{{EMOJI_SAMPLE_LIST_ALTERNATE}}", f"Weiterer Punkt {alternate_line}"
)
content = content.replace("{{EMOJI_SAMPLE_BLOCKQUOTE}}", blockquote)
content = content.replace("{{EMOJI_SAMPLE_CODE}}", code)
content = content.replace("{{EMOJI_SAMPLE_MATRIX}}", matrix)

(build / "emoji-harness.runtime.md").write_text(content, encoding="utf-8")
PY

pandoc "$BUILD_DIR/emoji-harness.runtime.md" \
  --standalone \
  --metadata title="Emoji Harness" \
  -o "$BUILD_DIR/emoji-harness.html"

python -m tools.emoji.inline_emojis \
  --in "$BUILD_DIR/emoji-harness.html" \
  --out "$BUILD_DIR/emoji-harness.emoji.html" \
  --css assets/emoji.css \
  --prefer twemoji \
  --coverage "$BUILD_DIR/emoji-inline-coverage-harness.json"

node .github/gitbook_worker/tools/html_to_pdf.js \
  "$BUILD_DIR/emoji-harness.emoji.html" \
  "$BUILD_DIR/emoji-harness.pdf"

pandoc publish/das-erda-buch.md \
  --standalone \
  --metadata title="Das ERDA Buch" \
  -o "$BUILD_DIR/erda-book.html"

python -m tools.emoji.inline_emojis \
  --in "$BUILD_DIR/erda-book.html" \
  --out "$BUILD_DIR/erda-book.emoji.html" \
  --css assets/emoji.css \
  --prefer twemoji \
  --coverage "$BUILD_DIR/emoji-inline-coverage.json"

node .github/gitbook_worker/tools/html_to_pdf.js \
  "$BUILD_DIR/erda-book.emoji.html" \
  "$BUILD_DIR/das-erda-buch.emoji.pdf"

pytest .github/gitbook_worker/tests \
  --maxfail=1 \
  --disable-warnings \
  -q \
  --cov=tools.emoji.emoji_utils \
  --cov=tools.emoji.scan_emojis \
  --cov=tools.emoji.scan_fonts \
  --cov=tools.emoji.inline_emojis \
  --cov=tools.emoji.report \
  --cov-report=term \
  --cov-report=json:"$BUILD_DIR/emoji-tools-coverage.json" \
  --cov-fail-under=90

python - <<'PY'
import json
from pathlib import Path

coverage_file = Path("build/emoji-inline-coverage.json")
if coverage_file.exists():
    data = json.loads(coverage_file.read_text(encoding="utf-8"))
    ratio = data.get("ratio", 0.0)
    if ratio < 0.90:
        raise SystemExit(f"Emoji-Inlining unter 0.90 ({ratio:.3f})")
else:
    raise SystemExit("emoji-inline-coverage.json fehlt")
PY

pattern=$'\x4e\x6f\x74\x6f'
if grep -R "$pattern" "$ROOT_DIR" \
  --exclude-dir=.git \
  --exclude-dir=.github \
  --exclude-dir=build \
  --quiet; then
  echo "Verbotene Font-Referenz im Repository gefunden" >&2
  exit 1
fi

if command -v fc-list >/dev/null 2>&1; then
  if fc-list | grep -i "$pattern" >/dev/null 2>&1; then
    echo "Verbotene Font-Referenz im Container gefunden" >&2
    exit 1
  fi
fi

python - <<'PY'
import json
from pathlib import Path

allowed = {"CC BY 4.0", "CC BY-SA 4.0"}
paths = [Path("assets"), Path("harness"), Path("docs")]
report = []
violations = []
for base in paths:
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            license_marker = None
            for line in text.splitlines()[:5]:
                if "License:" in line:
                    license_marker = line.split("License:", 1)[1].strip()
                    break
            if not license_marker:
                violations.append(f"Keine Lizenzangabe in {path}")
                continue
            if not any(lic in license_marker for lic in allowed):
                violations.append(f"Nicht-CC-Lizenz in {path}: {license_marker}")
            report.append({"path": str(path), "license": license_marker})
output = Path("build/license-asset-report.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
if violations:
    raise SystemExit("\n".join(violations))
PY

