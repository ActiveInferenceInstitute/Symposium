# Participant and Presenter Program visualizations

`symposium.organizing.visualizations` produces private, deterministic charts from
two separately validated scopes: a complete capture of the user-designated 2026
public participant view, and an approved public program bundle. It makes no provider
request and reads no paid research drafts or private intake.

```python
from pathlib import Path
from symposium.organizing.publication import verify_public_tree
from symposium.organizing.visualizations import load_authorized_cohort, render_visualizations

bundle = verify_public_tree(Path("data/public/2026"))
cohort = load_authorized_cohort(Path("/private/current-public-participants-2026.json"), bundle)
manifest = render_visualizations(bundle, cohort, Path("/private/new-visualizations"))
```

Use the locked project environment and the workspace's governed offline runner.
Keep the cohort capture and artifact destination outside the public checkout.
The destination must be new and have an existing parent. Existing files, symlinked
destinations and paths inside the public checkout are refused. No CLI surface or
new package dependency is introduced. Configure Matplotlib/cache/temp paths on the
external volume when launching; the package uses the noninteractive Agg backend.

## Input admission

The cohort interchange has `schema_version: 1`, `year: 2026`, a closed-schema
`participants` list, exact `participant_order`, the seven `substantive_fields`, and
`records_sha256` computed by `organizing.models.content_hash(participants)`.
Its source supplies the exact designated public-view URL, capture SHA-256,
`private_intake_used: false`, `historical_data_used: false`, and matching included
and total-view row counts. Partial/excluded-view captures need explicit source
reconciliation before this complete-cohort API will admit them.

The loader rejects duplicate IDs/names, unknown participant fields, changed bytes,
changed order, another edition/view and cardinality mismatches. It checks that each
public ID derives from the supplied normalized display name. It never appends
older participants from the program bundle or fills blank answers from old data.
The admitted ordered IDs and substantive answers carry a separate projection
SHA-256. Rendering checks it again before creating outputs, so replaced IDs or
answers cannot silently reuse the old source-record/capture bindings.
An accepted hash establishes binding, not current consent, capture completeness or
live-source freshness; those require the separately reviewed source acquisition.

Only background, pragmatic value, epistemic value, application, challenges,
learning needs and future impact enter the participant corpus. Dedicated names,
affiliations and identifiers are excluded. Free text can still identify its author;
these charts are not anonymized data.

## Figures and interpretation

| File under `figures/` | Content and scope |
| --- | --- |
| `participant-coverage.png` | All captured participants, including zero-answer records; per-field answer counts and answered-field distribution. |
| `participant-topic-weights.png` | Count-based two-topic LDA, shown as a one-dimensional weight histogram; complementary weights are not separate spatial axes. |
| `participant-nmf.png` | Two TF-IDF NMF component weights with symlog axes; no overlapping point labels. Full public-ID coordinates are in `data/participant-nmf-key.csv`. |
| `participant-text-network.png` | Text cosine edges at `>= 0.2`, enlarged with labels only on connected records; isolated records remain counted and drawn separately. All IDs and edge weights remain in `data/network.json`. |
| `presenter-program-overview.png` | Contribution-type counts and descriptive mean-TF-IDF abstract terms. Counts distinguish contribution records, missing abstracts and distinct exact trimmed presenter display/group strings, preserving case. Group strings are not split into verified people. |
| `cohort-text-comparison.png` | Separate participant-answer and presentation-abstract length/completeness distributions. It does not compare separately fitted semantic coordinates. |

Count/TF-IDF vocabulary uses English stop words, unigrams/bigrams and at most
10,000 terms. Seed 45 controls LDA, NMF and network layout. Empty/zero-vector
participant records stay in coverage and the full ordered cosine CSV; their
similarities are blank/unavailable, not assertions of zero similarity. If fewer
than two represented records or features remain, topic charts explicitly report
insufficient data without substituting another method.

All supplied abstract text comes from the approved bundle. Absent abstracts remain
absent; no text is invented for visualization. The figure contains no claim that
text components reveal expertise, that an edge establishes a relationship, or
that the captured volunteers represent a wider population. Descriptive terms are
not externally validated themes.

`visualizations.json` binds program/capture/participant hashes, exact row orders,
missing-text masks, actual model classes, model statuses, seed, installed package
versions, figure/data hashes, and final-draw text-box diagnostics. Nonzero text-box
overlap counts require inspection; even zero counts do not replace an independent
visual review. The manifest does not certify lock compatibility or live freshness.

## Verification

`tests/test_organizing_visualizations.py` exercises real synthetic public records,
scope/hash/order rejection, empty vectors, count-LDA/NMF numerical behavior,
insufficient-data handling, presenter display-string units, exclusive output
preservation, and an actual six-chart render with artifact hashes. No live provider
test or historical registration data is used.

Run the focused test and Ruff gates through the qualified workspace runner before
the full repository validation. Keep actual source-bound receipts. Inspect all
final figures separately, including labels and edge visibility; tests alone do not
establish visual quality. Designed books require their own physical-page review.
