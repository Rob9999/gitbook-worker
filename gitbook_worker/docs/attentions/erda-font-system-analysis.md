---
version: 1.0.0
date: 2025-02-09
history:
  - v1.0.0: Initial full analysis of ERDA Font & GitBook Worker Font System.
---

# Volle Analyse: ERDA Font & GitBook Worker Font System

## 🔴 1. KERNPROBLEM: Warum ERDA Fonts nicht mehr im PDF rendern

**Befund: Die Windows User Fonts sind korrumpiert und überschatten die Repo-Fonts.**

| Font | Windows User Fonts Pfad | Größe | Repo-Pfad | Größe |
|---|---|---|---|---|
| CJK | `%LOCALAPPDATA%\Microsoft\Windows\Fonts\erda-ccby-cjk-test.ttf` | **84 KB** (alter Test-Build!) | `.github/fonts/.../erda-ccby-cjk.ttf` | 155 KB ✅ |
| CJK (Duplikat) | `...\erda-ccby-cjk.ttf` | **5 Bytes** 💥 | — | — |
| Indic | `...\erda-ccby-indic.ttf` | **5 Bytes** 💥 | `.github/fonts/.../erda-ccby-indic.ttf` | 12 KB ✅ |
| Ethiopic | `...\erda-ccby-ethiopic.ttf` | **5 Bytes** 💥 | `.github/fonts/.../erda-ccby-ethiopic.ttf` | 4 KB ✅ |

**Was passiert:**

