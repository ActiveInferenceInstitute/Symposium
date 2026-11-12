"""Check the repository's documentation: relative links, docs index, gate arm list.

Runs offline with the standard library only. ``./gate.sh docs`` is the entry point
used by local runs and CI.

Checks:
  1. Every relative link in tracked Markdown resolves, outside archived/historical
     trees and generated output. Fenced blocks (backtick or tilde), inline code
     spans, HTML comments and raw HTML are not treated as links. Anchors are not
     resolved; only the target file.
  2. ``docs/documentation-index.md`` lists every Markdown file under ``docs/``.
  3. The current arm table in ``docs/_generated/gate-measurements.md`` names exactly
     the arms that ``./gate.sh list`` reports, in both directions, so a new or
     removed arm cannot land undocumented. Historical tables are ignored.
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
INDEX_REL = "docs/documentation-index.md"
MEASUREMENTS_REL = "docs/_generated/gate-measurements.md"
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
REFERENCE = re.compile(r"^[ ]{0,3}\[[^\]]+\]:[ \t]*(?:\n[ \t]*)?(<[^>]*>|\S+)", re.MULTILINE)
ARM_HEADER = "| Arm | Status |"


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md", "*.MD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    paths = [Path(p) for p in out.decode("utf-8").split("\0") if p]
    return [p for p in paths if not p.as_posix().startswith(SCAN_EXCLUDES)]


def strip_inline_code(text: str) -> str:
    """Blank inline code spans, matching backtick runs of exactly equal length."""
    out = []
    index = 0
    while index < len(text):
        if text[index] != "`":
            out.append(text[index])
            index += 1
            continue
        run_end = index
        while run_end < len(text) and text[run_end] == "`":
            run_end += 1
        run = run_end - index
        probe = run_end
        closing = -1
        while probe < len(text):
            if text[probe] != "`":
                probe += 1
                continue
            candidate_end = probe
            while candidate_end < len(text) and text[candidate_end] == "`":
                candidate_end += 1
            if candidate_end - probe == run:
                closing = probe
                break
            probe = candidate_end
        if closing == -1:
            out.append(text[index:run_end])
            index = run_end
            continue
        out.append(" ")
        index = closing + run
    return "".join(out)


def strip_code(text: str) -> str:
    """Blank out fenced blocks, inline code spans and HTML comments."""
    kept = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" \t")
        indent = len(line) - len(stripped)
        match = FENCE_OPEN.match(stripped)
        if fence is None:
            if indent <= 3 and match:
                fence = (match.group(1)[0], len(match.group(1)))
                kept.append("\n")
                continue
            kept.append(line)
            continue
        if (
            indent <= 3
            and match
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= fence[1]
            and stripped.strip() == match.group(1)
        ):
            fence = None
        kept.append("\n")
    return strip_inline_code(HTML_COMMENT.sub("", "".join(kept)))


def _paragraph_end(text: str, start: int) -> int:
    """Return the index of the blank line that ends this paragraph, or the text end."""
    match = re.compile(r"\n[ \t]*\n").search(text, start)
    return match.start() if match else len(text)


def _skip_link_tail(text: str, cursor: int) -> int:
    """Return the index just past a link's optional title and closing parenthesis.

    A malformed tail (unterminated quote or parenthesis, or a close that falls in a
    later paragraph) is not allowed to consume the rest of the document: the scan
    resumes at ``cursor`` so later links are still checked.
    """
    limit = _paragraph_end(text, cursor)
    probe = cursor
    while probe < limit and text[probe].isspace():
        probe += 1
    if probe < limit and text[probe] in "\"'":
        end = text.find(text[probe], probe + 1)
        if end == -1 or end > limit:
            return cursor
        probe = end + 1
    elif probe < limit and text[probe] == "(":
        depth = 0
        while probe < limit:
            if text[probe] == "(":
                depth += 1
            elif text[probe] == ")":
                depth -= 1
                if depth == 0:
                    probe += 1
                    break
            probe += 1
        if depth != 0:
            return cursor
    close = text.find(")", probe)
    if close == -1 or close > limit:
        return cursor
    return close + 1


def inline_destinations(text: str) -> list[str]:
    """Yield link destinations, honouring <angle> targets and nested parentheses."""
    found = []
    index = 0
    while True:
        start = text.find("](", index)
        if start == -1:
            return found
        cursor = start + 2
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor < len(text) and text[cursor] == "<":
            end = text.find(">", cursor + 1)
            if end == -1:
                index = start + 2
                continue
            found.append(text[cursor + 1 : end])
            index = _skip_link_tail(text, end + 1)
            continue
        depth = 0
        begin = cursor
        while cursor < len(text):
            char = text[cursor]
            if char == "\\":
                cursor += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            cursor += 1
        found.append(text[begin:cursor])
        index = _skip_link_tail(text, cursor)


def links_in(text: str) -> list[str]:
    body = strip_code(text)
    found = inline_destinations(body)
    for match in REFERENCE.finditer(body):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        found.append(target)
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
    target = target.split("#", 1)[0].split("?", 1)[0]
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
    index_path = ROOT / INDEX_REL
    if not index_path.exists():
        return [f"{INDEX_REL} is missing"]
    referenced = {resolve(Path(INDEX_REL), t) for t in links_in(index_path.read_text("utf-8"))}
    documented = {
        (ROOT / path).resolve()
        for path in tracked_markdown()
        if path.as_posix().startswith("docs/") and path.as_posix() != INDEX_REL
    }
    return [
        f"docs file not listed in {INDEX_REL}: {path.relative_to(ROOT)}"
        for path in sorted(documented - referenced)
    ]


def current_arm_rows(text: str) -> set[str]:
    """Arm names in the first (current-run) table only, excluding history tables."""
    rows: set[str] = set()
    inside = False
    for line in text.splitlines():
        if line.startswith(ARM_HEADER):
            inside = True
            continue
        if not inside:
            continue
        if not line.startswith("|"):
            break
        cell = line.strip().strip("|").split("|")[0].strip().strip("`").strip()
        if cell and not set(cell) <= {"-", " "}:
            rows.add(cell)
    return rows


def check_gate_arms() -> list[str]:
    measurements = ROOT / MEASUREMENTS_REL
    if not measurements.exists():
        return [f"{MEASUREMENTS_REL} is missing"]
    out = subprocess.run(
        ["./gate.sh", "list"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    expected = {line.strip() for line in out.splitlines() if line.strip()}
    documented = current_arm_rows(measurements.read_text(encoding="utf-8"))
    problems = [
        f"gate arm missing from the current table in {MEASUREMENTS_REL}: {arm}"
        for arm in sorted(expected - documented)
    ]
    problems += [
        f"stale gate arm in the current table in {MEASUREMENTS_REL}: {arm}"
        for arm in sorted(documented - expected)
    ]
    return problems


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
