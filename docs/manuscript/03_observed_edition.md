# Edition evidence and replay

The released Presenter Program has a version-specific DOI and a public manifest
with hashes for its PDF and Word editions [@program2026]. `CITATION.cff` distinguishes
software metadata from book creators. The repository release notes record the
snapshot counts and unresolved abstracts, independent visual review, release-file
hash checks and local source-gate outcomes. These are recorded release observations,
not measurements reproduced by this manuscript render.

To repeat the public-tree checks from the source revision, prepare the pinned
Python dependencies and run `./gate.sh program`. `./gate.sh site` builds the public
Pages surface, and `./gate.sh docs` checks documentation links and index coverage.
The research-input scaffold has a separate `edition validate` command and does not
replace the released-tree check. The methods catalog can be inspected offline via
`uv run symposium organize methods --format json`.
