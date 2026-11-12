# Version 3.3.0: 2026 Presenter Program, final lineup

**Book published on Zenodo November 12, 2026.**
*2026 Active Inference Symposium — Presenter Program*, version 3.3.0, is available
at [10.5281/zenodo.24161029](https://doi.org/10.5281/zenodo.24161029)
([public record](https://zenodo.org/records/24161029)). It is a new version under the
same concept record, [10.5281/zenodo.23986504](https://doi.org/10.5281/zenodo.23986504),
and supersedes [version 3.2.0](release_3_2_0.md). The public record metadata, DOI
resolution and all six unauthenticated asset SHA-256 checks are verified.

The [GitHub v3.3.0 software release](https://github.com/ActiveInferenceInstitute/Symposium/releases/tag/v3.3.0)
attaches the same six book-package files. The book DOI identifies this book
edition; it does not identify a released software archive.

## What changed

This edition carries the final presenter lineup from the organizer program as
captured on November 12, 2026 (UTC):

- **55 contributions** (from 57): 37 prerecorded talks, 14 livestreamed panels or
  group sessions, 3 interactive workshops and the keynote. 53 abstracts are supplied;
  the abstracts for Karl Friston and Mike Levin remain explicitly pending.
- **Removed:** prerecorded talks for which no video was submitted, and contributions
  withdrawn since November 1. Their presenters may still submit a lightning talk.
- **Added or re-credited:** new contributions and updated group credits from the
  organizer program, including the Textbook Group review and the live Q&A sessions.
- **19 explicit UTC sessions** (from 18).
- **119 consenting participant profiles** (from 45). The public listing includes a
  registration only when its latest answer for that email is an affirmative "Yes" and
  no answer for the same email is "No". One consenting registration is withheld
  because its affiliations field contains contact information that requires review.
  Two previously listed participants no longer appear in the consent-filtered view
  and are removed; no reason is inferred.

Dossiers, participant briefs, the UTC calendar, portraits, the public manifest and
both books are regenerated from the same verified bundle.

## Book and credits

The PDF (60 pages) and editable Word book cover the 6th Applied Active Inference
Symposium, November 12–13, 2026 (UTC). The cover credits Active Inference Institute
first, followed by all 50 exact published presenter/group display labels: 51 credit
entries, not a verified count of distinct individuals. Composite labels remain whole.
Affiliations, ORCIDs and supplied backgrounds appear only for exact whole-label
matches in the current designated public participant view and the public
co-organizing-team table: 8 labels. Supplied self-reports are not verified
institutional or identity claims. The cover and page-two artwork are the same
generated conceptual illustrations as version 3.2.0.

## Zenodo metadata edit after publication

On November 12, 2026 (about 18:15 UTC), at the organizer's request, the Zenodo record
metadata of version 3.3.0 was edited by hand; no file changed, and the six deposited
files above are still the published package.

- **Creators: 51 credit entries became 56 individual creators.** Composite credits
  were split into the people they name, each added person placed after their
  co-presenter: Dan Corva and Kevin Backhouse; Fraser Paterson (Andrew Pashea and
  Daniel Friedman were already listed); John Boik and Glen EP Ropella; Antonio
  Lucas-Alba and Héctor M. Manrique; Harshil Shah; Satyaki Maitra; Jesse Parent and
  Avery Lim; John H. Clippinger and Holly Grimm; Michael Walker.
- **Jesse Parent and Avery Lim** carry the ORCIDs and the affiliation (JOPRO) they
  supplied in writing to the organizers.
- Comma-separated credits had been deposited with the text after the first comma as
  given names (for example family name "Dan Corva", given name "Kevin Backhouse");
  the edited entries keep each full name as the family name, like the single
  presenters.
- The description sentence on creator entries now reads "Creator entries list each
  named presenter once, with Active Inference Institute first."

The deposited PDF and Word book are unchanged: their covers still list the 51 credit
labels, and contribution 36 still carries its submitted title, "From Minimal Regulators
to World Models: Boundary-Relative Distinctions for Factoring Generative Models"; the
presenters retitled it on November 12 to "From Minimal Model Systems to World Models:
Boundary-Relative Distinctions for Factoring Generative Models". Both are corrected
only in a new version.

## Public data and analyses

`data/public/2026/` is refreshed from the November 12 organizer snapshot. Participant
charts in the [visualization guide](visualizations_2026.md) are unchanged from
version 3.2.0 and still describe the 55-record November 5 public cohort; they were not
regenerated for this edition. Raw captures, source row identifiers, consent ledgers,
local build receipts and credentials are excluded from the release.

## Published book-package assets

| Zenodo file | Bytes | SHA-256 |
| --- | ---: | --- |
| [PDF book](https://zenodo.org/records/24161029/files/Active-Inference-Symposium-2026-Presenter-Program-v3.3.0.pdf) | 6,700,933 | `9308767e14ccdb02731690fe45223873c7b597f1bac080b0eae098936501f5da` |
| [Editable Word book](https://zenodo.org/records/24161029/files/Active-Inference-Symposium-2026-Presenter-Program-v3.3.0.docx) | 7,063,377 | `15f230cf08fe328d3e9ddd7cdee54d685226fa8b56ff248d93a7a627740cf46d` |
| [publication.json](https://zenodo.org/records/24161029/files/publication.json) | 1,674 | `84756394b349aa3ada4c7fabff3b5d9f0b43c962b32c004cc396066c5b849e3f` |
| [LICENSE.txt](https://zenodo.org/records/24161029/files/LICENSE.txt) | 1,083 | `757b4f0a698bc60665ab37f15c83a0834ce4c6f8b66d8794a614c00f6dd8e14b` |
| [README.md](https://zenodo.org/records/24161029/files/README.md) | 1,285 | `e5cd9b35dee68db08985729aeea317865746ace9cf501dc1a62b89b4af3f1df0` |
| [SHA256SUMS.txt](https://zenodo.org/records/24161029/files/SHA256SUMS.txt) | 492 | `75aacb8dcc23da3b8234d720b4ab6feac6c5847b65ebc7fb57d420ae958daa6c` |

The checked-in `data/public/2026/book.pdf` and `book.docx` are byte-identical to the
deposited PDF and Word files. The Zenodo `publication.json` is sanitized book-release
metadata, distinct from the repository's public-tree manifest of the same name.

## Verification

The source suite passed locally: 776 tests passed with 9 skips. All 60 PDF pages were
reviewed; the Word book contains every contribution title and the version DOI. Public
Zenodo metadata and DOI resolution were read back, and all six deposited files were
downloaded without authentication and matched byte-for-byte to the reviewed package.
Remote CI and the Pages deployment are tracked separately from Zenodo; see the GitHub
Actions history for their outcome.
