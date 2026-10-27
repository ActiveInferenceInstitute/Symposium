# Public program and organizer publication

The 2026 Symposium is online and free, November 12–13 (UTC). The Pages explorer
publishes approved program abstracts and consented participant answers, with
available presenter dossiers, participant briefs, an abstract book, and explicit
session times. It needs no paid AI calls. Existing analysis and generation commands
remain optional, separate workflows; their generated claims do not enter this
public projection automatically.

## Public build

The deployment input is `data/public/2026/`. It contains `program.json`, the
`publication.json` hash manifest, approved images under `assets/portraits/`, and
allowlisted artifacts at the public root: `book.pdf`, `book.docx`, `program.ics`,
`dossiers/<public-id>.md`, and `participants/<public-id>.md` when available.

```python
from pathlib import Path
from symposium.organizing.publication import verify_public_tree
from symposium.organizing.site import build_site

public_root = Path("data/public/2026")
bundle = verify_public_tree(public_root)
build_site(bundle, Path("_site"), assets_dir=public_root, artifacts_dir=public_root)
```

Run this with `uv run --no-sync python` after `uv sync --locked`. Use a new output
directory: the builder refuses overwrite. Verification rejects unexpected files,
symlinks, digest mismatches, forbidden fields, unsafe URLs, and malformed artifacts.
The site copies only named downloads and approved, hash-verified pictures. Raw
snapshots, private approval ledgers, transport receipts, and organizer credentials
never belong in this directory or Pages artifacts.

The generated HTML contains the full readable content. Native disclosure controls
work without JavaScript. JavaScript adds search, contribution-type filtering, reset,
result counts, anchor expansion, and UTC/local timezone display. Relative links
work under the `/Symposium/` project path. Download links appear only when their
files exist. No analytics, runtime CDN, remote fonts, or private SDK is required.

## Private source mapping and snapshot

Keep the mapping and source snapshots in an organizer-owned workspace outside the
public repository. `bridge.validate_mapping` requires separate organizer and public
documents, three distinct table URIs, and a complete, unique column mapping using
`bridge.FIELDS`. Participant data comes from the organizer document; presentations
and sessions come from the public program document.

This illustrative mapping generator uses symbolic identifiers only. Replace every
symbol with verified source identifiers in the private workspace before use:

```python
from symposium.organizing.bridge import FIELDS, validate_mapping

mapping = {
    "schema_version": 1,
    "organizer_document": "ORGANIZER_DOCUMENT",
    "public_document": "PUBLIC_PROGRAM_DOCUMENT",
    "sources": {},
}
for kind, fields in FIELDS.items():
    document = mapping["organizer_document" if kind == "participants" else "public_document"]
    mapping["sources"][kind] = {
        "uri": f"superhuman://docs/{document}/tables/TABLE_{kind.upper()}",
        "fields": {field: "COLUMN_" + field.upper() for field in sorted(fields)},
    }
validate_mapping(mapping)
```

`bridge.pull_snapshot(mapping, transport, public_root=..., workspace=...)` reads
schema and complete table pages into a new private snapshot. A connected Docs
transport can supply the read operations. The optional `InstituteOSTransport(root)`
uses a separately installed InstituteOS checkout and its external Python interpreter;
it requires `SUPERHUMAN_DOCS_MCP_TOKEN` in the operator environment. Neither that
checkout nor its token is a package or Pages dependency. Never place the token in
source, shell history, logs, mapping files, or GitHub Pages secrets.

## Projection, consent, and approval

`projection.project_snapshot(snapshot, event, resources)` returns an allowlisted
public bundle plus a private inclusion/exclusion ledger. Presenter entries derive
from the published program. Participant inclusion requires explicit affirmative
public-sharing consent. Contact fields and private document links are excluded;
public records use generated public identifiers rather than private row identifiers.
Duplicate identity or contribution ambiguity is recorded for organizer review;
do not silently merge conflicting answers or invent missing text. Preserve the
projection warnings and exclusions with the private snapshot.

Missing program abstracts remain visibly missing. Participant answers are
self-reported, not assessed expertise or verified identity. Dossiers summarize the
provided contribution and sources; participant briefs retain stated background,
applications, learning needs, and organizer-supplied resources. Neither supplies
invented research, rankings, inferred collaborations, or AI-generated biographies.

Only explicit UTC session records become schedule entries or calendar events.
An accepted abstract is not evidence of a speaking time. Pending sessions remain
pending, and the official program is the revision authority. A published site is a
snapshot, not a live synchronization promise.

`publication.stage_public(..., apply=True)` rechecks the snapshot, its age, the
projection, the private ledger, approved media and artifact bindings before creating
a new public tree. The default snapshot freshness limit is one hour; the API permits
an explicit limit no greater than one day. Retain the original private warnings,
including any media omission receipts. Review the resulting public content before
integrating the tree into the repository. Never broaden consent because a file is
needed for a layout or to increase the directory count.

## Dossiers, briefs, calendar, and native abstract book

Use `artifacts.write_dossiers` and `publication.write_participant_briefs` with the
validated bundle and new output directories. `publication.write_calendar` exports
only explicit sessions. These deterministic outputs require no LLM provider.

`artifacts.stage_abstract_book` stages a separate manuscript project.
`artifacts.render_abstract_book(bundle, workspace, template_root)` invokes the
existing Template repository's native rendering pipeline with its own Python 3.14
environment. Template and the fresh render workspace must be on GitVault; the
workspace must be outside Template. Both interpreter prefixes must resolve on the
external volume. Rendering records stdout/stderr and preserves intermediate evidence.
The native DOCX/PDF outputs require their own visual inspection; text equivalence
alone does not establish layout quality. A draft book is labeled as a draft.

