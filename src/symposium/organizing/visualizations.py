"""Source-bound participant and presenter visualizations with fresh private outputs."""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import re
from dataclasses import asdict, replace
from pathlib import Path
from typing import TypedDict

import numpy as np

from .models import PublicBundle, PublicParticipant, canonical_bytes, content_hash, validate_bundle
from .visualization_data import (
    FIELDS,
    PUBLIC_VIEW,
    SEED,
    THRESHOLD,
    AuthorizedCohort,
    TopicWeights,
    VisualizationError,
    authorized_records,
    compare_texts,
    projection_hash,
    text_features,
    topic_weights,
)


class CohortSource(TypedDict):
    """Only source-admission fields are consumed; raw source identifiers stay private."""

    source_url: str
    capture_file_sha256: str
    historical_data_used: bool
    private_intake_used: bool
    included_participants: int
    public_view_total_rows: int


class CohortDocument(TypedDict):
    """Interchange written by the separately reviewed 2026 public-view capture."""

    schema_version: int
    year: int
    participants: list[PublicParticipant]
    participant_order: list[str]
    substantive_fields: list[str]
    records_sha256: str
    source: CohortSource


def load_authorized_cohort(path: Path, bundle: PublicBundle) -> AuthorizedCohort:
    """Check the designated view, full membership, field allowlist, hashes and order.

    The capture must be refreshed and authorized separately. Neither a valid hash
    nor this loader certifies current consent or live-source freshness.
    """
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise VisualizationError("Cohort must be a bounded regular JSON file")
    try:
        document: CohortDocument = json.loads(path.read_text(encoding="utf-8"))
        source = document["source"]
        checked_bundle = validate_bundle(bundle)
        if (
            type(document["schema_version"]) is not int
            or document["schema_version"] != 1
            or type(document["year"]) is not int
            or document["year"] != 2026
            or checked_bundle["event"]["year"] != 2026
        ):
            raise VisualizationError("Cohort and program must belong to the 2026 edition")
        if (
            source["source_url"] != PUBLIC_VIEW
            or source["historical_data_used"] is not False
            or source["private_intake_used"] is not False
        ):
            raise VisualizationError("Cohort source is not the designated 2026 public view")
        cohort = authorized_records(checked_bundle, document["participants"])
        if list(cohort.ids) != document["participant_order"]:
            raise VisualizationError("Participant records differ from their declared row order")
        if document["records_sha256"] != cohort.records_sha256:
            raise VisualizationError("Participant content hash differs from the captured cohort")
        if tuple(document["substantive_fields"]) != FIELDS:
            raise VisualizationError("Substantive fields differ from the seven-field allowlist")
        if (
            type(source["included_participants"]) is not int
            or type(source["public_view_total_rows"]) is not int
            or source["included_participants"] != len(cohort.ids)
            or source["public_view_total_rows"] != len(cohort.ids)
        ):
            raise VisualizationError(
                "Source membership cardinality differs from the complete cohort"
            )
        if not re.fullmatch(r"[a-f0-9]{64}", source["capture_file_sha256"]):
            raise VisualizationError("Source capture needs a SHA-256 content binding")
        return replace(cohort, capture_sha256=source["capture_file_sha256"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise VisualizationError("Malformed public cohort interchange") from exc


def _write_json(path: Path, value: bytes) -> None:
    """Exclusively write already-serialized JSON evidence."""
    with path.open("xb") as stream:
        stream.write(value)


def _weight_key(path: Path, cohort: AuthorizedCohort, topics: TopicWeights) -> None:
    """Retain every participant in the external coordinate key; blanks are unavailable."""
    weights = {
        identifier: pair for identifier, pair in zip(topics.ids, topics.weights, strict=False)
    }
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("public_id", "component_1", "component_2", "represented"))
        for identifier in cohort.ids:
            pair = weights.get(identifier)
            writer.writerow(
                (
                    identifier,
                    "" if pair is None else float(pair[0]),
                    "" if pair is None else float(pair[1]),
                    pair is not None,
                )
            )


def render_visualizations(bundle: PublicBundle, cohort: AuthorizedCohort, output: Path) -> Path:
    """Render six offline charts and bounded data evidence into a fresh private tree.

    All participants remain in coverage and similarity matrices. Topic models use
    represented substantive answer text only. Presenter figures use approved
    abstracts, including explicit accounting for absent abstracts.
    """
    checked = validate_bundle(bundle)
    if (
        checked["event"]["year"] != 2026
        or cohort.source_url != PUBLIC_VIEW
        or not re.fullmatch(r"[a-f0-9]{64}", cohort.capture_sha256)
        or len(cohort.ids) != len(set(cohort.ids))
        or len(cohort.ids) != len(cohort.answers)
        or any(len(row) != len(FIELDS) for row in cohort.answers)
        or cohort.projection_sha256 != projection_hash(cohort.ids, cohort.answers)
    ):
        raise VisualizationError("Cohort is not an admitted 2026 public-view input")
    repository = Path(__file__).resolve().parents[3]
    if (
        output.exists()
        or any(path.is_symlink() for path in (output, *output.parents))
        or output.resolve().is_relative_to(repository)
        or not output.parent.is_dir()
    ):
        raise VisualizationError(
            "Visualization output must be fresh and outside the public checkout"
        )
    output.mkdir(mode=0o700)
    figures = output / "figures"
    figures.mkdir()
    data = output / "data"
    data.mkdir()
    os.environ.setdefault("MPLCONFIGDIR", str(output / "matplotlib-cache"))
    from .visualization_charts import (
        nmf_projection,
        participant_coverage,
        participant_network,
        save_chart,
        topic_distribution,
    )
    from .visualization_program import program_overview, text_comparison

    features = text_features(cohort)
    lda, nmf = topic_weights(features), topic_weights(features, nonnegative=True)
    network = participant_network(features)
    comparison = compare_texts(checked, cohort)
    charts = (
        ("participant-coverage.png", participant_coverage(cohort)),
        ("participant-topic-weights.png", topic_distribution(lda, len(cohort.ids))),
        ("participant-nmf.png", nmf_projection(nmf, len(cohort.ids))),
        ("participant-text-network.png", network.figure),
        ("presenter-program-overview.png", program_overview(checked, comparison)),
        ("cohort-text-comparison.png", text_comparison(checked, cohort)),
    )
    receipts = [asdict(save_chart(figure, figures / name)) for name, figure in charts]
    _weight_key(data / "participant-nmf-key.csv", cohort, nmf)
    _weight_key(data / "participant-topic-key.csv", cohort, lda)
    _write_json(
        data / "network.json",
        canonical_bytes(
            {
                "participant_order": cohort.ids,
                "edges": network.edges,
                "threshold": THRESHOLD,
                "comparison": ">=",
                "isolated_ids": network.isolated_ids,
                "represented_ids": [cohort.ids[i] for i in features.represented],
            }
        ),
    )
    _write_json(data / "text-comparison.json", canonical_bytes(asdict(comparison)))
    with (data / "participant-cosine.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("public_id", *cohort.ids))
        for identifier, row in zip(cohort.ids, features.cosine, strict=True):
            writer.writerow(
                (identifier, *(float(value) if np.isfinite(value) else "" for value in row))
            )
    artifacts = {
        str(path.relative_to(output)): {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }
        for folder in (data, figures)
        for path in sorted(folder.iterdir())
    }
    manifest = {
        "schema_version": 1,
        "bundle_sha256": content_hash(checked),
        "records_sha256": cohort.records_sha256,
        "capture_sha256": cohort.capture_sha256,
        "projection_sha256": cohort.projection_sha256,
        "source_url": cohort.source_url,
        "source_freshness": "not_checked",
        "participant_order": cohort.ids,
        "participant_count": len(cohort.ids),
        "represented_ids": [cohort.ids[i] for i in features.represented],
        "empty_corpus_ids": [
            identifier
            for identifier, text in zip(cohort.ids, cohort.documents, strict=True)
            if not text
        ],
        "zero_vector_ids": [
            identifier for i, identifier in enumerate(cohort.ids) if i not in features.represented
        ],
        "presentation_order": [row["id"] for row in checked["presentations"]],
        "presentation_count": len(checked["presentations"]),
        "pending_abstract_ids": comparison.pending_abstracts,
        "distinct_presenter_display_strings": comparison.distinct_presenter_display_strings,
        "models": [
            {
                "requested": label,
                "actual_class": model.actual_class,
                "status": model.status,
                "input": kind,
                "components": 2,
                "seed": SEED,
                "fallback_used": False,
                "participant_order": model.ids,
                "top_terms": model.terms,
                "parameters": dict(model.parameters),
            }
            for label, model, kind in (("lda", lda, "counts"), ("nmf", nmf, "tfidf"))
        ],
        "vocabulary": {"ngrams": [1, 2], "stop_words": "sklearn English", "max_features": 10000},
        "charts": receipts,
        "artifacts": artifacts,
        "provider_calls": 0,
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("matplotlib", "numpy", "scipy", "scikit-learn", "networkx")
        },
        "interpretation": [
            "Submitted text only; no generated profiles or private registrations.",
            "Display/group strings are not verified distinct-person identities.",
            "Text components, terms and edges do not establish expertise or relationships.",
            "Topic/sparse charts use external ID keys; final page/figure review is still required.",
        ],
    }
    path = output / "visualizations.json"
    _write_json(path, canonical_bytes(manifest))
    return path
