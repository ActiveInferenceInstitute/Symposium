"""Static discovery from the public bundle and curated repository catalog."""

from __future__ import annotations

import html
import json
import re
from typing import Final
from urllib.parse import quote, unquote, urlsplit

from .ecosystem import Catalog, load_catalog
from .models import PublicationError, PublicBundle, canonical_bytes

SITE_URL: Final = "https://activeinferenceinstitute.github.io/Symposium/"


def canonical_base(value: str) -> str:
    """Accept an HTTPS site directory without credentials or traversal."""
    parts = urlsplit(value)
    decoded = unquote(parts.path)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or "?" in value
        or "#" in value
        or re.search(r"[\s\\\x00-\x1f\x7f]", value)
        or re.search(r"[\\\x00-\x1f\x7f%]", decoded)
        or any(part in {".", ".."} for part in decoded.split("/"))
        or "//" in decoded
        or decoded.rstrip("/").endswith((".html", ".htm", ".json", ".xml"))
    ):
        raise PublicationError(
            "site_url must be an HTTPS directory without credentials, query, fragment or traversal"
        )
    try:
        parts.port
    except ValueError as exc:
        raise PublicationError("site_url has an invalid port") from exc
    return value.rstrip("/") + "/"


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def metadata(title: str, description: str, url: str, schema: dict[str, str]) -> str:
    """Escape attributes and JSON script data in their distinct contexts."""
    data = json.dumps({"@context": "https://schema.org", **schema}, ensure_ascii=True)
    data = data.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return f'''<link rel="canonical" href="{_escape(url)}">
<meta property="og:type" content="website"><meta property="og:title" content="{_escape(title)}"><meta property="og:description" content="{_escape(description)}"><meta property="og:url" content="{_escape(url)}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{_escape(title)}"><meta name="twitter:description" content="{_escape(description)}">
<link rel="alternate" type="application/json" href="ecosystem.json" title="Methods catalog"><link rel="alternate" type="application/json" href="search-index.json" title="Public discovery index">
<script type="application/ld+json">{data}</script>'''


def event_metadata(bundle: PublicBundle, base: str) -> str:
    event = bundle["event"]
    return metadata(
        event["title"],
        "Approved Symposium program and public research methods.",
        base,
        {
            "@type": "Event",
            "name": event["title"],
            "url": base,
            "startDate": event["start_date"],
            "endDate": event["end_date"],
        },
    )


def _filters(name: str) -> str:
    return f'''<div class="filters" data-enhancement hidden><label>Search {name}<input id="{name}-search" type="search" data-search aria-describedby="{name}-help" placeholder="Task, command or topic"></label><button type="button" data-reset>Reset filters</button><p class="search-help" id="{name}-help">All search words must match; word order does not matter.</p><p role="status" data-count></p></div><p data-empty hidden>No matches. Try fewer words or reset the filters.</p>'''


