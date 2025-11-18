import yaml
from tools.publishing import markdown_combiner


def _parse(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    meta = yaml.safe_load("\n".join(lines[1:end])) or {}
    body = "\n".join(lines[end + 1 :])  # noqa: E203
    return meta, body


def test_add_geometry_package_plain_text():
    text = "Hello"
    meta, body = _parse(markdown_combiner.add_geometry_package(text))
    assert "geometry" in meta
    hi = "\n".join(meta.get("header-includes", []))
    assert "\\usepackage{geometry}" not in hi
    assert "\\usepackage{pdflscape}" not in hi
    assert "Hello" in body


def test_add_geometry_package_yaml_header():
    text = "---\ntitle: Test\n---\ncontent"
    meta, _ = _parse(markdown_combiner.add_geometry_package(text))
    assert meta.get("title") == "Test"
    hi = "\n".join(meta.get("header-includes", []))
    assert "\\usepackage{geometry}" not in hi
    assert "\\usepackage{pdflscape}" not in hi


def test_add_geometry_package_existing_header_includes_with_metadata():
    text = (
        "---\n"
        "header-includes:\n"
        "  - \\usepackage{foo}\n"
        "author: Bob\n"
        "---\n"
        "Body"
    )
    meta, _ = _parse(markdown_combiner.add_geometry_package(text))
    hi = meta.get("header-includes", [])
    assert "\\usepackage{foo}" in hi
    assert all("\\usepackage{geometry}" not in line for line in hi)
    assert all("\\usepackage{pdflscape}" not in line for line in hi)
    assert meta.get("author") == "Bob"


def test_add_geometry_package_a4_landscape_enabled():
    text = "Hello"
    meta, _ = _parse(
        markdown_combiner.add_geometry_package(text, "a4-landscape")
    )  # noqa: E501
    opts = "\n".join(meta.get("geometry", []))
    assert "paperwidth=297mm" in opts
    assert "paperheight=210mm" in opts


def test_combine_markdown(tmp_path):
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("A", encoding="utf-8")
    f2.write_text("B", encoding="utf-8")
    combined = markdown_combiner.combine_markdown([str(f1), str(f2)])
    assert "A" in combined and "B" in combined
    assert "\\newpage" in combined


def test_combine_markdown_escapes_square_brackets(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("Value \\[m]", encoding="utf-8")
    combined = markdown_combiner.combine_markdown([str(f)])
    assert "\\[m]" not in combined
    assert "[m]" in combined


def test_normalize_md_handles_unicode_subscripts():
    text = "H₂O and $r₀$"
    normalized = markdown_combiner.normalize_md(text)
    assert "H$_2$O" in normalized
    assert "$r_{0}$" in normalized


def test_normalize_md_preserves_display_math():
    text = "Before \\[x\\] after"
    normalized = markdown_combiner.normalize_md(text)
    assert "\\[x\\]" in normalized


def test_normalize_md_handles_display_math_subscripts():
    text = "$$x₁$$"
    normalized = markdown_combiner.normalize_md(text)
    assert normalized == "$$x_{1}$$"
