"""Check the repository's documentation: relative links, docs index, gate arm list.

Runs offline with the standard library only. ``./gate.sh docs`` is the entry point
used by local runs and CI.

Checks:
  1. Every relative link in tracked Markdown resolves, outside archived/historical
     trees and generated output. Anchors are not resolved; only the target file.
  2. ``docs/documentation-index.md`` lists every Markdown file under ``docs/``.
  3. ``docs/_generated/gate-measurements.md`` lists exactly the arms that
     ``./gate.sh list`` reports, so a new arm cannot land undocumented.
"""

from __future__ import annotations

import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_EXCLUDES = ("archive/", "outputs/", ".venv/", ".gate/", "node_modules/", "htmlcov/")
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://", "data:")
FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
LINK = re.compile(r"\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[^)]*)?\)")
DEFINITION = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md", "*.MD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    paths = [Path(p) for p in out.decode("utf-8").split("\0") if p]
    return [p for p in paths if not str(p).startswith(SCAN_EXCLUDES)]


def links_in(text: str) -> list[str]:
    stripped = FENCE.sub("", text)
    stripped = HTML_COMMENT.sub("", stripped)
    stripped = INLINE_CODE.sub("", stripped)
    found = [m.group(1) for m in LINK.finditer(stripped)]
    found += [m.group(1) for m in DEFINITION.finditer(stripped)]
    return found


def resolve(source: Path, target: str) -> Path | None:
    """Return the local path a link points at, or None when it is not local."""
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target or target.startswith("#"):
        return None
    if target.lower().startswith(SKIP_SCHEMES):
        return None
    target = target.split("#", 1)[0]
    if not target:
        return None
    target = urllib.parse.unquote(target)
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()
    return (ROOT / source.parent / target).resolve()


def check_links(files: list[Path]) -> list[str]:
    broken: list[str] = []
    for rel in files:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for target in links_in(text):
            resolved = resolve(rel, target)
            if resolved is not None and not resolved.exists():
                broken.append(f"{rel}: {target}")
    return broken


def check_index() -> list[str]:
    index_path = ROOT / "docs" / "documentation-index.md"
    if not index_path.exists():
        return ["docs/documentation-index.md is missing"]
    referenced = {
        resolve(Path("docs/documentation-index.md"), t)
        for t in links_in(index_path.read_text(encoding="utf-8"))
    }
    documented = {
        (ROOT / p).resolve()
        for p in tracked_markdown()
        if str(p).startswith("docs/") and p.name != "documentation-index.md"
    }
    return [
        f"docs file not listed in docs/documentation-index.md: {p.relative_to(ROOT)}"
        for p in sorted(documented - referenced)
    ]


def check_gate_arms() -> list[str]:
    measurements = ROOT / "docs" / "_generated" / "gate-measurements.md"
    if not measurements.exists():
        return ["docs/_generated/gate-measurements.md is missing"]
    out = subprocess.run(
        ["./gate.sh", "list"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    arms = {line.strip() for line in out.splitlines() if line.strip()}
    text = measurements.read_text(encoding="utf-8")
    documented = {m.group(1) for m in re.finditer(r"^\|\s*`?([a-z][a-z-]*)`?\s*\|", text, re.M)}
    return [
        f"gate arm missing from docs/_generated/gate-measurements.md: {arm}"
        for arm in sorted(arms - documented)
    ]


def main() -> int:
    files = tracked_markdown()
    problems = check_links(files) + check_index() + check_gate_arms()
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(
            f"{len(problems)} documentation problem(s) in {len(files)} Markdown files",
            file=sys.stderr,
        )
        return 1
    print(
        f"documentation checks passed ({len(files)} Markdown files, "
        "relative links, docs index, gate arms)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
