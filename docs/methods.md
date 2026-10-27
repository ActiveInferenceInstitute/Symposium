# Methods and evidence boundaries

## Approved public content

Public dossiers and participant briefs are deterministic derivatives of an approved
organizer snapshot. Presentations retain supplied abstracts and attribution;
participant briefs retain affirmative-consent self-reports and supplied resources.
They do not perform external identity verification or infer competence, rankings,
collaborations or biographies. Missing abstracts and unconfirmed session times must
remain visibly pending. Only explicit sessions produce calendar entries.

The current approved snapshot lives in `data/public/2026/`. The separate
`data/inputs/aif_2026/` research scaffold may remain empty. Validate the former with
`organize check-public` and the latter with `edition validate`; neither substitutes
for the other. Structural validity does not establish truth, current consent outside
the recorded source, source freshness, or event readiness.

## Next intake and change review

1. Pull a fresh source snapshot into a private workspace outside the public checkout.
   Verify mapping/schema and preserve raw responses and transport evidence privately.
2. Project only allowlisted public fields. Review affirmative consent, identity
   ambiguities, missing text and exclusion warnings. Do not reuse historical consent.
3. Create dossiers, participant briefs and explicit-session calendar artifacts.
   Stage and render the native book separately; inspect every final PDF/DOCX surface.
4. Bind reviewed artifacts to the candidate bundle and stage a fresh public tree.
5. Verify integrity, inspect content readiness and compare the candidate with the
   previous approved tree before an organizer decides whether to integrate it.

```bash
uv run symposium organize readiness --public-dir "$CANDIDATE_PUBLIC_DIR"
uv run symposium organize readiness --public-dir "$CANDIDATE_PUBLIC_DIR" --require-complete
uv run symposium organize review-update --previous-public-dir data/public/2026 \
  --candidate-public-dir "$CANDIDATE_PUBLIC_DIR" \
  --output "$SYMPOSIUM_PRIVATE_DIR/update-review.json" --public-root .
```

Set both directory variables to organizer-owned locations outside the public
checkout. Normal readiness reports pending content without failing; strict readiness
returns nonzero for incomplete content. Integrity errors fail both modes. Readiness
reports `source_freshness: not_checked`: hashes do not establish whether the source
has changed since capture.

Update review verifies both public trees and records additions, removals, changed
fields and artifact differences. The report is private and refuses an existing
output. It does not promote a candidate, delete a record, identify renamed people,
or infer that a removal means revoked consent. Resolve removals and ambiguous
identity changes with organizers. A confirmed withdrawal requires an explicit
publication decision; earlier downloads and publication history may persist.

## Optional research analysis

The `analyze` and `generate` commands use external LLM providers and can incur
charges. Profiles, methods, curricula, summaries and proposals are unverified drafts.
Public-sharing consent is not itself authorization for every third-party processing
purpose. Verify authorization and minimize transmitted data before making requests.
Keep drafts private and review material claims against primary sources, including
identity, provenance, quotations and dates. No generated draft is automatically
published by the organizer pipeline.

[CSV schema and preflight](2026_setup.md) cover structural input checks; the
[API guide](api_guide.md) covers actual configuration and error handling. Prompt
requests for citations or comprehensive research are not guarantees of accuracy.

## Artifacts and interpretation

A manifest or artifact index establishes byte/bundle bindings, not semantic or visual
quality. Native rendering uses the separate Template Python 3.14 pipeline; a render
exit status and extracted text do not replace page-by-page visual review. Website
verification needs actual browser, keyboard, responsive and download checks.

[Text visualization](csv_visualization_guide.md) is exploratory corpus analysis.
Retain input hashes/order, options, lockfile, actual method, warnings and outputs.
Distances and clusters describe a representation of text, not validated scientific
relationships or assessments of people. No publication, test result, rendering or
visualization in this pipeline independently validates scientific claims.