def _methods(catalog: Catalog, base: str) -> str:
    roles = {
        "code-integration": "Native render integration",
        "manual-handoff": "Manual handoff",
        "resource": "Reading resource",
    }
    credential_labels = {
        "openrouter": "OpenRouter API key",
        "perplexity": "Perplexity API key",
        "instituteos-docs": "Superhuman Docs MCP token",
    }
    jumps = "".join(
        f'<a href="#workflow-{_escape(w["id"])}">{_escape(w["title"])}</a>'
        for w in catalog["workflows"]
    )
    workflows = []
    for workflow in catalog["workflows"]:
        commands = "".join(
            f"<li><code>uv run {_escape(command)}</code></li>" for command in workflow["commands"]
        )
        repositories = "".join(
            f'<a href="#repository-{_escape(key)}">{_escape(key)}</a>'
            for key in workflow["repository_ids"]
        )
        credentials = (
            ", ".join(credential_labels[key] for key in workflow["credential_ids"]) or "None"
        )
        workflows.append(
            f'''<article class="resource workflow" data-record tabindex="-1" id="workflow-{_escape(workflow["id"])}"><h3>{_escape(workflow["title"])}</h3><p>{_escape(workflow["summary"])}</p><ul>{commands}</ul><p><strong>Credential requirements:</strong> {_escape(credentials)}</p><div class="cluster"><a href="{_escape(workflow["docs_url"])}">Workflow documentation</a>{repositories}</div></article>'''
        )
    repositories = []
    for repository in catalog["repositories"]:
        repositories.append(
            f'''<article class="resource" data-record tabindex="-1" id="repository-{_escape(repository["id"])}"><p class="eyebrow">{_escape(roles[repository["role"]])}</p><h3><a href="{_escape(repository["repository_url"])}">{_escape(repository["name"])}</a></h3><p>{_escape(repository["summary"])}</p><p><strong>Use for:</strong> {_escape(repository["use_for"])}</p><p><strong>Handoff:</strong> {_escape(repository["handoff"])}</p><p>Source checked {_escape(repository["checked_on"])} · commit <code>{_escape(repository["commit"])}</code></p><div class="cluster"><a href="{_escape(repository["evidence_url"])}">Inspect pinned source evidence</a></div></article>'''
        )
    head = metadata(
        "Methods & workflows · Symposium",
        "Symposium workflows and curated public Institute repository handoffs.",
        base + "methods.html",
        {
            "@type": "CollectionPage",
            "name": "Symposium methods and workflows",
            "url": base + "methods.html",
        },
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Symposium workflows, credentials and curated public Institute repositories."><title>Methods &amp; workflows · Symposium</title><link rel="icon" href="static/favicon.svg"><link rel="stylesheet" href="static/site.css"><script src="static/site.js" defer></script>{head}</head>
<body><a class="skip" href="#main">Skip to content</a><header class="masthead"><a class="brand" href="index.html">Active Inference Institute<span>Symposium</span></a><nav aria-label="Main navigation"><a href="index.html">Program</a><a href="#workflows">Workflows</a><a href="#repositories">Repositories</a><a href="#boundaries">Credentials &amp; limits</a></nav></header>
<main id="main"><section class="intro"><p class="eyebrow">From program to practice</p><h1>Methods &amp; workflows</h1><p>Choose a task, inspect its commands, and follow the public sources. Repository handoffs require your review and execution.</p><div class="cluster"><a class="button" href="#workflows">Choose a workflow</a><a href="index.html#presentations">Explore presentations</a></div></section>
<section id="workflows" data-filter-group><div class="section-heading"><h2>Choose a workflow</h2><p>Commands run in a local Symposium installation, not in this browser. Consult the linked documentation for inputs and setup.</p></div><nav class="workflow-jumps" aria-label="Workflow shortcuts">{jumps}</nav>{_filters("workflows")}<div class="methods-stack">{"".join(workflows)}</div></section>
<section id="repositories" data-filter-group><div class="section-heading"><h2>Public repository handoffs</h2><p>Evidence is pinned to a reviewed revision. A listing does not demonstrate an installed integration, compatibility, or successful cross-repository execution.</p></div>{_filters("repositories")}<div class="resource-grid">{"".join(repositories)}</div></section>
<section id="boundaries"><div class="section-heading"><h2>Credentials &amp; limits</h2><p><a href="https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/credentials.md">Credential setup and access guide</a></p><p>This static site needs no API credentials and makes no model calls. Optional CLI workflows may require provider accounts, credentials and paid usage. OpenRouter and Perplexity refer to separate provider API credentials. InstituteOS documentation access is a separate, restricted documentation boundary; this public catalog grants no access.</p><p>Review workflow documentation before running commands. Keep secrets in your local environment; never put keys or private source data in public bundles, catalogs or generated files.</p><p>The catalog was reviewed on {_escape(catalog["reviewed_on"])}. It is a curated snapshot, not a live inventory. Manual handoffs do not synchronize data or authorize publication. Organizers must approve public material separately.</p><p>The discovery index contains methods, workflows and approved presentations. It excludes participant self-reports; the approved public directory remains in the program. Metadata does not independently verify research claims.</p></div><div class="cluster"><a href="ecosystem.json">Methods catalog · JSON</a><a href="search-index.json">Discovery index · JSON</a><a href="llms.txt">Source and reuse guidance</a><a href="sitemap.xml">Page sitemap</a></div></section></main><footer><p>Active Inference Institute · Act. Infer. Serve.</p><a href="index.html">Return to the public program</a></footer></body></html>"""


def discovery_files(bundle: PublicBundle, base: str) -> dict[str, bytes]:
    """Read validated catalog and render discovery bytes before output creation."""
    catalog = load_catalog()
    methods = _methods(catalog, base)
    entries = [
        {
            "id": "methods",
            "kind": "methods",
            "title": "Methods & workflows",
            "url": "methods.html",
            "text": "Curated public Institute repositories and local Symposium workflows.",
        }
    ]
    entries.extend(
        {
            "id": w["id"],
            "kind": "workflow",
            "title": w["title"],
            "url": "methods.html#workflow-" + quote(w["id"]),
            "text": w["summary"],
        }
        for w in catalog["workflows"]
    )
    entries.extend(
        {
            "id": r["id"],
            "kind": "repository",
            "title": r["name"],
            "url": "methods.html#repository-" + quote(r["id"]),
            "text": r["summary"],
        }
        for r in catalog["repositories"]
    )
    entries.extend(
        {
            "id": p["id"],
            "kind": "presentation",
            "title": p["title"],
            "url": "index.html#presentation-" + quote(p["id"]),
            "text": p["abstract"],
        }
        for p in bundle["presentations"]
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{_escape(base + page)}</loc></url>" for page in ("", "methods.html"))
        + "</urlset>\n"
    )
    guidance = f"""# Symposium public sources

This static, organizer-approved snapshot is not live synchronization or independent research verification. Consult the official program for revisions. Do not infer attendance, credentials, endorsement, or scientific validity from inclusion.

- [Program]({base}index.html): approved presentations, explicit schedule and public directory.
- [Methods]({base}methods.html): local workflows, credential boundaries and manual repository handoffs.
- [Catalog]({base}ecosystem.json): curated repository evidence pinned to reviewed revisions.
- [Discovery index]({base}search-index.json): methods and approved presentations; excludes participant self-reports.
- [Official program]({bundle["event"]["program_url"]}): organizer revision authority.

Participant profiles are consented self-reports, not independently verified biographies. Avoid enriching or inferring personal facts. Private source records, credentials and unapproved data are outside this snapshot. Catalog review date: {catalog["reviewed_on"]}. This guidance does not control crawler access or guarantee indexing.
"""
    return {
        "methods.html": methods.encode(),
        "ecosystem.json": canonical_bytes(catalog),
        "search-index.json": canonical_bytes({"schema_version": 1, "entries": entries}),
        "sitemap.xml": sitemap.encode(),
        "llms.txt": guidance.encode(),
    }
