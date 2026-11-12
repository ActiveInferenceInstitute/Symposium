"""Real offline source, numerical and preservation scenarios with synthetic records."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Literal, assert_never

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.container import BarContainer

from symposium.organizing.models import (
    PublicBundle,
    PublicParticipant,
    canonical_bytes,
    content_hash,
    public_id,
)
from symposium.organizing.visualization_data import (
    FIELDS,
    PUBLIC_VIEW,
    PublicId,
    VisualizationError,
    compare_texts,
    text_features,
    topic_weights,
)
from symposium.organizing.visualization_program import text_comparison
from symposium.organizing.visualizations import (
    CohortDocument,
    load_authorized_cohort,
    render_visualizations,
)
from tests.test_organizing_site import bundle as bundle


def person(name: str, background: str = "") -> PublicParticipant:
    return PublicParticipant(
        id=public_id("person", name.casefold()),
        name=name,
        affiliations="",
        orcid="",
        background=background,
        pragmatic_value="",
        epistemic_value="",
        active_inference_application="",
        challenges="",
        learning_needs="",
        future_impact="",
    )


@pytest.fixture
def document() -> CohortDocument:
    rows = [
        person("Synthetic B", "robot learning curious systems"),
        person("Synthetic A", "learning cognitive systems"),
        person("Synthetic Empty"),
    ]
    return CohortDocument(
        schema_version=1,
        year=2026,
        participants=rows,
        participant_order=[row["id"] for row in rows],
        substantive_fields=list(FIELDS),
        records_sha256=content_hash(rows),
        source={
            "source_url": PUBLIC_VIEW,
            "capture_file_sha256": "a" * 64,
            "historical_data_used": False,
            "private_intake_used": False,
            "included_participants": 3,
            "public_view_total_rows": 3,
        },
    )


def save_cohort(document: CohortDocument, path: Path) -> Path:
    path.write_bytes(canonical_bytes(document))
    return path


def test_cohort_preserves_source_order_and_blank_answers(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: source order intentionally differs from display-name order.
    path = save_cohort(document, tmp_path / "cohort.json")
    # When: the authorized view capture is loaded.
    cohort = load_authorized_cohort(path, bundle)
    # Then: current rows and missing answers are retained without older-roster fallback.
    assert cohort.ids == tuple(document["participant_order"])
    assert cohort.documents == ("robot learning curious systems", "learning cognitive systems", "")
    assert cohort.records_sha256 == document["records_sha256"]


Defect = Literal["duplicate", "order", "hash", "year", "view", "count", "unknown", "outsider"]


@pytest.mark.parametrize(
    "defect", ["duplicate", "order", "hash", "year", "view", "count", "unknown", "outsider"]
)
def test_changed_or_out_of_scope_input_is_refused_before_outputs(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path, defect: Defect
) -> None:
    # Given: a structurally corrupted or out-of-scope capture.
    changed = json.loads(canonical_bytes(document))
    match defect:
        case "duplicate":
            changed["participants"][1]["id"] = changed["participants"][0]["id"]
        case "order":
            changed["participant_order"].reverse()
        case "hash":
            changed["participants"][0]["background"] = "different source answer"
        case "year":
            changed["year"] = 2025
        case "view":
            changed["source"]["source_url"] = "https://example.org/other-view"
        case "count":
            changed["source"]["public_view_total_rows"] = 4
        case "unknown":
            changed["participants"][0]["email"] = "private@example.org"
        case "outsider":
            outsider = person("Uncaptured Person", "older roster text")
            changed["participants"].append(outsider)
            changed["participant_order"].append(outsider["id"])
            changed["records_sha256"] = content_hash(changed["participants"])
        case unreachable:
            assert_never(unreachable)
    path = tmp_path / "cohort.json"
    path.write_bytes(canonical_bytes(changed))
    # When / Then: admission fails before the caller can create an artifact tree.
    with pytest.raises(ValueError):
        load_authorized_cohort(path, bundle)
    assert not (tmp_path / "output").exists()


def test_empty_record_has_unavailable_cosines_and_remains_in_order(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: two substantive records and one empty current participant.
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: the full-cohort text matrices are formed.
    features = text_features(cohort)
    # Then: empty text is unavailable rather than a zero-similarity assertion.
    assert features.ids == cohort.ids
    assert features.represented == (0, 1)
    assert features.cosine.shape == (3, 3)
    assert np.isnan(features.cosine[2]).all() and np.isnan(features.cosine[:, 2]).all()
    assert np.isclose(features.cosine[0, 0], 1)


def test_count_lda_and_tfidf_nmf_use_actual_models_without_fallback(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: a real small corpus with a known source order.
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    features = text_features(cohort)
    # When: both requested models are fitted.
    lda, nmf = topic_weights(features), topic_weights(features, nonnegative=True)
    # Then: exact participating IDs and finite, complementary/nonnegative weights survive.
    assert lda.ids == nmf.ids == cohort.ids[:2]
    assert lda.actual_class.endswith(".LatentDirichletAllocation")
    assert nmf.actual_class.endswith(".NMF")
    assert np.allclose(lda.weights.sum(axis=1), 1)
    assert np.isfinite(nmf.weights).all() and (nmf.weights >= 0).all()


def test_all_empty_records_report_insufficient_data_without_model_substitution(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: eligible participants whose substantive fields are all blank.
    for row in document["participants"]:
        row["background"] = ""
    document["records_sha256"] = content_hash(document["participants"])
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: a topic representation is requested.
    topics = topic_weights(text_features(cohort))
    # Then: no PCA/other fallback or invented coordinates appear.
    assert topics.status == "insufficient_data" and topics.actual_class == ""
    assert topics.ids == () and topics.weights.shape == (0, 2)


def test_display_group_strings_are_not_split_into_claimed_people(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: two contributions carrying the same whole group display string.
    second = copy.deepcopy(bundle["presentations"][0])
    second.update(id="second-talk", title="Another supplied contribution")
    bundle["presentations"].append(second)
    bundle["presentations"][0]["presenter"] = second["presenter"] = "Synthetic A, Synthetic B"
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: descriptive program counts are computed.
    result = compare_texts(bundle, cohort)
    # Then: two contribution records remain one display/group string, not two verified people.
    assert len(result.presentation_words) == 2
    assert result.distinct_presenter_display_strings == 1


def test_render_refuses_occupied_output_without_changing_it(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: an existing output and its original evidence bytes.
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    output = tmp_path / "occupied"
    output.mkdir()
    sentinel = output / "preserved.json"
    sentinel.write_bytes(b"original")
    # When / Then: an attempted refresh refuses and preserves earlier outputs.
    with pytest.raises(VisualizationError):
        render_visualizations(bundle, cohort, output)
    assert sentinel.read_bytes() == b"original"


@pytest.mark.parametrize("changed_field", ["answers", "ids"])
def test_replaced_corpus_cannot_reuse_admitted_source_bindings(
    bundle: PublicBundle,
    document: CohortDocument,
    tmp_path: Path,
    changed_field: Literal["answers", "ids"],
) -> None:
    # Given: admission followed by a changed projection with stale source bindings.
    admitted = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    match changed_field:
        case "answers":
            answers = (
                ("uncaptured changed answer", *admitted.answers[0][1:]),
                *admitted.answers[1:],
            )
            changed = replace(admitted, answers=answers)
        case "ids":
            ids = (PublicId(public_id("person", "uncaptured outsider")), *admitted.ids[1:])
            changed = replace(admitted, ids=ids)
        case unreachable:
            assert_never(unreachable)
    output = tmp_path / "refused"
    # When / Then: rendering rejects changed answers/IDs before output creation.
    with pytest.raises(VisualizationError):
        render_visualizations(bundle, changed, output)
    assert not output.exists()


def test_distinct_display_strings_preserve_published_case(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: separate contributions with display strings differing only in case.
    second = copy.deepcopy(bundle["presentations"][0])
    second.update(
        id="second-talk", title="Another supplied contribution", presenter="synthetic team"
    )
    bundle["presentations"][0]["presenter"] = "Synthetic Team"
    bundle["presentations"].append(second)
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: exact trimmed published display strings are counted.
    result = compare_texts(bundle, cohort)
    # Then: no inferred identity normalization merges different published labels.
    assert result.distinct_presenter_display_strings == 2


def test_render_records_full_coverage_and_actual_artifact_hashes(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given: a source-bound synthetic cohort with an empty row.
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: the real offline chart API renders into a fresh tree.
    manifest_path = render_visualizations(bundle, cohort, tmp_path / "visualizations")
    # Then: the complete ordered scope and actual bytes remain machine-checkable.
    manifest = json.loads(manifest_path.read_text())
    assert manifest["participant_order"] == list(cohort.ids)
    assert manifest["empty_corpus_ids"] == [cohort.ids[2]]
    assert manifest["provider_calls"] == 0 and len(manifest["charts"]) == 6
    for name, receipt in manifest["artifacts"].items():
        assert (
            hashlib.sha256((manifest_path.parent / name).read_bytes()).hexdigest()
            == receipt["sha256"]
        )


@pytest.mark.parametrize("empty", [False, True])
def test_comparison_histograms_share_actual_bar_geometry(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path, empty: bool
) -> None:
    # Given: very different source ranges, or two completely empty corpora.
    if empty:
        document["participants"], document["participant_order"] = [], []
        document["source"]["included_participants"] = 0
        document["source"]["public_view_total_rows"] = 0
        bundle["presentations"] = []
    else:
        abstract = " ".join(["abstract"] * 120)
        bundle["presentations"][0]["abstract"] = abstract
        bundle["presentations"][0]["abstract_sha256"] = hashlib.sha256(
            abstract.encode()
        ).hexdigest()
    document["records_sha256"] = content_hash(document["participants"])
    cohort = load_authorized_cohort(save_cohort(document, tmp_path / "cohort.json"), bundle)
    # When: the real comparative histogram figure is drawn.
    figure = text_comparison(bundle, cohort)
    try:
        figure.canvas.draw()
        first, second = figure.axes[0].containers
        assert isinstance(first, BarContainer) and isinstance(second, BarContainer)
        # Then: actual rectangles share all edges/widths and retain both record totals.
        assert len(first.patches) == len(second.patches) == 15
        assert [(bar.get_x(), bar.get_width()) for bar in first.patches] == [
            (bar.get_x(), bar.get_width()) for bar in second.patches
        ]
        assert sum(bar.get_height() for bar in first.patches) == len(cohort.ids)
        assert sum(bar.get_height() for bar in second.patches) == len(bundle["presentations"])
    finally:
        plt.close(figure)


@pytest.mark.parametrize(
    "pairs",
    [
        ((0, 1), (1, 2)),
        ((0, 1), (1, 2), (3, 4), (4, 5)),
        ((0, 1), (0, 2), (0, 3)),
    ],
)
def test_network_node_ids_do_not_collide_with_edge_weights(
    pairs: tuple[tuple[int, int], ...], tmp_path: Path
) -> None:
    from scipy.sparse import csr_matrix

    from symposium.organizing.visualization_charts import participant_network, save_chart
    from symposium.organizing.visualization_data import PublicId, TextFeatures

    # Two isolated records, as in a real cohort, keep the isolate panel populated.
    count = 3 + max(index for pair in pairs for index in pair)
    ids = tuple(PublicId(f"person-{index:016x}") for index in range(count))
    cosine = np.zeros((count, count))
    for first, second in pairs:
        cosine[first, second] = cosine[second, first] = 0.3
    empty = csr_matrix((count, 0))
    features = TextFeatures(ids, empty, empty, (), tuple(range(count)), cosine)
    summary = participant_network(features)
    receipt = save_chart(summary.figure, tmp_path / "network.png")
    assert len(summary.edges) == len(pairs)
    assert receipt.overlapping_text_pairs == 0
