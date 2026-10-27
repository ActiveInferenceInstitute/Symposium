# Optional background research drafts

`analyze backgrounds` uses the Perplexity provider to draft participant background
reports from authorized participant input. The prompts request research and source
attribution; the implementation does not prove exhaustive coverage, correct identity,
verified citations, complete employment history, or a person's expertise.

```bash
uv run symposium analyze backgrounds --help
```

For an explicitly authorized paid run, supply `--csv-file` and `--output-dir` as
shown in the [user guide](user_guide.md), configure a private `PERPLEXITY_API_KEY`,
and keep results outside the public checkout. Review whether provider transmission
is authorized before submitting personal information. Limit inputs to what the task
requires. The consent filter is an input gate, not a comprehensive privacy review.

Verify each material claim against the cited primary source, including identity,
dates, authorship and quotation context. Record unresolved identity matches and
inaccessible sources rather than filling gaps. A model-generated URL is not evidence
that the source was read. Treat recommendations and inferred interests as drafts;
participant self-reports remain distinct from independently verified facts.

A payment error stops processing. Other failures may leave partial reports; inspect
logs and output completeness. No background report is automatically added to the
public program. For deterministic source-based public dossiers and briefs, use
[organizer publication](organizing_publication.md). See [methods](methods.md) for
evidence and interpretation limits.
