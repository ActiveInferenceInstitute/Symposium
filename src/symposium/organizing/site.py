"""Render the approved public bundle as an offline-capable static explorer."""

from __future__ import annotations

import hashlib
import html
import re
import shutil
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import quote

from .models import canonical_bytes, validate_bundle


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _link(url: str, label: str, cls: str = "") -> str:
    return f'<a class="{cls}" href="{_escape(url)}">{_escape(label)}</a>' if url else ""


def _checked_file(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError("Unsafe asset path")
    candidate = root / path
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("Asset escapes input directory")
    if not candidate.is_file():
        raise ValueError(f"Missing asset: {relative}")
    return candidate


def build_site(
    bundle: Mapping,
    output_dir: Path,
    *,
    artifacts_dir: Path | None = None,
    assets_dir: Path | None = None,
) -> Path:
    """Build into an exclusively created directory; reject existing output.

    Validate all content and read allowlisted assets before creating output. The
    caller must publish only after this function returns successfully.
    """
    bundle = validate_bundle(dict(bundle))
    output_dir = Path(output_dir)
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(output_dir)
    copies: dict[str, bytes] = {"program.json": canonical_bytes(bundle)}
    images: dict[str, list[str]] = {}
    for item in bundle.get("presentations", []):
        images[item["id"]] = []
        for picture in item.get("pictures", []):
            if assets_dir is None:
                raise ValueError("Picture assets require assets_dir")
            source = _checked_file(Path(assets_dir), picture["path"])
            if source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError("Unsupported image type")
            content = source.read_bytes()
            if hashlib.sha256(content).hexdigest() != picture["sha256"]:
                raise ValueError("Picture hash mismatch")
            name = f"media/{picture['sha256']}{source.suffix.lower()}"
            copies[name] = content
            images[item["id"]].append(
                f'<img loading="lazy" src="{name}" alt="{_escape(picture["alt"])}">'
            )
    downloads: dict[str, str] = {}
    if artifacts_dir is not None:
        artifacts_dir = Path(artifacts_dir)
        names = ["book.pdf", "book.docx", "program.ics"]
        for item in bundle.get("presentations", []):
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", item["id"]):
                raise ValueError("Unsafe presentation ID")
            names.extend(f"dossiers/{item['id']}{ext}" for ext in (".pdf", ".docx", ".md"))
        names.extend(f"participants/{p['id']}.md" for p in bundle.get("participants", []))
        for name in names:
            if (artifacts_dir / name).exists() or (artifacts_dir / name).is_symlink():
                source = _checked_file(artifacts_dir, name)
                copies[f"downloads/{name}"] = source.read_bytes()
                downloads[name] = f"downloads/{name}"
    event = bundle["event"]
    actions = "".join(
        _link(event.get(key, ""), label, "button" if index == 0 else "")
        for index, (key, label) in enumerate(
            [
                ("participant_registration_url", "Register to participate"),
                ("presenter_registration_url", "Presenter registration"),
                ("program_url", "Official program"),
                ("community_url", "Join the community"),
                ("donate_url", "Support the Institute"),
            ]
        )
    )
    book_links = "".join(
        _link(downloads.get(name, ""), label)
        for name, label in [
            ("book.pdf", "Abstract book draft · PDF"),
            ("book.docx", "Abstract book draft · Word"),
            ("program.ics", "Add scheduled sessions · ICS"),
        ]
    )
    rows = []
    types = sorted({p.get("contribution_type", "") for p in bundle.get("presentations", [])} - {""})
    for p in bundle.get("presentations", []):
        dossiers = "".join(
            _link(downloads.get(f"dossiers/{p['id']}{ext}", ""), f"Dossier · {label}")
            for ext, label in [(".pdf", "PDF"), (".docx", "Word"), (".md", "Markdown")]
        )
        rows.append(f'''<details class="record" id="presentation-{_escape(p["id"])}" data-record data-category="{_escape(p.get("contribution_type", ""))}">
<summary><span class="eyebrow">{_escape(p.get("contribution_type", "Presentation"))}</span><h3>{_escape(p["title"])}</h3><span>{_escape(p["presenter"])}</span><span class="read-label">Read abstract</span></summary>
<div class="record-body"><div class="prose">{_escape(p["abstract"] or "No program abstract has been published for this presentation yet.")}</div><div class="pictures">{"".join(images[p["id"]])}</div><div class="cluster">{_link(p.get("source_url", ""), "Approved source")}{dossiers}<a href="#presentation-{quote(p["id"])}">Link to abstract</a></div></div></details>''')
    participant_rows = []
    fields = [
        ("background", "Background"),
        ("pragmatic_value", "Pragmatic value"),
        ("epistemic_value", "Epistemic value"),
        ("active_inference_application", "Applications of Active Inference"),
        ("challenges", "Challenges"),
        ("learning_needs", "Learning needs"),
        ("future_impact", "Future impact"),
    ]
    for p in bundle.get("participants", []):
        affiliations = p.get("affiliations", [])
        if isinstance(affiliations, list):
            affiliations = "; ".join(affiliations)
        content = "".join(
            f'<h4>{label}</h4><p class="prose">{_escape(p[key])}</p>'
            for key, label in fields
            if p.get(key)
        )
        orcid = p.get("orcid", "")
        brief = _link(
            downloads.get(f"participants/{p['id']}.md", ""), "Participant brief · Markdown"
        )
        participant_rows.append(
            f'<details class="record" data-record id="participant-{_escape(p["id"])}"><summary><h3>{_escape(p["name"])}</h3><span>{_escape(affiliations)}</span><span class="read-label">Explore profile</span></summary><div class="record-body">{content}{_link(orcid if orcid.startswith("https://") else "https://orcid.org/" + orcid, "ORCID") if orcid else ""}<div class="cluster">{brief}</div></div></details>'
        )
    sessions = []
    for s in bundle.get("sessions", []):
        sessions.append(
            f'<article class="session"><div><time datetime="{_escape(s["start_utc"])}">{_escape(s["start_utc"])} UTC</time><span> — </span><time datetime="{_escape(s["end_utc"])}">{_escape(s["end_utc"])} UTC</time></div><h3>{_escape(s["title"] or "Session title not yet published")}</h3><p>{_escape(s.get("presenter", ""))} · {_escape(s.get("kind", ""))}</p></article>'
        )
    resources = "".join(
        f'<article class="resource"><p class="eyebrow">{_escape(r.get("category", ""))}</p><h3>{_link(r["url"], r["title"])}</h3><p>{_escape(r.get("description", ""))}</p></article>'
        for r in bundle.get("resources", [])
    )
    livestreams = "".join(
        _link(item["url"], item["title"]) for item in event.get("livestreams", [])
    )

    def filters(prefix: str, categories: list[str] | None = None) -> str:
        select = (
            '<label>Contribution type<select data-category-filter><option value="">All types</option>'
            + "".join(f"<option>{_escape(t)}</option>" for t in categories or [])
            + "</select></label>"
            if categories
            else ""
        )
        return f'<div class="filters" data-enhancement hidden><label>Search {prefix}<input type="search" data-search placeholder="Name, topic, or phrase"></label>{select}<button type="button" data-reset>Reset filters</button><p role="status" data-count></p></div><p data-empty hidden>No matches. Try another phrase or reset the filters.</p>'

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Explore approved Symposium abstracts, participant profiles, scheduled sessions and Institute resources."><title>{_escape(event["title"])} · Active Inference Institute</title><link rel="stylesheet" href="static/site.css"><script src="static/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="masthead"><a class="brand" href="#main">Active Inference Institute<span>Symposium</span></a><nav aria-label="Main navigation"><a href="#presentations">Presentations</a><a href="#participants">Participants</a><a href="#schedule">Schedule</a><a href="#resources">Resources</a></nav></header>
<main id="main"><section class="intro"><p class="eyebrow">Annual Symposium</p><h1>{_escape(event["title"])}</h1><p class="dates">{_escape(event["start_date"])} — {_escape(event["end_date"])} · UTC</p><p class="lead">Online and free to attend. November 12–13, 2026 (UTC).</p><div class="cluster actions">{actions}</div><div class="cluster downloads">{book_links}<a href="program.json" download>Program data · JSON</a></div></section>
<section id="presentations" data-filter-group><div class="section-heading"><p class="eyebrow">The research</p><h2>Presentations & abstracts</h2><p>Full abstracts from the approved program. Open a presentation to read and explore its sources.</p></div>{filters("presentations", types)}{"".join(rows) or "<p>No approved presentations published yet.</p>"}</section>
<section id="participants" data-filter-group><div class="section-heading"><p class="eyebrow">The community</p><h2>Participant directory</h2><p>Self-reported interests, applications, and learning needs shared for this public directory.</p></div>{filters("participants")}{"".join(participant_rows) or "<p>No approved participant profiles published yet.</p>"}</section>
<section id="schedule"><div class="section-heading"><p class="eyebrow">Gather together</p><h2>Schedule & live sessions</h2><p>Only explicitly scheduled sessions are shown. Abstracts do not imply a speaking time.</p></div>{'<label data-enhancement hidden>Display times in <select id="timezone"><option value="UTC">UTC</option><option value="local">Your local timezone</option></select></label>' if sessions else ""}{"".join(sessions) or "<p>Session times have not been published in this bundle. See the official program for updates.</p>"}<div class="cluster">{livestreams}</div></section>
<section id="resources"><div class="section-heading"><p class="eyebrow">Keep exploring</p><h2>Institute methods & resources</h2></div><div class="resource-grid">{resources or "<p>No resources published in this bundle.</p>"}</div></section></main>
<footer><p>Active Inference Institute · Act. Infer. Serve.</p><p>Public program snapshot · {_escape(event["year"])}. Presenter abstracts and participant profiles are self-reported, approved public content. Refer to the official program for revisions.</p><a href="#main">Back to top</a></footer></body></html>"""
    output_dir.mkdir(parents=True, exist_ok=False)
    for name, content in copies.items():
        target = output_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    static = output_dir / "static"
    static.mkdir()
    for name in ("site.css", "site.js"):
        shutil.copyfile(Path(__file__).parent / "static" / name, static / name)
    (output_dir / ".nojekyll").touch()
    index = output_dir / "index.html"
    index.write_text(document, encoding="utf-8")
    return index
