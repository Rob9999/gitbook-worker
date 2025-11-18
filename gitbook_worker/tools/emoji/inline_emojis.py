"""Replace emoji characters in HTML with inline SVG/PNG assets."""

from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from .emoji_utils import (
    emoji_cldr_name,
    emoji_to_slug,
    iter_emoji_sequences,
)

TWEMOJI_VERSION = "14.0.2"
TWEMOJI_SVG = (
    f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/{TWEMOJI_VERSION}/svg/{{slug}}.svg"
)
TWEMOJI_PNG = (
    f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/{TWEMOJI_VERSION}/72x72/{{slug}}.png"
)
OPENMOJI_BLACK = (
    "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/black/svg/{slug_upper}.svg"
)
CACHE_DIR = Path("build/emoji-assets")

SKIP_PARENTS = {"script", "style", "code", "pre", "kbd", "samp"}


@dataclass
class EmojiAsset:
    kind: str  # "svg" or "png"
    content: str  # raw SVG markup or base64 encoded PNG
    source: str  # provider identifier


class EmojiAssetFetcher:
    def __init__(self, prefer: str = "twemoji") -> None:
        self.prefer = prefer
        self.cache: Dict[str, Optional[EmojiAsset]] = {}
        self.stats: Dict[str, int] = {"twemoji_svg": 0, "twemoji_png": 0, "openmoji": 0}
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def fetch(self, emoji: str) -> Optional[EmojiAsset]:
        if emoji in self.cache:
            return self.cache[emoji]

        slug = emoji_to_slug(emoji)
        providers = self._provider_order()
        asset: Optional[EmojiAsset] = None
        for provider in providers:
            if provider == "twemoji_svg":
                asset = self._fetch_twemoji_svg(slug)
            elif provider == "twemoji_png":
                asset = self._fetch_twemoji_png(slug)
            elif provider == "openmoji":
                asset = self._fetch_openmoji(slug)
            if asset:
                self.stats[provider] += 1
                break
        if asset is None:
            self.cache[emoji] = None
            return None
        self.cache[emoji] = asset
        return asset

    def _provider_order(self) -> List[str]:
        if self.prefer == "openmoji":
            return ["openmoji", "twemoji_svg", "twemoji_png"]
        return ["twemoji_svg", "twemoji_png", "openmoji"]

    def _fetch_twemoji_svg(self, slug: str) -> Optional[EmojiAsset]:
        for candidate in self._slug_variants(slug):
            asset = self._download_asset(
                TWEMOJI_SVG.format(slug=candidate),
                candidate,
                suffix=".svg",
                kind="svg",
                source="twemoji_svg",
            )
            if asset:
                return asset
        return None

    def _fetch_twemoji_png(self, slug: str) -> Optional[EmojiAsset]:
        for candidate in self._slug_variants(slug):
            asset = self._download_asset(
                TWEMOJI_PNG.format(slug=candidate),
                candidate,
                suffix=".png",
                kind="png",
                source="twemoji_png",
            )
            if asset:
                return asset
        return None

    def _fetch_openmoji(self, slug: str) -> Optional[EmojiAsset]:
        for candidate in self._slug_variants(slug):
            asset = self._download_asset(
                OPENMOJI_BLACK.format(slug_upper=candidate.upper()),
                candidate,
                suffix=".svg",
                kind="svg",
                source="openmoji",
            )
            if asset:
                return asset
        return None

    def _download_asset(
        self,
        url: str,
        slug: str,
        *,
        suffix: str,
        kind: str,
        source: str,
    ) -> Optional[EmojiAsset]:
        cache_file = CACHE_DIR / f"{source}_{slug}{suffix}"
        if cache_file.exists():
            data = cache_file.read_bytes()
        else:
            try:
                response = requests.get(url, timeout=10)
            except requests.RequestException:
                return None
            if response.status_code != 200:
                return None
            data = response.content
            cache_file.write_bytes(data)
        if kind == "svg":
            return EmojiAsset(kind="svg", content=data.decode("utf-8"), source=source)
        return EmojiAsset(kind="png", content=base64.b64encode(data).decode("ascii"), source=source)

    @staticmethod
    def _slug_variants(slug: str) -> List[str]:
        variants = [slug]
        simplified = "-".join(part for part in slug.split("-") if part != "fe0f")
        if simplified and simplified not in variants:
            variants.append(simplified)
        return variants


