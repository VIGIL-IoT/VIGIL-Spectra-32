"""Check repository Markdown for broken relative inline-link targets."""

from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SKIP_PARTS = {".git", ".taste-skill", ".archify", ".venv", "node_modules"}


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    ]


def remove_fenced_blocks(source: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for line in source.splitlines():
        marker = line.lstrip()
        if fence is None:
            if marker.startswith("```") or marker.startswith("~~~"):
                fence = marker[:3]
            else:
                lines.append(line)
        elif marker.startswith(fence):
            fence = None
    return "\n".join(lines)


def check_links() -> list[str]:
    errors: list[str] = []
    for markdown in markdown_files():
        source = remove_fenced_blocks(markdown.read_text(encoding="utf-8"))
        for match in LINK_PATTERN.finditer(source):
            raw_target = match.group(1).strip()
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            relative = Path(unquote(parsed.path))
            candidate = (markdown.parent / relative).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"{markdown.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{markdown.relative_to(ROOT)}: missing link target: {target}")
    return errors


def main() -> int:
    errors = check_links()
    if errors:
        print("Broken Markdown links:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Checked relative Markdown links in {len(markdown_files())} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
