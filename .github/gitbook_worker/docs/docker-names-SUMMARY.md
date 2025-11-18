# Smart Merge Configuration Module - Implementation Summary

## Was wurde implementiert?

Ein vollständig konfigurierbares System für Docker-Image- und Container-Namen im ERDA GitBook Worker Repository. Keine Hardcodierung mehr – alle Namen werden über ein mehrschichtiges YAML-Merge-System konfiguriert.

## Erstellte Dateien

### Python Module (`.github/gitbook_worker_tools/`)

1. **`__init__.py`** - Package-Definition
2. **`smart_merge.py`** - Kern-Implementierung (YAML-Merge, Template-Rendering)
3. **`cli.py`** - Kommandozeilen-Interface mit Subkommandos
4. **`README.md`** - Vollständige API- und CLI-Dokumentation
5. **`INTEGRATION.md`** - Integrationsbeispiele für Tests, Workflows, Skripte
6. **`MIGRATION.md`** - Migrationsleitfaden von hardkodierten zu konfigurierbaren Namen

### Konfigurationsdateien

1. **`.github/gitbook_worker/defaults/docker_config.yml`** - Standard-Konfiguration
2. **`docker_config.yml.example`** - Beispiel für Repository-Überschreibungen

### Wrapper-Skripte (Repo Root)

1. **`docker-names.ps1`** - PowerShell-Wrapper für einfachen CLI-Zugriff
2. **`docker-names.sh`** - Bash-Wrapper für einfachen CLI-Zugriff

### Tests

1. **`.github/gitbook_worker/tests/test_smart_merge.py`** - Vollständige Unit-Tests (13 Tests, alle bestehen)

### Dokumentation

1. **`README.md`** - Aktualisiert mit Docker-Konfigurationssektion

## Architektur

### Konfigurationsebenen (Niedrigste → Höchste Priorität)

1. `.github/gitbook_worker/defaults/docker_config.yml` - Defaults
2. `docker_config.yml` (Repo-Root) - Repository-weite Überschreibungen
3. `publish.yml` - `docker_config` Sektion - Allgemeine Einstellungen
4. `publish.yml` - Spezifischer Publish-Eintrag - Entry-spezifisch

### Kontexte

- **`github-action`** - GitHub Actions CI/CD
- **`prod`** - Produktionsumgebung
- **`test`** - Lokale Tests (pytest)
- **`docker-test`** - Docker-basierte Integrationstests

### Template-System

Verwendet Python's `str.format()` für Platzhalter:

```yaml
docker_names:
  test:
    image: "erda-gitbook-{context}:{branch}"
    container: "erda-{context}-{publish_name}"
```

Verfügbare Variablen:
- `{context}` - Ausführungskontext
- `{repo_name}` - Repository-Name
- `{branch}` - Git-Branch
- `{publish_name}` - Publish-Eintragsname
- Benutzerdefinierte Variablen via `--var KEY=VALUE`

## CLI-Verwendung

### Einzelnen Namen abrufen

```bash
# PowerShell
.\docker-names.ps1 get-name --type image --context test --publish-name space-tests

# Direkt mit Python
$env:PYTHONPATH="C:\RAMProjects\ERDA\.github"
python -m gitbook_worker_tools.cli get-name --type container --context docker-test
```

### Alle Namen als JSON

```bash
.\docker-names.ps1 get-all-names --context docker-test --publish-name space-tests

# Ausgabe:
# {
#   "image": "erda-gitbook-dockertest:latest",
#   "container": "erda-dockertest-space-tests"
# }
```

### Konfiguration ausgeben

```bash
.\docker-names.ps1 dump-config --publish-name main-book
```

## Python API

