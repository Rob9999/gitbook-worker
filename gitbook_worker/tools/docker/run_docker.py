#!/usr/bin/env python3
"""
Plattformunabhängiges Convenience-Modul zum Ausführen von Tests und Orchestrator im Docker Container.

Verwendung:
    python run_docker.py test                    # Alle Tests
    python run_docker.py test-slow               # Nur Integrationstests
    python run_docker.py orchestrator            # Orchestrator mit Default-Profil
    python run_docker.py orchestrator --profile ci  # Mit spezifischem Profil
    python run_docker.py orchestrator --rebuild     # Image neu bauen und Orchestrator starten
    python run_docker.py shell                   # Interaktive Shell im Container
    python run_docker.py build                   # Nur Image bauen
    python run_docker.py info                    # Build-Informationen anzeigen

Optionen:
    --no-build      Image nicht bauen, wenn es fehlt
    --rebuild       Image vor Ausführung neu bauen (erzwingt --pull)
    --no-cache      Docker-Build ohne Layer-Cache
    --profile       Profil für Orchestrator (default: local)
    --verbose       Mehr Logging-Output
    --use-dynamic   Verwende Dockerfile.dynamic statt Dockerfile (empfohlen)
"""

import argparse
import sys
from pathlib import Path


def _detect_repo_root(start: Path) -> Path:
    """Best-effort repository root detection.

    Walks up the directory tree looking for known markers (content.yaml, .git).
    Falls back to the historical relative traversal if no marker is found.
    """

    markers = {"content.yaml", ".git"}
    for candidate in [start, *start.parents]:
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    # Fallback: assume the repo root is three levels up (gitbook_worker/../..)
    return start.parents[3]


_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = _detect_repo_root(_THIS_FILE)
TOOLS_PATH = REPO_ROOT / "gitbook_worker" / "tools"
if str(TOOLS_PATH) not in sys.path:
    sys.path.insert(0, str(TOOLS_PATH))

from utils.docker_runner import main as docker_runner_main


def _windows_path_to_docker(path: Path) -> str:
    """Convert Windows path to Docker-compatible format.

    Examples:
        C:\\Users\\me\\repo -> /c/Users/me/repo
        /c/Users/me/repo -> /c/Users/me/repo (already Unix-style)
    """
    path_str = str(path.resolve())
    # Check if Windows path (has drive letter)
    if len(path_str) > 1 and path_str[1] == ":":
        drive = path_str[0].lower()
        rest = path_str[2:].replace("\\", "/")
        return f"/{drive}{rest}"
    # Already Unix-style
    return path_str.replace("\\", "/")


def build_docker_args(
    command: str,
    profile: str = "local",
    no_build: bool = False,
    verbose: bool = False,
    rebuild: bool = False,
    no_cache: bool = False,
    use_dynamic: bool = False,
) -> list[str]:
    """Erstelle die Argumentliste für docker_runner."""

    # Wähle Dockerfile basierend auf --use-dynamic Flag
    dockerfile_name = "Dockerfile.dynamic" if use_dynamic else "Dockerfile"
    dockerfile = str(
        REPO_ROOT / "gitbook_worker" / "tools" / "docker" / dockerfile_name
    )
    # "ERDA Smart Worker" für dynamisches Image, Legacy für statisches
    tag = "erda-smart-worker" if use_dynamic else "erda-workflow-tools"
    context = str(REPO_ROOT)
    workdir = str(REPO_ROOT)

    args = [
        "--dockerfile",
        dockerfile,
        "--tag",
        tag,
        "--context",
        context,
        "--workdir",
        workdir,
        "--env",
        "PYTHONPATH=/workspace",
        "--env",
        "OSFONTDIR=/workspace/.github/fonts:/workspace/fonts-storage",
    ]

    # Mount zusätzliche Verzeichnisse, die fonts.yml referenziert
    # .github/fonts für ERDA CC-BY CJK
    github_fonts = REPO_ROOT / ".github" / "fonts"
    if github_fonts.exists():
        github_fonts_docker = _windows_path_to_docker(github_fonts)
        args.extend(
            [
                "--run-arg=-v",
                f"--run-arg={github_fonts_docker}:/workspace/.github/fonts:ro",
            ]
        )

    # fonts-storage für selbst-gehostete Font-Bundles (z.B. Twemoji Mozilla)
    # Erstelle das Verzeichnis, falls es nicht existiert (z.B. auf frischem GitHub Checkout)
    fonts_storage = REPO_ROOT / "fonts-storage"
    if not fonts_storage.exists():
        fonts_storage.mkdir(parents=True, exist_ok=True)
        logger_note = (
            f"✓ Created fonts-storage directory at {fonts_storage}\n"
            "  Fonts will be downloaded automatically via FontStorageBootstrapper"
        )
        print(logger_note)

    fonts_storage_docker = _windows_path_to_docker(fonts_storage)
    args.extend(
        [
            "--run-arg=-v",
            f"--run-arg={fonts_storage_docker}:/workspace/fonts-storage:ro",
        ]
    )

    if no_build:
        args.append("--no-build")

    if verbose:
        args.append("--verbose")

    if rebuild:
        args.append("--rebuild")

    if no_cache:
        args.append("--no-cache")

    # Füge den Container-Befehl hinzu
    # WICHTIG: --it muss das LETZTE Argument vor dem Container-Befehl sein
    # argparse.REMAINDER nimmt alle nachfolgenden Argumente automatisch auf
    args.append("--it")

    if command == "test":
        args.extend(
            [
                "bash",
                "-c",
                "cd /workspace && python3 -m pytest gitbook_worker/tests -v --tb=short",
            ]
        )
    elif command == "test-slow":
        args.extend(
            [
                "bash",
                "-c",
                "cd /workspace && python3 -m pytest gitbook_worker/tests -v -m slow --tb=short",
            ]
        )
    elif command == "orchestrator":
        # Font-Check: Rebuild fontconfig cache for mounted volumes and check availability
        # The mounted fonts in /workspace/.github/fonts and /workspace/fonts-storage
        # need to be registered with fontconfig before use
        font_guard = (
            "fc-cache -f /workspace/.github/fonts /workspace/fonts-storage 2>/dev/null || true; "
            "test -f /workspace/fonts-storage/twemoji-colr/TwemojiMozilla.ttf || "
            "{ echo 'ERROR: Twemoji font file missing in /workspace/fonts-storage/twemoji-colr/'; exit 45; }; "
            "test -f /workspace/.github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf || "
            "{ echo 'ERROR: ERDA CC-BY CJK font file missing in /workspace/.github/fonts/'; exit 46; }; "
        )
        orchestrator_cmd = (
            "python3 -m gitbook_worker.tools.workflow_orchestrator run "
            "--root /workspace "
            "--content-config content.yaml "
            "--lang de "
            f"--profile {profile}"
        )
        args.extend(
            [
                "bash",
                "-c",
                f"cd /workspace && {font_guard}{orchestrator_cmd}",
            ]
        )
    elif command == "shell":
        args.extend(["bash"])
    elif command == "info":
        # Zeige Build-Informationen an
        args.extend(["--info"])
    elif command == "build":
        # Nur bauen, nichts ausführen
        args = [
            "--dockerfile",
            dockerfile,
            "--tag",
            tag,
            "--context",
            context,
            "--workdir",
            workdir,
            "--print-only",  # Nur anzeigen, nicht ausführen
            "--it",
            "true",  # Dummy-Befehl
        ]
    else:
        raise ValueError(f"Unbekannter Befehl: {command}")

    return args