Build artifacts in a private staging directory, run
`publication.write_artifact_index(bundle, artifacts_dir)`, then pass that directory
to `stage_public`. The artifact index binds files to the exact public bundle; it is
not a substitute for reviewing their contents. The final public manifest binds the
actual bytes. Preserve earlier editions and `archive/`; do not overwrite historical
source data, rendered books, or prior review evidence to refresh the current edition.

## GitHub Pages deployment

`.github/workflows/pages.yml` runs on relevant `main` pushes or a manual main-branch
dispatch. Its build job installs the locked public package, verifies the entire
approved public tree, builds `_site`, and uploads that directory alone. A dependent
job deploys through the `github-pages` environment with Pages/OIDC permissions.
There are no organizer secrets and no live private-source reads in CI. Configure
repository Pages to use GitHub Actions and restrict the deployment environment to
`main`; GitHub documents the required [custom-workflow actions and permissions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

A workflow file is deployment configuration, not proof that a deployment succeeded.
Verify its run result, the deployed `/Symposium/` URL, source-attribution content,
search/reset, keyboard disclosure controls, mobile layout, and available downloads
against the current approved manifest after release.

## Command-line workflow

`uv run symposium organize --help` lists the operator commands. Keep
`SYMPOSIUM_PRIVATE_DIR` outside every public checkout and set `INSTITUTEOS_ROOT`
and `TEMPLATE_ROOT` to their separately installed checkouts. The SDK pull requires
its environment token; an authenticated connected Docs transport can instead use
the Python transport protocol. Keep real mappings private.

```bash
uv run symposium organize pull --mapping "$SYMPOSIUM_PRIVATE_DIR/mapping.json" \
  --instituteos-root "$INSTITUTEOS_ROOT" --workspace "$SYMPOSIUM_PRIVATE_DIR/intake" --public-root .
# Select the newly saved snapshot; schema/rows and all raw answers remain private.
uv run symposium organize project --snapshot "$SYMPOSIUM_PRIVATE_DIR/snapshot.json" \
  --event "$SYMPOSIUM_PRIVATE_DIR/event.json" --resources "$SYMPOSIUM_PRIVATE_DIR/resources.json" \
  --workspace "$SYMPOSIUM_PRIVATE_DIR/projection" --public-root . --portraits
uv run symposium organize dossiers --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --output-dir "$SYMPOSIUM_PRIVATE_DIR/artifacts/dossiers" --public-root .
uv run symposium organize participant-briefs --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --output-dir "$SYMPOSIUM_PRIVATE_DIR/artifacts/participants" --public-root .
uv run symposium organize calendar --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --output "$SYMPOSIUM_PRIVATE_DIR/artifacts/program.ics" --public-root .
uv run symposium organize book --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --workspace "$SYMPOSIUM_PRIVATE_DIR/book" --template-root "$TEMPLATE_ROOT" --public-root . --render
```

Review the native outputs and copy only the reviewed PDF/DOCX into the artifact
staging directory as `book.pdf` and `book.docx`. The renderer applies a documented,
process-local Template compatibility policy to preserve literal tilde and
middle-dot characters, fails if the expected Template contract changes, and sets
Word page geometry to A4 with 25 mm margins. It records original/native and final
artifact hashes. The PDF has a linked contents section; the editable Word version
uses heading styles and has no generated contents section or printed page numbers.

```bash
uv run symposium organize artifact-index --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --artifacts-dir "$SYMPOSIUM_PRIVATE_DIR/artifacts" --public-root .
uv run symposium organize stage-public --bundle "$SYMPOSIUM_PRIVATE_DIR/projection/program.json" \
  --snapshot "$SYMPOSIUM_PRIVATE_DIR/snapshot.json" \
  --ledger "$SYMPOSIUM_PRIVATE_DIR/projection/approval-ledger.json" \
  --assets-dir "$SYMPOSIUM_PRIVATE_DIR/projection/portraits" \
  --artifacts-dir "$SYMPOSIUM_PRIVATE_DIR/artifacts" \
  --output-dir "$SYMPOSIUM_PRIVATE_DIR/approved-public" --public-root . --apply
uv run symposium organize check-public --public-dir "$SYMPOSIUM_PRIVATE_DIR/approved-public"
uv run symposium organize site --public-dir "$SYMPOSIUM_PRIVATE_DIR/approved-public" \
  --output-dir "$SYMPOSIUM_PRIVATE_DIR/site-preview"
```

All destinations are fresh: existing outputs are never overwritten. Review the
approved candidate and its diff before integrating it into `data/public/2026/`.
A later consent withdrawal requires a refreshed projection and removal from the
current public tree; publication history and previously downloaded copies persist.

For the return path, prepare a private JSON request with `page_uri`, fresh
`baseline_content`, `receipt_markdown`, and the actual `public_manifest_hash`.
`organize receipt-prepare --request ... --output ... --public-root .` creates a
plan without mutation. `organize receipt-apply --plan ... --instituteos-root ...
--output ... --public-root . --apply` appends once after a fresh page-hash check and
verifies readback. Reapplying an identical verified receipt is a no-op. A concurrent
edit fails; an uncertain write outcome must be inspected before retrying. This is
optimistic conflict detection, not a server-side atomic transaction. Receipts belong
on a dedicated private integration page; they never update acceptance, consent,
recording, scheduling, or email-sent fields automatically.
