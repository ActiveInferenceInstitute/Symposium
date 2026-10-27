# Integration methods

Reviewed: 2026-10-27. Offline metadata; no live availability or authentication checks.

## Start — personalized learning

Role: manual-handoff

AI-assisted learning and curriculum preparation.

Use for: Prepare a reading plan and identify learning needs before a contribution.

Handoff: Browsing is independent of Symposium. Generating curricula in Start has its own configuration, authorization and optional provider costs.

[Repository](https://github.com/ActiveInferenceInstitute/Start) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/Start/blob/7797ff5a34bf8584aef99b23d697b6363f4b7eff/README.md)

## Institute courses

Role: resource

Course materials and their publishing infrastructure.

Use for: Find teaching materials and educational context for a presentation or workshop.

Handoff: Reference materials only; Symposium does not import course records or run the course build pipeline.

[Repository](https://github.com/ActiveInferenceInstitute/courses) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/courses/blob/d42e4294c3e799696ad84837cf8671ce50d1419a/README.md)

## Fundamentals textbook companion

Role: resource

Python examples and figure-generation code accompanying Active Inference learning materials.

Use for: Study concrete algorithms and reproduce an example before describing its results.

Handoff: The companion code is distinct from access to the textbook. Running an example does not establish scientific validity.

[Repository](https://github.com/ActiveInferenceInstitute/fundamentals) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/fundamentals/blob/fc3383c27af6b8bd7b93ed3daf90deae24d454e7/README.md)

## Generalized Notation Notation

Role: manual-handoff

Notation and tooling for specifying, validating and rendering generative models.

Use for: Make model assumptions explicit and prepare model artifacts alongside a contribution.

Handoff: Use the separate GNN pipeline and its model/backend admission evidence. No automatic Symposium model adapter is installed.

[Repository](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/f0dfb68368280f3a43ff91ac28db058c968002d8/.github/README.md)

## pymdp (Institute fork)

Role: manual-handoff

Discrete-state Active Inference agent modeling code.

Use for: Develop and reproduce computational demonstrations for a contribution.

Handoff: This is the Institute fork; its README identifies infer-actively/pymdp as upstream. Model execution and dependency selection remain a separate workflow.

[Repository](https://github.com/ActiveInferenceInstitute/pymdp) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/pymdp/blob/411a8e36fbd273d4fc4c897561e80aa5be59dc8e/README.md)

## Active Inference Ontology

Role: resource

Structured terminology, identifiers, relations and vocabulary exports.

Use for: Clarify terms and document mappings when communicating research methods.

Handoff: Vocabulary alignment needs human review and does not establish formal or scientific equivalence. Symposium does not perform automatic ontology mapping.

[Repository](https://github.com/ActiveInferenceInstitute/Active_Inference_Ontology) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/Active_Inference_Ontology/blob/02661575f9ac5213eed6d392c37ca6642660c191/README.md)

## Working Groups

Role: manual-handoff

Draft charters and operating procedures for collaborative work.

Use for: Prepare a group discussion and plan continued work after the Symposium.

Handoff: Draft documents carry no authority until adopted and ratified. This link does not create membership or change organizer decisions.

[Repository](https://github.com/ActiveInferenceInstitute/Working_Groups) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/Working_Groups/blob/b366662015d03dc29798dedbf1d472ecef036ce2/README.md)

## Active Inference Journal

Role: resource

Public recordings, transcripts, captions and associated metadata.

Use for: Find prior discussions and recordings to contextualize a contribution.

Handoff: This is a content archive, not an automatic Symposium submission, acceptance or proceedings-publication service.

[Repository](https://github.com/ActiveInferenceInstitute/ActiveInferenceJournal) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/ActiveInferenceJournal/blob/5678957afcb0f7f2a03af509b9c1b1023f3c5024/README.md)

## Journal Utilities

Role: manual-handoff

Tools for transcription, transcript browsing and export.

Use for: Prepare accessible recording and transcript artifacts after permission to process and share them.

Handoff: Separate hardware, services and configuration may be required. Symposium does not automatically send recordings to these tools.

[Repository](https://github.com/ActiveInferenceInstitute/Journal_Utilities) · [Pinned evidence](https://github.com/ActiveInferenceInstitute/Journal_Utilities/blob/b690625cfe02c007b12fd18085868cdefbe10688/README.md)

## docxology/template

Role: code-integration

Reproducible research and document rendering pipeline used by the native abstract-book workflow.

Use for: Render the approved abstract-book project to PDF and editable Word.

Handoff: Existing optional integration requires an explicitly selected Template checkout, compatible separate Python 3.14 environment and --render. Inspect final pages; rendering does not authorize publication.

[Repository](https://github.com/docxology/template) · [Pinned evidence](https://github.com/docxology/template/blob/83dd01d219ca1bfe663f655128c206b3e4e29ca2/.github/README.md)

## Prepare research inputs

Use learning resources to prepare research materials; validate the separate research-input scaffold. These inputs are independent of the approved public program.

Credentials: none

- `uv run symposium edition validate --year 2026`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/2026_setup.md)

## Express and reproduce models

Choose notation, vocabulary and computational tools for a contribution. These are manual handoffs to separate repositories, not automatic model execution inside Symposium.

Credentials: none


[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/methods.md)

## Check the public program

Verify the approved publication tree and inspect pending text offline. Structural integrity and content readiness do not establish source freshness.

Credentials: none

- `uv run symposium organize check-public --public-dir data/public/2026`
- `uv run symposium organize readiness --public-dir data/public/2026`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/organizing_publication.md)

## Capture a private organizing snapshot

Use the optional InstituteOS bridge only with separately configured SDK access and a reviewed mapping. Raw source records stay outside the public checkout. Start by inspecting the pull interface.

Credentials: instituteos-docs

- `uv run symposium organize pull --help`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/organizing_publication.md)

## Review a candidate intake

Compare two verified public trees before an organizer decides whether to integrate changes. The private report does not publish, infer renamed people or infer why a participant was removed.

Credentials: none

- `uv run symposium organize review-update --previous-public-dir data/public/2026 --candidate-public-dir "$CANDIDATE_PUBLIC_DIR" --output "$SYMPOSIUM_PRIVATE_DIR/update-review.json" --public-root .`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/methods.md)

## Assemble and render the abstract book

Use source-grounded dossiers, participant briefs and the optional native Template renderer. Run the documented private staging process and inspect final PDF/Word pages before publishing.

Credentials: none

- `uv run symposium organize dossiers --help`
- `uv run symposium organize participant-briefs --help`
- `uv run symposium organize book --help`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/organizing_publication.md)

## Optional OpenRouter research drafts

Generate private research drafts only after separately authorizing provider transmission and charges. Public-sharing consent alone does not authorize every external processing purpose.

Credentials: openrouter

- `uv run symposium analyze participants --csv-file "$SYMPOSIUM_PRIVATE_DIR/registrations.csv" --output-dir "$SYMPOSIUM_PRIVATE_DIR/drafts" --api-provider openrouter`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/api_usage.md)

## Optional Perplexity research drafts

Use the existing Perplexity analysis workflow only with authorized source inputs and paid-provider access. Verify generated claims, citations and identity matches against primary sources.

Credentials: perplexity

- `uv run symposium analyze presenters --data-dir "$SYMPOSIUM_PRIVATE_DIR/presenters" --output-dir "$SYMPOSIUM_PRIVATE_DIR/drafts" --api-provider perplexity`

[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/perplexity_research.md)

## Continue after the event

Use public archives for context and draft group procedures for follow-through. Recording processing and sharing still require their own permissions and service configuration.

Credentials: none


[Documentation](https://github.com/ActiveInferenceInstitute/Symposium/blob/main/docs/methods.md)
