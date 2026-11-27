# Evidence and Approval Boundaries in the Active Inference Symposium Program

This methods manuscript describes the organizer publication workflow. The released Presenter Program remains a separate publication with its own credits and DOI.



The numbered Markdown sections assemble in filename order. `config.yaml` defines
publication metadata and PDF output. `preamble.md` supplies LaTeX configuration,
and `references.bib` supplies machine-readable citations.

## Render and verify

From the root of a clean source checkout, with Git, uv, Pandoc, XeLaTeX, BibTeX,
and the [Template LaTeX dependencies](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/guides/startup-and-setup.md):

```bash
source_checkout="$(pwd -P)"
slug="$(basename "$source_checkout")"
renderer_checkout="$(mktemp -d)/template"
git init -q "$renderer_checkout"
git -C "$renderer_checkout" remote add origin https://github.com/docxology/template.git
git -C "$renderer_checkout" fetch --depth=1 --filter=blob:none origin 87704feae0a4490ef7dad9c931d268e8c30273c2
git -C "$renderer_checkout" sparse-checkout set docs infrastructure scripts
git -C "$renderer_checkout" checkout --detach FETCH_HEAD
cd "$renderer_checkout"
uv sync --locked --no-dev
mkdir -p projects/working
ln -s "$source_checkout" "projects/working/$slug"
uv run --no-sync python scripts/pipeline/stage_03_render.py --project "working/$slug"
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project "working/$slug"
```

Read the assembled PDF at `output/pdf/${slug}_combined.pdf` in the source checkout.
Its validation report and source-bound provenance receipt are in `output/reports/`.
The build writes generated artifacts under `output/`. Use a disposable source
checkout if the project is already using that directory for other output.