class EmojiInliner:
    def __init__(self, prefer: str = "twemoji", asset_fetcher: Optional[EmojiAssetFetcher] = None) -> None:
        self.asset_fetcher = asset_fetcher or EmojiAssetFetcher(prefer=prefer)
        self.replaced = 0
        self.total = 0
        self.missing: Dict[str, int] = {}
        self._soup: Optional[BeautifulSoup] = None

    def process_soup(self, soup: BeautifulSoup) -> None:
        self._soup = soup
        for text_node in list(soup.find_all(string=True)):
            if isinstance(text_node, NavigableString) and text_node.parent.name not in SKIP_PARENTS:
                self._process_text_node(text_node)

    def _split_text(self, text: str) -> List[Dict[str, str]]:
        segments: List[Dict[str, str]] = []
        cursor = 0
        for match in iter_emoji_sequences(text):
            index = text.find(match, cursor)
            if index == -1:
                continue
            if index > cursor:
                segments.append({"type": "text", "value": text[cursor:index]})
            segments.append({"type": "emoji", "value": match})
            cursor = index + len(match)
        if cursor < len(text):
            segments.append({"type": "text", "value": text[cursor:]})
        return segments

    def _process_text_node(self, node: NavigableString) -> None:
        text = str(node)
        segments = self._split_text(text)
        if not any(segment["type"] == "emoji" for segment in segments):
            return
        parent = node.parent
        current = node
        for idx, segment in enumerate(segments):
            if segment["type"] == "text":
                new_node: Tag | NavigableString = NavigableString(segment["value"])
            else:
                emoji_char = segment["value"]
                self.total += 1
                replacement = self._create_emoji_tag(parent, emoji_char)
                if replacement is None:
                    self.missing[emoji_char] = self.missing.get(emoji_char, 0) + 1
                    new_node = NavigableString(emoji_char)
                else:
                    new_node = replacement
                    self.replaced += 1
            if idx == 0:
                current.replace_with(new_node)
                current = new_node
            else:
                current.insert_after(new_node)
                current = new_node

    def _create_emoji_tag(self, parent: Tag, emoji_char: str) -> Optional[Tag]:
        asset = self.asset_fetcher.fetch(emoji_char)
        if not asset:
            return None
        factory = self._soup or parent
        span = factory.new_tag("span")
        span["class"] = ["emoji"]
        span["data-emoji"] = emoji_char
        span["title"] = emoji_cldr_name(emoji_char)
        span["data-source"] = asset.source
        if asset.kind == "svg":
            svg_fragment = BeautifulSoup(asset.content, "html.parser")
            svg_tag = svg_fragment.find("svg")
            if svg_tag:
                span.append(svg_tag)
            else:
                span.append(svg_fragment)
        else:
            img = factory.new_tag("img")
            img["src"] = f"data:image/png;base64,{asset.content}"
            img["alt"] = emoji_char
            span.append(img)
        return span

    def coverage(self) -> Dict[str, object]:
        ratio = 1.0 if self.total == 0 else self.replaced / self.total
        return {
            "total": self.total,
            "replaced": self.replaced,
            "ratio": ratio,
            "missing": self.missing,
            "stats": self.asset_fetcher.stats,
        }


def ensure_css(soup: BeautifulSoup, css_path: Optional[str]) -> None:
    if not css_path:
        return
    path = Path(css_path)
    if not path.exists():
        raise FileNotFoundError(f"CSS-Datei {css_path} nicht gefunden")
    css_content = path.read_text(encoding="utf-8")
    head = soup.head
    if not head:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)
    style_tag = soup.new_tag("style")
    style_tag.string = css_content
    style_tag["data-origin"] = str(path)
    head.append(style_tag)


def inline_file(
    input_path: Path,
    output_path: Path,
    *,
    prefer: str = "twemoji",
    css_path: Optional[str] = None,
    coverage_path: Optional[Path] = None,
    asset_fetcher: Optional[EmojiAssetFetcher] = None,
) -> Dict[str, object]:
    html = input_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    ensure_css(soup, css_path)

    if os.environ.get("EMOJI_INLINING", "on").lower() == "off":
        output_path.write_text(str(soup), encoding="utf-8")
        coverage = {
            "total": 0,
            "replaced": 0,
            "ratio": 0.0,
            "missing": {},
            "stats": {},
            "disabled": True,
        }
        if coverage_path:
            coverage_path.parent.mkdir(parents=True, exist_ok=True)
            coverage_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")
        return coverage

    inliner = EmojiInliner(prefer=prefer, asset_fetcher=asset_fetcher)
    inliner.process_soup(soup)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(soup), encoding="utf-8")
    coverage = inliner.coverage()
    if coverage_path:
        coverage_path.parent.mkdir(parents=True, exist_ok=True)
        coverage_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    return coverage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input", required=True, help="Input HTML file")
    parser.add_argument("--out", dest="output", required=True, help="Output HTML file")
    parser.add_argument(
        "--prefer",
        choices=["twemoji", "openmoji"],
        default="twemoji",
        help="Primary emoji asset source",
    )
    parser.add_argument("--css", help="CSS file to inline for .emoji styles")
    parser.add_argument(
        "--coverage",
        help="Path to coverage JSON output (replaced vs total)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    coverage_path = Path(args.coverage) if args.coverage else None
    coverage = inline_file(
        input_path,
        output_path,
        prefer=args.prefer,
        css_path=args.css,
        coverage_path=coverage_path,
    )
    ratio = coverage.get("ratio", 0.0)
    print(
        f"Inline-Coverage: {coverage.get('replaced', 0)} / {coverage.get('total', 0)} = {ratio:.3f}"
    )


if __name__ == "__main__":
    main()
