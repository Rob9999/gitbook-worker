---
version: 1.0.0
date: 2025-11-29
history:
  - 2025-11-29: Initial sprintable task stack for the ERDA font family backlog.
---

# ERDA Font Stack – Sprintable Task Stack

This list captures the immediate localization-driven work for the ERDA CC-BY font family. Each task is structured to be sprint-ready (clear scope, sample material, acceptance hints) and sized for the font team backlog.

## Task Board

| ID | Locale / Scope | Description | Sample / Acceptance | Owner | Status |
|----|----------------|-------------|---------------------|-------|--------|
| FNT-001 | zh (Chinese) | Ensure sampled paragraph renders without fallback boxes or spacing drift in the new combined font stack. | `�测�����一个��的日�，数���，有�于持����同�的��。` | font-squad | TODO |
| FNT-002 | ja (Japanese) | Validate Kana + Kanji mix spacing and kerning for the provided operational log line; update glyph metrics if clipping appears. | `��チームは��かな一日を��し、��したデータが����を容�にすると��ました。` | font-squad | TODO |
| FNT-003 | ko (Korean) | Rebuild Hangul subset to support the status message and confirm consistent stroke weight at 12–16 pt. | `�� �은 ���이 고르게 유지된 차�한 하�를 기록하여 주� ��가 수�해�다고 보고�습니다.` | font-squad | TODO |
| FNT-004 | hi (Hindi) | Add/adjust Devanagari ligatures so that this sentence renders without stacked-matra overlap in PDF exports. | `टीम न� एक श�ंत दिन दर्ज किय � जह�� म�न स्थिर रह � �र स�प्त �हिक त�लन� सर�ल ह� गई�` | indic-taskforce | TODO |
| FNT-005 | am (Amharic) | Extend Ethiopic coverage to include the daily report text and verify baseline alignment vs. Latin fallback. | `��� ������ ����� �� ����� �� ������ ���� ������� ������� ��� �������� ����` | ethiopic-taskforce | TODO |
| FNT-006 | Repo housekeeping | Rename `.github/fonts/erda-ccby-cjk` to `.github/fonts/erda-ccby-fonts`, update all import/path references, and adjust documentation/tests accordingly. | Directory renamed, pipelines/tests green, docs updated. | tooling-team | TODO |

## Notes
- The provided locale snippets are intentionally copied verbatim (encoding artefacts included) to mirror the current upstream data; do not “fix” them until the glyph layer has been verified.
- Complete the rename task (FNT-006) before cutting the next release tag so downstream consumers can switch to the new neutral package name.
- Update this stack as soon as a task moves to “In Progress” or “Done” to keep the sprint board trustworthy.
