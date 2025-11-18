import shutil

import pandas as pd


# Import von der Root des .github-Pakets
import tools.converter.convert_assets as convert_assets
from tools.converter.convert_assets import convert_csv
from tools.converter.csv2md_and_chart import save_chart, save_markdown


def test_csv_to_md_and_chart(output_dir, artifact_dir, logger):
    df = pd.DataFrame({"name": ["Alpha", "Beta"], "value": [1, 2]})
    md_out = output_dir / "table.md"
    png_out = output_dir / "chart.png"
    save_markdown(df, md_out, title="Title", note="Note")
    save_chart(df, png_out, x="name", y_cols=["value"])
    logger.info("Generated markdown and chart")
    assert md_out.is_file()
    content = md_out.read_text(encoding="utf-8")
    assert "Alpha" in content and "Beta" in content
    assert png_out.is_file()
    shutil.copy(md_out, artifact_dir / md_out.name)
    shutil.copy(png_out, artifact_dir / png_out.name)


def test_convert_assets(
    tmp_path,
    monkeypatch,
    output_dir,
    artifact_dir,
    logger,
):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("name,value\nA,1\nB,2\n", encoding="utf-8")
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "table.md").write_text("{table}", encoding="utf-8")
    monkeypatch.setattr(convert_assets, "TEMPLATES", template_dir)
    assets_dir = output_dir / "assets"
    convert_csv(csv_path, assets_dir)
    out_md = assets_dir / "tables" / "data.md"
    out_png = assets_dir / "diagrams" / "data.png"
    logger.info("Converted CSV to assets")
    assert out_md.is_file()
    out_text = out_md.read_text(encoding="utf-8")
    assert "A" in out_text and "B" in out_text
    assert out_png.is_file()
    shutil.copy(out_md, artifact_dir / out_md.name)
    shutil.copy(out_png, artifact_dir / out_png.name)
