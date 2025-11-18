#!/usr/bin/env python3
"""
python_workspace_runner.py — Convenience runner für isolierte Python-Workspaces

Ziele
- Ein Workspace (Ordner) vorbereiten: venv erstellen/aktualisieren
- Abhängigkeiten installieren (requirements*.txt ODER pyproject.toml)
- Danach ein Kommando/Modul im Workspace-venv starten

Highlights
- Windows/Linux/macOS kompatibel
- .venv im Workspace-Root
- Robust gegen cp1252 (ASCII-Logging)
- Unterstützt sowohl `--cmd`-Tokens als auch Remainder nach `--`
- Optional schnelle Installer: `uv` (wenn vorhanden)

Beispiele
--------
# 1) Publishing-Tests im .github-Workspace fahren
python python_workspace_runner.py \
  --root .github \
  --install auto \
  --module pytest -- -vv -s .github/tests/

# 2) simulations-Workspace, Requirements erzwingen und Script starten
python python_workspace_runner.py \
  --root simulations \
  --install requirements \
  --req requirements.txt --req requirements-dev.txt \
  --cmd python src/simulations/deck_calculator/adapter.py --flagX

# 3) Nur Umgebung vorbereiten, nichts starten
python python_workspace_runner.py --root .github --install auto --print-env
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Iterable, List, Sequence

try:
    import tomllib  # Python 3.11+
except Exception:
    tomllib = None  # optional

# ------------------------------
# Logging (ASCII only)
# ------------------------------


def log_info(msg: str) -> None:
    print(f"INFO: {msg}")


def log_warn(msg: str) -> None:
    print(f"WARN: {msg}")


def log_error(msg: str) -> None:
    print(f"ERROR: {msg}")


def shquote(token: str) -> str:
    if any(ch in token for ch in (" ", "\t", '"', "'")):
        return f'"{token}"'
    return token


# ------------------------------
# OS helpers
# ------------------------------


def is_windows() -> bool:
    return platform.system().lower() == "windows"


# ------------------------------
# Subprocess
# ------------------------------


def run(cmd: Sequence[str], cwd: Path | None = None, env: dict | None = None) -> int:
    log_info(
        "EXEC: " + " ".join(shquote(c) for c in cmd) + (f"  (cwd={cwd})" if cwd else "")
    )
    try:
        cp = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env)
        return cp.returncode
    except FileNotFoundError:
        log_error(f"Command not found: {cmd[0]}")
        return 127


def run_capture(
    cmd: Sequence[str], cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    log_info(
        "EXEC: " + " ".join(shquote(c) for c in cmd) + (f"  (cwd={cwd})" if cwd else "")
    )
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True
    )


# ------------------------------
# Venv helpers
# ------------------------------


def venv_paths(root: Path) -> dict:
    vdir = root / ".venv"
    if is_windows():
        return {
            "dir": vdir,
            "python": vdir / "Scripts" / "python.exe",
            "pip": vdir / "Scripts" / "pip.exe",
            "bin": vdir / "Scripts",
        }
    else:
        return {
            "dir": vdir,
            "python": vdir / "bin" / "python",
            "pip": vdir / "bin" / "pip",
            "bin": vdir / "bin",
        }


def ensure_venv(root: Path, base_python: Path | None, upgrade_deps: bool) -> int:
    vp = venv_paths(root)
    vdir: Path = vp["dir"]
    vpy: Path = vp["python"]

    if not vdir.exists():
        vdir.mkdir(parents=True, exist_ok=True)
        py = str(base_python or sys.executable)
        # --upgrade-deps ist ab Python 3.9 verfügbar; wenn es scheitert, fallback ohne
        rc = run([py, "-m", "venv", "--upgrade-deps", str(vdir)])
        if rc != 0:
            log_warn("Falling back to 'python -m venv' without --upgrade-deps")
            rc = run([py, "-m", "venv", str(vdir)])
        if rc != 0:
            return rc

    if upgrade_deps:
        rc = run([str(vpy), "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"])
        if rc != 0:
            return rc
    return 0


def prefer_uv() -> bool:
    return shutil.which("uv") is not None


def install_dependencies(
    root: Path,
    mode: str,
    req_files: list[Path],
    extras: list[str],
    allow_pre: bool,
    index_url: str | None,
    extra_index_url: str | None,
) -> int:
    vp = venv_paths(root)
    vpy: Path = vp["python"]

    # Harmonisiere Pfade relativ zum Root
    req_files = [(root / p) if not p.is_absolute() else p for p in req_files]

    pyproject = root / "pyproject.toml"
    has_pyproject = pyproject.exists()
    # Default-Heuristik
    if mode == "auto":
        if (
            any(
                (root / n).exists()
                for n in (
                    "requirements.txt",
                    "requirements-dev.txt",
                    "requirements.lock",
                )
            )
            or req_files
        ):
            mode_eff = "requirements"
        elif has_pyproject:
            mode_eff = "pyproject"
        else:
            log_info(
                "Keine requirements/pyproject gefunden — Überspringe Installation."
            )
            return 0
    else:
        mode_eff = mode

    base_pip = [str(vpy), "-m", "pip", "install"]
    if allow_pre:
        base_pip += ["--pre"]
    if index_url:
        base_pip += ["--index-url", index_url]
    if extra_index_url:
        base_pip += ["--extra-index-url", extra_index_url]

    if mode_eff == "requirements":
        # Sammle existierende Files
        candidates = req_files[:]
        for n in ("requirements.txt", "requirements-dev.txt", "requirements.lock"):
            p = root / n
            if p.exists() and p not in candidates:
                candidates.append(p)
        if not candidates:
            log_warn("Mode 'requirements', aber keine requirements-Dateien gefunden.")
            return 0
        for rf in candidates:
            rc = run(base_pip + ["-r", str(rf)], cwd=root)
            if rc != 0:
                return rc
        return 0

    if mode_eff == "pyproject":
        if not has_pyproject:
            log_error("pyproject.toml nicht gefunden.")
            return 1
        if prefer_uv():
            # Schnell und deterministisch, falls uv verfügbar ist
            cmd = ["uv", "pip", "install", "-e", "."]
            for ex in extras:
                cmd += ["-E", ex]
            if allow_pre:
                cmd += ["--prerelease"]
            rc = run(cmd, cwd=root)
            return rc
        else:
            cmd = base_pip + ["-e", "."]
            if extras:
                # pip Extras via ".[ex1,ex2]"
                spec = ".[" + ",".join(extras) + "]"
                cmd = base_pip + ["-e", spec]
            rc = run(cmd, cwd=root)
            return rc

    log_error(f"Unbekannter Installationsmodus: {mode_eff}")
    return 2


# ------------------------------
# Pytest ensure helper
# ------------------------------


def ensure_pytest_installed(root: Path) -> int:
    """If pytest is missing, try to install it. Prefer optional-dependencies
    extras from pyproject.toml (tests/test/dev/ci). Returns 0 on success.
    """
    vp = venv_paths(root)
    vpy = str(vp["python"])

    # Probe: is pytest importable?
    probe = run(
        [
            vpy,
            "-c",
            "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('pytest') else 42)",
        ]
    )
    if probe == 0:
        return 0

    # Prefer installing extras if declared in pyproject
    pyproj = root / "pyproject.toml"
    if tomllib and pyproj.exists():
        try:
            with pyproj.open("rb") as fh:
                data = tomllib.load(fh)
            opt = (data.get("project") or {}).get("optional-dependencies") or {}
            for extra_key in ("tests", "test", "dev", "ci"):
                if extra_key in opt:
                    log_info(f"Installiere pyproject-Extras: {extra_key}")
                    rc = run(
                        [vpy, "-m", "pip", "install", "-e", f".[{extra_key}]"], cwd=root
                    )
                    if rc == 0:
                        return 0
        except Exception as e:
            log_warn(f"Konnte pyproject nicht lesen: {e}")

    # Fallback: install pytest directly
    log_info("pytest nicht gefunden – installiere 'pytest'")
    return run([vpy, "-m", "pip", "install", "-U", "pytest"], cwd=root)


# ------------------------------
# Command execution in venv
# ------------------------------


def build_env_with_venv(root: Path, extra_env: list[str]) -> dict:
    env = os.environ.copy()
    vp = venv_paths(root)
    bin_dir = str(vp["bin"])
    # Prepend venv bin to PATH
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    # Ensure venv is visible to Python tooling
    env["VIRTUAL_ENV"] = str(vp["dir"])
    # Parse KEY=VALUE pairs
    for kv in extra_env:
        if "=" in kv:
            k, v = kv.split("=", 1)
            env[k] = v
        else:
            log_warn(f"Ignoriere ungültige --env Angabe: {kv}")
    return env


def run_module_in_venv(
    root: Path,
    exec_cwd: Path,
    module: str,
    args: list[str],
    env_pairs: list[str],
) -> int:
    vp = venv_paths(root)
    vpy = str(vp["python"])
    env = build_env_with_venv(root, env_pairs)
    cmd = [vpy, "-m", module] + args
    return run(cmd, cwd=exec_cwd, env=env)


def run_cmd_in_venv(
    root: Path, exec_cwd: Path, cmd: list[str], env_pairs: list[str]
) -> int:
    env = build_env_with_venv(root, env_pairs)
    return run(cmd, cwd=exec_cwd, env=env)


# ------------------------------
# Path normalization
# ------------------------------


def _rebase_token_to_root(token: str, root: Path) -> str:
    """
    - Absolute Pfade unterhalb von ``root`` -> relativ zu ``root``.
    - Tokens, die mit ``<rootname>/`` oder ``<rootname>\`` anfangen (z.B. ``.github/...``),
      werden auf den Teil nach dem Rootnamen gekürzt.
    """

    t = token.strip('"')
    p = Path(t)

    # Absolutpfade in root -> relativ machen
    if p.is_absolute():
        try:
            rel = p.relative_to(root)
            return str(rel)
        except Exception:
            return token

    # Präfix '<rootname>/' oder '\\' entfernen
    root_name = root.name
    root_name_lower = root_name.lower()
    lowered = t.lower()
    for sep in ("/", "\\"):
        prefix = f"{root_name}{sep}"
        if lowered.startswith(f"{root_name_lower}{sep}"):
            return t[len(prefix) :]
    return token


def _rebase_list(tokens: list[str], root: Path) -> list[str]:
    return [_rebase_token_to_root(tok, root) for tok in (tokens or [])]


# ------------------------------
# CLI
# ------------------------------


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Prepare a Python workspace (.venv + deps) and run a command or module.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument(
        "--root",
        required=True,
        help="Workspace-Root (Ordner mit requirements/pyproject)",
    )
    p.add_argument(
        "--base-python",
        default=None,
        help="Interpreter zum Erstellen der venv (default: aktueller Python)",
    )
    p.add_argument(
        "--clean", action="store_true", help="Bestehende .venv löschen und neu anlegen"
    )
    p.add_argument(
        "--upgrade",
        dest="upgrade",
        action="store_true",
        help="pip/setuptools/wheel upgraden (default: an)",
    )
    p.add_argument(
        "--no-upgrade",
        dest="upgrade",
        action="store_false",
        help="Upgrades überspringen",
    )
    p.set_defaults(upgrade=True)

    p.add_argument(
        "--install",
        choices=["auto", "requirements", "pyproject", "skip"],
        default="auto",
        help="Installationsmodus",
    )
    p.add_argument(
        "--req",
        action="append",
        default=[],
        help="Zusätzliche requirements-Datei (mehrfach)",
    )
    p.add_argument(
        "--extras",
        default="",
        help="Komma-separierte Extras bei pyproject (z.B. dev,tests)",
    )
    p.add_argument(
        "--pre", action="store_true", help="Vorab-Releases (pre-release) erlauben"
    )
    p.add_argument("--index-url", default=None, help="Custom pip --index-url")
    p.add_argument(
        "--extra-index-url", default=None, help="Custom pip --extra-index-url"
    )

    p.add_argument(
        "--env",
        action="append",
        default=[],
        help="KEY=VALUE ins Laufzeit-Env (mehrfach)",
    )
    p.add_argument(
        "--module", default=None, help="Python-Modul mit 'python -m <module>' ausführen"
    )
    p.add_argument(
        "--cmd",
        nargs="+",
        default=None,
        help="Kommando in venv ausführen (Alternative zu Remainder)",
    )
    p.add_argument(
        "--print-env", action="store_true", help="Nur venv-Pfade ausgeben und beenden"
    )
    p.add_argument(
        "--exec-cwd",
        choices=["root", "repo"],
        default="root",
        help=(
            "Arbeitsverzeichnis für die Ausführung: 'root' = Workspace-Root, 'repo' = "
            "Repository-Root (Parent von .github)"
        ),
    )

    # Alles nach `--` als remainder (z.B. pytest-Args)
    p.add_argument(
        "remainder",
        nargs=argparse.REMAINDER,
        help="Argumente nach '--' werden an Modul/Kommando weitergereicht",
    )

    args = p.parse_args(argv)
    return args


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        log_error(f"Root existiert nicht: {root}")
        return 2

    vp = venv_paths(root)
    vdir: Path = vp["dir"]

    # Clean venv
    if args.clean and vdir.exists():
        log_info(f"Entferne bestehende venv: {vdir}")
        shutil.rmtree(vdir, ignore_errors=True)

    # Ensure venv
    base_py = Path(args.base_python).resolve() if args.base_python else None
    rc = ensure_venv(root, base_py, upgrade_deps=args.upgrade)
    if rc != 0:
        return rc

    # Install deps
    reqs = [Path(p) for p in args.req]
    extras = [e.strip() for e in args.extras.split(",") if e.strip()]
    rc = install_dependencies(
        root,
        args.install,
        reqs,
        extras,
        allow_pre=args.pre,
        index_url=args.index_url,
        extra_index_url=args.extra_index_url,
    )
    if rc != 0:
        return rc

    if args.exec_cwd == "repo" and root.name == ".github":
        exec_cwd = root.parent
    else:
        exec_cwd = root

    env_pairs = list(args.env)
    if not any(kv.startswith("REPO_ROOT=") for kv in env_pairs):
        env_pairs.append(f"REPO_ROOT={exec_cwd}")
    if not any(kv.startswith("GITHUB_DIR=") for kv in env_pairs):
        gh_dir = (exec_cwd / ".github").resolve()
        env_pairs.append(f"GITHUB_DIR={gh_dir}")

    # Auto-install pytest when requested as module
    if args.module and args.module.lower() == "pytest":
        rc = ensure_pytest_installed(root)
        if rc != 0:
            return rc

    if args.print_env:
        vp = venv_paths(root)
        print(
            textwrap.dedent(
                f"""
        VENV_DIR={vp['dir']}
        VENV_PYTHON={vp['python']}
        VENV_BIN={vp['bin']}
        """
            )
        )
        return 0

    # Determine command
    remainder = list(args.remainder or [])
    if remainder and remainder[0] == "--":
        remainder = remainder[1:]

    # Pfade nur rebasen, wenn wir auch im Workspace-Root starten.
    # Bei --exec-cwd repo sollen z.B. ".github/tests/" unverändert bleiben.
    if exec_cwd == root:
        remainder = _rebase_list(remainder, root)

    if args.module:
        # remainder an Modul weiterreichen
        return run_module_in_venv(root, exec_cwd, args.module, remainder, env_pairs)

    if args.cmd:
        # direkte Kommandotokens: nur im Root rebasen
        cmd = (
            _rebase_list(list(args.cmd), root) if exec_cwd == root else list(args.cmd)
        ) + remainder
        return run_cmd_in_venv(root, exec_cwd, cmd, env_pairs)

    # Nichts auszuführen angegeben -> Hinweis + Erfolg
    log_info(
        "Keine Ausführung angegeben. Verwende --module pytest -- -vv -s .github/tests/ oder --cmd python ..."
    )
    return 0


if __name__ == "__main__":
    main()
