# Symposium data

`public/2026/` is the approved **November 12, 2026** public snapshot, the final
presenter lineup: 55 contributions, 19 explicit UTC sessions and 119 consenting
participant profiles. Version 3.3.0 regenerates its program, portraits, dossiers,
participant briefs, calendar, PDF/Word books and manifest from that snapshot. Its
date does not imply consent beyond the affirmative answers captured for it.

The participant analyses still use a separate admitted 55-record public 2026 cohort,
captured November 5; 15 have no substantive answers. Raw captures, consent records,
source row identifiers, private execution evidence and generated provider drafts
remain outside this public data tree. Absence from one snapshot does not by itself
establish a withdrawal or an identity change. See the
[3.3.0 release record](../docs/release_3_3_0.md).

The version 3.3.0 book is published separately on Zenodo at
[10.5281/zenodo.24161029](https://doi.org/10.5281/zenodo.24161029); its public
downloads match the checked-in `book.pdf` and `book.docx` byte for byte. The
[GitHub v3.3.0 release](https://github.com/ActiveInferenceInstitute/Symposium/releases/tag/v3.3.0)
carries the same six book-package files. The earlier 3.2.0 edition remains at
[10.5281/zenodo.23986505](https://doi.org/10.5281/zenodo.23986505).

`inputs/aif_2024/` contains historical presenter exports and registrations.
`inputs/aif_2025/` contains historical participant registrations.
`inputs/aif_2026/` is the empty current-edition workspace, based on the 2025 survey
schema. Historical inputs are retained unchanged.

```bash
uv run symposium edition init --year 2026
uv run symposium edition validate --year 2026
# Before analysis, require actual eligible registrations and presenter exports:
uv run symposium edition validate --year 2026 --require-data
```

Populate current authorized registrations in
`inputs/aif_2026/Public_Participant_Information.csv`. Add one current topic CSV and
one works CSV per presenter under `inputs/aif_2026/presenters/<Presenter_Name>/`.
Do not copy historical registrations into the new year. See the
[2026 organizer guide](../docs/2026_setup.md) for all 14 registration fields,
consent rules, presenter layout, validation behavior, and processing examples.

Other directories contain proposal catechisms, system prompts, templates, and
user-provided domain context. Keep API credentials in the ignored `.env` file and
organizer configuration in the ignored `config.json`. Reports go to
`outputs/<year>_symposium/`, which is ignored by Git. Review registration data before
committing anything to this public repository.