```python
from gitbook_worker_tools import smart_merge

# Alle Namen abrufen
names = smart_merge.get_all_docker_names(
    repo_root=Path("/path/to/repo"),
    publish_name="space-tests",
    context="docker-test",
    extra_vars={"branch": "main"}
)

print(f"Image: {names['image']}")
print(f"Container: {names['container']}")

# Konfiguration zusammenführen
config = smart_merge.merge_configs(
    repo_root=Path("/path/to/repo"),
    publish_name="main-book"
)

# Spezifischen Namen abrufen
image = smart_merge.get_docker_name(
    config=config,
    name_type="image",
    context="test",
    extra_vars={"branch": "main"}
)
```

## Integration

### Pytest Fixture

```python
# conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

@pytest.fixture
def docker_names():
    def _get_names(context="test", publish_name="test"):
        repo_root = Path(__file__).parent.parent
        return smart_merge.get_all_docker_names(
            repo_root=repo_root,
            publish_name=publish_name,
            context=context
        )
    return _get_names

# In Tests verwenden
def test_build(docker_names):
    names = docker_names(context="docker-test", publish_name="space-tests")
    subprocess.run(["docker", "build", "-t", names["image"], "."])
```

### GitHub Actions

```yaml
- name: Get Docker Names
  id: docker
  run: |
    export PYTHONPATH="${GITHUB_WORKSPACE}/.github"
    NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
      --context github-action \
      --publish-name main-book \
      --repo-name ${{ github.repository }} \
      --branch ${{ github.ref_name }})
    
    echo "image=$(echo "$NAMES" | jq -r '.image')" >> $GITHUB_OUTPUT
    echo "container=$(echo "$NAMES" | jq -r '.container')" >> $GITHUB_OUTPUT

- name: Build
  run: docker build -t ${{ steps.docker.outputs.image }} .
```

## Tests

Alle 13 Unit-Tests bestehen:

```
test_deep_merge                          ✓
test_load_yaml_safe                      ✓
test_merge_configs_defaults_only         ✓
test_merge_configs_with_overrides        ✓
test_merge_configs_with_publish_yml      ✓
test_render_template                     ✓
test_render_template_missing_variable    ✓
test_get_docker_name                     ✓
test_get_docker_name_fallback_to_default ✓
test_get_all_docker_names                ✓
test_get_docker_name_no_config           ✓
test_get_docker_name_no_template         ✓
test_complex_layering                    ✓
```

## Vorteile

1. **Keine Hardcodierung** - Alle Namen konfigurierbar
2. **Konsistenz** - Einheitliche Namenskonventionen
3. **Flexibilität** - Einfache Überschreibung pro Kontext/Publish-Eintrag
4. **Keine Konflikte** - Verschiedene Kontexte verwenden verschiedene Namen
5. **Wartbarkeit** - Änderungen an einer Stelle
6. **Dokumentiert** - Vollständige Dokumentation und Beispiele

## Nächste Schritte (Optional)

1. **Migration**: Bestehende Tests/Workflows auf smart_merge umstellen
2. **CI/CD**: GitHub Actions Workflows aktualisieren
3. **Konfiguration**: `docker_config.yml` für projekt-spezifische Namen erstellen
4. **Cleanup**: Alte hardcodierte Namen entfernen

## Antwort auf die ursprüngliche Frage

> "welcher Teil der Repo Software hat das getan?"

Der Container `sphere-space-tests` wurde höchstwahrscheinlich von:
- Einem Test in `.github/gitbook_worker/tests/` **ODER**
- Einem manuellen `docker run` Befehl mit hardcodiertem Namen

Mit dem neuen System kann jeder Teil des Repositories (Tests, Workflows, Skripte) die konfigurierten Namen abrufen über:
- CLI: `./docker-names.ps1 get-name ...`
- Python API: `smart_merge.get_all_docker_names(...)`

Keine Hardcodierung mehr notwendig!

## Lizenz

- Code: MIT License (siehe `LICENSE-CODE`)
- Dokumentation: CC BY-SA 4.0 (siehe `LICENSE`)

---

**Implementiert am**: 11. November 2025  
**Status**: ✅ Vollständig implementiert und getestet  
**Alle Tests**: ✅ 13/13 bestanden
