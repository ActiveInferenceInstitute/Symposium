# Catechism templates

Structured proposal templates that `symposium generate projects --catechism <NAME>`
reads. Each file supplies the question/section scaffold the generator fills in.

| File | `--catechism` value | Purpose |
| --- | --- | --- |
| `KarmaGAPGrants.md` | `KarmaGAP` | Ethical research grant-proposal format (default). |
| `EUGrants.md` | `EUGrants` | European research-funding proposal format. |
| `Synthetic_Catechism.md` | `Synthetic` | Cross-domain synthesis template. |

The `--catechisms-dir` option points the CLI at a directory of such templates; the
shipped set is the default. Keep templates as Markdown so generated proposals stay
readable. See the [user guide](../../docs/user_guide.md) for proposal examples and
[`../README.md`](../README.md) for the broader data layout.