1. `luaotfload-tool --find="ERDA CC-BY CJK"` findet zuerst die **84 KB alte Test-Datei** (`erda-ccby-cjk-test.ttf`) aus dem Windows User Fonts Verzeichnis
2. Indic und Ethiopic werden zu den **5-Byte-Stub-Dateien** aufgelöst — das sind **keine gültigen Fonts**, sie rendern nichts
3. Der Publisher setzt zwar `OSFONTDIR` und generiert eine dynamische `fonts.conf`, aber der **LuaTeX-Cache** (unter `C:\texlive\2025\texmf-var\luatex-cache\`) hat die alten Pfade eingefroren
4. Im Cache befinden sich **4 verschiedene ERDA CJK Einträge** mit Versionen `1.0.20251104.200610`, `1.0.20251129.181446` und `1.0.20251105.175026` — ein Chaos aus historischen Installationen

## 🔧 2. Sofortige Reparatur (Font-Cache)

Um die Fonts wieder zum Laufen zu bringen, müssen zwei Dinge passieren:

**Schritt A: Korrumpierte Windows User Fonts entfernen**

```
C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\erda-ccby-cjk-test.ttf  ← löschen
C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\erda-ccby-cjk.ttf       ← löschen (5 Bytes!)
C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\erda-ccby-indic.ttf     ← löschen (5 Bytes!)
C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\erda-ccby-ethiopic.ttf  ← löschen (5 Bytes!)
```

**Schritt B: LuaTeX Font-Cache neu aufbauen**

```
luaotfload-tool --update --force
```

Danach sollte luaotfload die Fonts über `OSFONTDIR` direkt aus dem Repo-Pfad (`.github/fonts/erda-ccby-cjk/true-type/`) finden.

## 🏗️ 3. Architektur-Analyse: Gesamtes Font-System

```
┌─────────────────────────────────────────────────────────────────────┐
│                   fonts.yml  (Single Source of Truth)                │
│  7 Fonts: CJK, INDIC, ETHIOPIC, EMOJI, MONO, SANS, SERIF           │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
    ┌─────────────▼──────────────┐     ┌────────────────────────────┐
    │  FontConfigLoader          │────▶│  publish.yml Override       │
    │  (font_config.py)          │     │  mainfont_fallback:         │
    │  singleton, merges w/      │     │  "Twemoji:harf; ERDA CJK:  │
    │  manifest fonts            │     │   harf"                     │
    └─────────────┬──────────────┘     └────────────┬───────────────┘
                  │                                 │
    ┌─────────────▼─────────────────────────────────▼───────────────┐
    │  SmartFontStack  (smart_font_stack.py)                         │
    │  - Bootstrap: fonts-storage/ (DejaVu + Twemoji auto-download)  │
    │  - Search: .github/fonts/ → fonts-storage/ → system fonts      │
    │  - Resolve: declared paths → search paths → download           │
    │  - Write: temp fonts.meta.yml                                  │
    └─────────────┬─────────────────────────────────────────────────┘
                  │
    ┌─────────────▼─────────────────────────────────────────────────┐
    │  Publisher  (publisher.py)                                      │
    │  1. _configure_osfontdir()  → sets OSFONTDIR env               │
    │  2. Windows: generates dynamic fonts.conf → FONTCONFIG_FILE    │
    │  3. _normalize_fallback_spec() → checks luaotfload-tool --find │
    │  4. _lua_fallback_block() → Lua table literal                  │
    │  5. _build_font_header() → pandoc-fonts.tex                    │
    │     ├─ \directlua{luaotfload.add_fallback('mainfont', {...})}  │
    │     └─ \setmainfont[RawFeature={fallback=mainfont}]{DejaVu}    │
    │  6. Pandoc --pdf-engine=lualatex -H pandoc-fonts.tex           │
    └───────────────────────────────────────────────────────────────┘
```

**Font-Herkunft im Repo:**

| Font | Pfad im Repo | Tracking | Bootstrap |
|---|---|---|---|
| DejaVu (3×) | `fonts-storage/dejavu/` | **.gitignore** | Auto-Download via `FontStorageBootstrapper` |
| Twemoji Mozilla | `fonts-storage/twemoji-colr/` | **.gitignore** | Auto-Download via `FontStorageBootstrapper` |
| ERDA CJK | `.github/fonts/erda-ccby-cjk/true-type/` | **Git-tracked** (155 KB) | Lokal generiert aus `generator/` |
| ERDA Indic | `.github/fonts/erda-ccby-cjk/true-type/` | **Git-tracked** (12 KB) | Lokal generiert |
| ERDA Ethiopic | `.github/fonts/erda-ccby-cjk/true-type/` | **Git-tracked** (4 KB) | Lokal generiert |

### Datenfluss: fonts.yml → LaTeX Preamble

```
fonts.yml (CJK/INDIC/ETHIOPIC names)
    ↓
FontConfigLoader.get_default_fonts()
    ↓
_get_default_variables()  →  mainfontfallback = "ERDA CC-BY CJK:mode=harf; ..."
    ↓
publish.yml  pdf_options.mainfont_fallback  (OVERRIDE)
    ↓                                        ↓
_parse_pdf_options()  →  _build_variable_overrides()
    ↓
variable_map["mainfontfallback"] = "Twemoji Mozilla:mode=harf; ERDA CC-BY CJK:mode=harf"
    ↓
_normalize_fallback_spec()  ← checks luaotfload-tool --find, appends DejaVu Sans
    ↓
_lua_fallback_block()  →  Lua table: {"Twemoji Mozilla:mode=harf", "ERDA CC-BY CJK:mode=harf", ...}
    ↓
_build_font_header()  →  pandoc-fonts.tex
    ↓
\directlua{luaotfload.add_fallback('mainfont', {...})}
\setmainfont[RawFeature={fallback=mainfont}]{DejaVu Serif}
    ↓
Pandoc --pdf-engine=lualatex -H deeptex.sty -H pandoc-fonts.tex
```

### Relevante Umgebungsvariablen

| Variable | Default | Wirkung |
|---|---|---|
| `ERDA_ENABLE_LUA_FALLBACK` | `"1"` | `0`/`false`/`no`/`off` → kein `RawFeature`, kein `luaotfload.add_fallback()` |
| `ERDA_ENABLE_MISSING_GLYPH_DETECTOR` | `"0"` | `1` → LuaTeX-Callback loggt/bricht bei fehlenden Glyphen ab |
| `ERDA_KEEP_LATEX_TEMP` | `"0"` | Temp-Dir mit pandoc-fonts.tex behalten (Debug) |
| `OSFONTDIR` | (dynamisch gebaut) | Erweitert um `.github/fonts/` und `fonts-storage/` |
| `FONTCONFIG_FILE` | (dynamisch auf Windows) | Generierte `fonts.conf` damit fontconfig/luaotfload ERDA Fonts findet |

## 📦 4. ERDA Fonts im `.github`-Ordner: Analyse & Optionen

**Aktueller Stand:**

- 130 Dateien, ~808 KB insgesamt (davon TTFs: 250 KB)
- 75 Dateien in Git tracked (Generator-Code, Docs, Build-Logs, TTFs)
- Eigenständiges Unterprojekt mit eigener `.vscode/`, `requirements.txt`, Benchmarks, Tests
- Eigentlich ein **komplettes Mini-Projekt** — `fonttools` als Dependency, Python-Generator, modulare Zeichensätze

### Option A: Im Repo belassen (Status Quo verbessern)

- **Pro:** Alles in einem Repo, einfaches Deployment, TTFs direkt verfügbar
- **Contra:** 808 KB "Ballast" für Kunden die andere Fonts wollen; Generator-Code ist irrelevant für den Worker; `.github/fonts` ist ein ungewöhnlicher Pfad
- **Empfehlung:** Wenn beibehalten → Generator/Docs/Logs gehören aufgeräumt, nur die 3 TTFs + Lizenz + minimales README behalten

### Option B: Eigenes Git-Repo (`erda-ccby-fonts`)

- **Pro:** Saubere Trennung; eigene Versionierung und Releases; Kunden können Fork/Alternative nutzen; Font-Generator wird eigenständig testbar; Worker-Repo bleibt schlank
- **Contra:** Zusätzliche Dependency-Verwaltung; `fonts.yml` braucht `download_url` statt `paths`; Build-Pipeline komplexer
- **Empfehlung:** **Dies ist die beste Langzeitlösung.** Der Font-Generator IST bereits ein eigenständiges Projekt.

### Option C: Kundenwahl-Modell (ERDA Fonts optional)

- **Pro:** Maximale Flexibilität — Kunden wählen eigene CJK-Fonts (Noto Sans CJK, Source Han, etc.)
- **Contra:** Lizenz-Tracking wird komplex; jeder Font braucht eigene Attribution; Testing-Matrix explodiert
- **Empfehlung:** Kann auf Option B aufbauen — `fonts.yml` erlaubt bereits `download_url` und `paths`-Overrides über `publish.yml`

## 🎯 5. Empfohlene Strategie (3 Phasen)

**Phase 1 — Sofort:**

1. Korrumpierte Windows User Fonts löschen
2. `luaotfload-tool --update --force` ausführen
3. PDF-Build testen → Fonts sollten wieder rendern

**Phase 2 — Kurzfristig (nächster Sprint):**

1. `.github/fonts/erda-ccby-cjk/` aufräumen: Generator-Logs, Benchmarks, alte Docs entfernen
2. In `fonts.yml` bei CJK/INDIC/ETHIOPIC eine `download_url` ergänzen (GitHub Release URL)
3. `FontStorageBootstrapper` um ERDA-Font-Bundle erweitern (analog DejaVu/Twemoji)
4. Publisher-Code härten: Vor jedem Build prüfen ob resolved Font-Pfad > 100 Bytes (Guard gegen korrupte Stubs)

**Phase 3 — Mittelfristig:**

1. Neues Repo `erda-ccby-fonts` erstellen mit Generator + TTF-Releases
2. `fonts.yml` umstellen: `paths` → `download_url` (GitHub Release Asset)
3. `.github/fonts/` aus Worker-Repo entfernen
4. Kunden-Dokumentation: "Bring your own CJK font" Guide in `docs/`
5. `publish.yml` erhält optionale `fonts:`-Sektion für Kunden-Overrides (Mechanismus existiert bereits via `merge_manifest_fonts`)
