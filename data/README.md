# Symposium data

`public/2026/` is the retained approved **November 1, 2026** public snapshot:
57 contributions, 18 explicit UTC sessions, and 45 previously approved participant
profiles. Version 3.2.0 updates its reviewed PDF/Word book artifacts and their
manifest hashes while preserving the program, portraits, dossiers, participant
briefs and calendar. Its date does not imply current or renewed participant consent.

The new participant analyses use a separate admitted 55-record public 2026 cohort,
rechecked November 5; 15 have no substantive answers. That cohort is not copied into
the historical public snapshot or replaced by its 45 participant rows. Raw captures,
consent records, source row identifiers, private execution evidence and generated
provider drafts remain outside this public data tree. Absence from one snapshot
does not by itself establish a withdrawal or an identity change. See the
[3.2.0 release record](../docs/release_3_2_0.md).

The book is published separately on Zenodo at
[10.5281/zenodo.23986505](https://doi.org/10.5281/zenodo.23986505). Its public download
hashes match the independently reviewed PDF/Word files. The GitHub software release
and website deployment remain pending under the repository's publication controls.

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