def main():
    parser = argparse.ArgumentParser(
        description="Docker-basierte Tests und Workflows ausführen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s test                      # Alle Unit-Tests ausführen
  %(prog)s test-slow                 # Integrationstests ausführen
  %(prog)s orchestrator              # Orchestrator mit local-Profil
  %(prog)s orchestrator --profile ci # Orchestrator mit ci-Profil
  %(prog)s shell                     # Interaktive Shell im Container
  %(prog)s build                     # Nur Docker-Image bauen
        """,
    )

    parser.add_argument(
        "command",
        choices=["test", "test-slow", "orchestrator", "shell", "build", "info"],
        help="Auszuführender Befehl",
    )

    parser.add_argument(
        "--profile",
        default="local",
        help="Profil für den Orchestrator (default: local)",
    )

    parser.add_argument(
        "--no-build", action="store_true", help="Image nicht bauen, wenn es fehlt"
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Image vor dem Start neu bauen (inkl. --pull)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Docker-Build ohne Layer-Cache ausführen",
    )

    parser.add_argument("--verbose", action="store_true", help="Mehr Logging-Output")

    parser.add_argument(
        "--use-dynamic",
        action="store_true",
        help="Verwende Dockerfile.dynamic statt Dockerfile (empfohlen für Best Practice)",
    )

    args = parser.parse_args()

    # Wähle Dockerfile
    dockerfile_name = "Dockerfile.dynamic" if args.use_dynamic else "Dockerfile"
    tag_name = "erda-smart-worker" if args.use_dynamic else "erda-workflow-tools"

    if args.use_dynamic and args.verbose:
        print("ℹ Using Dockerfile.dynamic (ERDA Smart Worker)")

    # Spezialfall: Nur bauen
    if args.command == "build":
        image_type = "ERDA Smart Worker" if args.use_dynamic else "Legacy"
        print(f"Building Docker image ({image_type}) using {dockerfile_name}...")
        docker_args = [
            "--dockerfile",
            str(
                REPO_ROOT
                / ".github"
                / "gitbook_worker"
                / "tools"
                / "docker"
                / dockerfile_name
            ),
            "--tag",
            tag_name,
            "--context",
            str(REPO_ROOT),
            "--workdir",
            str(REPO_ROOT),
        ]
        if args.verbose:
            docker_args.append("--verbose")
        if args.no_cache:
            docker_args.append("--no-cache")
        docker_args.append("--rebuild")
        docker_args.extend(["--it", "true"])  # Dummy-Befehl, wird nicht ausgeführt

        # Baue das Image
        try:
            return docker_runner_main(docker_args)
        except SystemExit as e:
            if e.code == 0:
                print(f"SUCCESS: Docker image built successfully (tag: {tag_name})!")
            return e.code

    # Normale Befehle
    docker_args = build_docker_args(
        command=args.command,
        profile=args.profile,
        no_build=args.no_build,
        verbose=args.verbose,
        rebuild=args.rebuild,
        no_cache=args.no_cache,
        use_dynamic=args.use_dynamic,
    )

    if args.verbose:
        print(f"Docker command: {args.command}")
        print(f"Profile: {args.profile}")
        print(f"No-Build: {args.no_build}")

    try:
        exit_code = docker_runner_main(docker_args)
        if exit_code == 0:
            print(f"\nSUCCESS: Command '{args.command}' completed successfully!")
        else:
            print(f"\nERROR: Command '{args.command}' failed (exit code: {exit_code})")
        return exit_code
    except KeyboardInterrupt:
        print("\nWARNING: Interrupted by user")
        return 130
    except Exception as e:
        print(f"\nERROR: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
