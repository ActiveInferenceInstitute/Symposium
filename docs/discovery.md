# Method discovery and indexing

The [public methods hub](https://activeinferenceinstitute.github.io/Symposium/methods.html)
organizes tasks and links relevant public repositories. Its workflows and repository
searches run locally in the browser; every card and link remains available without
JavaScript. Filtered anchor navigation reveals the requested record before focusing it.

## One curated catalog

[`ecosystem.json`](../src/symposium/organizing/resources/ecosystem.json) is the reviewed
source for the hub, CLI and [integration document](integrations.md). Records include
stable IDs, integration roles, use cases, handoff limits, reviewed dates and README
evidence pinned to exact public commits. Dates record review, not live availability.
The validator checks the schema and provenance binding; it cannot prove that a
repository remains public, compatible, or scientifically suitable.

```bash
uv run symposium organize methods --format json
uv run symposium organize methods --format markdown
uv run symposium organize capabilities
```

Refresh the catalog when a relevant interface or source changes:

1. Verify the actual public repository owner/name, archival status and default revision.
   Read its README and the implementation needed to substantiate the proposed handoff.
2. Record a pinned evidence URL, checked date and bounded description. Distinguish an
   existing code integration from a manual handoff or reference resource. Preserve fork
   attribution and draft/adoption status. Exclude private repository/document handles.
3. Update repository/workflow records together, validate all references and inspect
   the generated Markdown and website. A catalog addition does not install an adapter.
4. Regenerate `docs/integrations.md` from `organize methods --format markdown`, review
   its diff and run the actual site/CLI/package checks before publishing.

## Published discovery surfaces

| File | Purpose |
|---|---|
| `index.html` | Approved program; canonical URL is the site directory |
| `methods.html` | Searchable methods/workflows and public repository handoffs |
| `ecosystem.json` | Versioned catalog with reviewed provenance |
| `search-index.json` | Methods, workflows, repository summaries and approved presentations |
| `sitemap.xml` | Canonical HTML page URLs, without fragment pseudo-pages or guessed modification dates |
| `llms.txt` | Source/reuse guidance and links for machine readers |

Both HTML pages include canonical/social metadata and safely escaped JSON-LD. Event
metadata uses approved event dates; it adds no inferred cost, attendance, location,
acceptance, credentials or scientific validation. Metadata is a description, not a
claim of rich-result eligibility. Participant self-reports are excluded from the
additional discovery index and Person structured data; the existing consented public
directory remains readable in the program.

The Python `build_site(..., site_url=...)` keyword supports another HTTPS directory.
The default is the GitHub Pages project URL. Invalid credentials, query/fragment and
traversal URL forms fail before output creation. Deploy a custom URL only after
checking its canonical page URLs and path prefixes against that deployment.

## Search engines and ownership

The sitemap makes page URLs available for discovery. A sitemap, structured metadata
or `llms.txt` does not guarantee crawling, indexing, ranking or use by an AI service.
Google documents [sitemap submission](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
and [owner/full-user indexing requests](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl).
Authenticated submission and URL inspection remain separate operational actions.

This is a project under `activeinferenceinstitute.github.io/Symposium/`. A
`robots.txt` placed inside the project directory would not control the host's root
robots policy. The build does not invent that authority or publish crawler rules for
unrelated Institute sites. Check the deployed site and authorized Search Console
property when confirming actual discovery; successful local rendering is not an
indexing receipt.
