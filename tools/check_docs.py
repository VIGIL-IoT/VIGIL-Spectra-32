"""Check repository Markdown links and repository-wide text hygiene."""

from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
REFERENCE_TARGET_PATTERN = re.compile(r"(?m)^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")
SKIP_PARTS = {".git", ".taste-skill", ".archify", ".venv", "node_modules"}
EM_DASH = chr(0x2014)
ENTITY_FORMS = ("&" + "mdash;", "&" + "#8212;", "&" + "#x2014;")
PERSONAL_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s<>\"']+", re.I),
    re.compile(re.escape("/" + "home" + "/") + r"[^/\s<>\"']+", re.I),
    re.compile(re.escape("/" + "Users" + "/") + r"[^/\s<>\"']+", re.I),
)


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    ]


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        try:
            contents = path.read_bytes()
            if b"\0" in contents:
                continue
            contents.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        files.append(path)
    return files


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
        errors.extend(check_markdown_targets(markdown, source))
    return errors


def check_markdown_targets(markdown: Path, source: str) -> list[str]:
    errors: list[str] = []
    matches = list(LINK_PATTERN.finditer(source))
    matches.extend(IMAGE_PATTERN.finditer(source))
    matches.extend(REFERENCE_TARGET_PATTERN.finditer(source))
    for match in matches:
        raw_target = next((group for group in match.groups() if group is not None), "").strip()
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


def text_policy_errors(relative_path: str, source: str) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if EM_DASH in line or any(entity in line.casefold() for entity in ENTITY_FORMS):
            errors.append(f"{relative_path}:{line_number}: forbidden em dash")
        if any(pattern.search(line) for pattern in PERSONAL_PATH_PATTERNS):
            errors.append(f"{relative_path}:{line_number}: personal machine path")
    return errors


def check_text_policy() -> list[str]:
    errors: list[str] = []
    for path in text_files():
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        errors.extend(text_policy_errors(path.relative_to(ROOT).as_posix(), source))
    return errors


def main() -> int:
    errors = check_links() + check_text_policy()
    if errors:
        print("Broken Markdown links:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Checked relative Markdown links in {len(markdown_files())} files and "
        f"text hygiene in {len(text_files())} repository files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
