# Symposium data

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
