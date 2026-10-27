# Migration and historical workflows

The numbered v1 scripts are historical. Current commands are `symposium analyze`,
`generate`, `visualize`, `edition`, and `organize`; inspect each with `uv run symposium
COMMAND --help`. There is no automatic directory reorganization or general migration
utility. Preserve historical files and evidence while preparing new inputs separately.

Current package support starts at Python 3.12. Python 3.10/3.11 users must select a
supported interpreter and synchronize the committed lock before running the current
package; see [installation](installation.md). The separate Template renderer remains
on Python 3.14.

For current research inputs, follow [2026 setup](2026_setup.md). Presenter exports
belong immediately under individual folders within `data/inputs/aif_2026/presenters/`.
Do not copy a 2024/2025 registration roster into 2026 or infer renewed consent.
`uv run python run.py --year 2025` explicitly selects historical research paths;
it is not a current onboarding action and some menu actions make paid requests.

For organizer publication, use [the private snapshot and staging workflow](organizing_publication.md).
Approved `data/public/2026/` and the research scaffold are independent. Keep raw
snapshots, private identifiers and drafts outside the public checkout. Validate a
fresh candidate and inspect its changes before integration; never overwrite an old
publication as an undocumented migration shortcut.

Earlier verification records [2.2.0](release_2_2_0.md) and [2.2.1](release_2_2_1.md)
retain their original runtime, roster-readiness and test claims. Those claims describe
those releases, not the current tree.
