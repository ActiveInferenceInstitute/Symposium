# InstituteOS integration — Symposium

## Identity

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/Symposium` |
| Affiliation | `institute` |
| Category | `research-software` |
| Status | `active` |
| Maturity | `released` |
| Steward | Active Inference Institute |
| Default branch | `main` |
| Current release | — |
| License | `MIT` |
| Citation | Active Inference Institute — Symposium. |

## Federation

| Setting | Value |
| --- | --- |
| Dashboard mode | `repos` |
| Analytics | `true` |
| Dashboard | `true` |
| Sync policy | `pull` |
| Registries | — |
| Tags | symposium, research, learning-plans, visualization, python |

## Ecosystem relations

| Repository | Relation | Note |
| --- | --- | --- |
| `ActiveInferenceInstitute/InstituteOS` | `referenced-by` | Federated via the InstituteOS .aii manifest. |
| `ActiveInferenceInstitute/Active_Inference_Ontology` | `references` | Uses Active Inference Ontology terms. |

## Key artifacts

| Path | Kind | Description |
| --- | --- | --- |
| `README.md` | `doc` | Repository overview. |
| `src` | `code` | Source tree. |
| `pyproject.toml` | `code` | Python package config. |
| `LICENSE` | `doc` | License. |
| `AGENTS.md` | `doc` | Agent guidance. |
| `CITATION.cff` | `citation` | Machine-readable citation metadata. |
| `tests` | `test` | Test suite. |
| `docs` | `doc` | Documentation tree. |
| `CHANGELOG.md` | `doc` | Changelog. |

## Portable tasks

| Task | Command | Working directory | Description |
| --- | --- | --- | --- |
| `test` | `python -m pytest` | `.` | Run the test suite. |

## Validation

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

The sidecar is valid when `validate` prints `OK` and reports no missing artifact,
manifest, link, or declared-doc path. Completeness is a curation target, not a
runtime requirement.

## Data boundary

This sidecar carries metadata only. It does not grant execution permission, does not
replace the repository's own documentation, and must not be used to move private
content into a public repository. Task execution is limited to trusted checkouts.
