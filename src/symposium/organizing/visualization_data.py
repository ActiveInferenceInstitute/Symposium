"""Immutable inputs and numerical evidence for public-text visualization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, NewType

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .models import PublicBundle, PublicParticipant, content_hash, public_id, validate_bundle

PublicId = NewType("PublicId", str)
SubstantiveField = Literal[
    "background",
    "pragmatic_value",
    "epistemic_value",
    "active_inference_application",
    "challenges",
    "learning_needs",
    "future_impact",
]
FIELDS: Final[tuple[SubstantiveField, ...]] = (
    "background",
    "pragmatic_value",
    "epistemic_value",
    "active_inference_application",
    "challenges",
    "learning_needs",
    "future_impact",
)
SEED: Final = 45
THRESHOLD: Final = 0.2
PUBLIC_VIEW: Final = "https://docs.superhuman.com/d/_dfDPUsAuSgQ/Public-Participants_suOKkHtg"


@dataclass(frozen=True, slots=True)
class VisualizationError(ValueError):
    """A source or output does not satisfy the visualization contract."""

    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class AuthorizedCohort:
    """Detached substantive answers from a checked, designated public-view capture."""

    ids: tuple[PublicId, ...]
    answers: tuple[tuple[str, ...], ...]
    records_sha256: str
    capture_sha256: str
    source_url: str
    projection_sha256: str

    @property
    def documents(self) -> tuple[str, ...]:
        return tuple("\n\n".join(text for text in row if text) for row in self.answers)

    @property
    def answered_counts(self) -> tuple[int, ...]:
        return tuple(sum(bool(text) for text in row) for row in self.answers)


def projection_hash(ids: tuple[PublicId, ...], answers: tuple[tuple[str, ...], ...]) -> str:
    """Bind the immutable ordered corpus projection to the admitted source records."""
    return content_hash({"participant_order": ids, "answers": answers})


def authorized_records(bundle: PublicBundle, rows: list[PublicParticipant]) -> AuthorizedCohort:
    """Validate closed participant records without borrowing the older bundle roster.

    This helper validates records only; the loader separately checks source identity,
    year, cardinality, order and hashes before returning the authorized value.
    """
    checked = validate_bundle({**bundle, "participants": rows})["participants"]
    if any(row["id"] != public_id("person", row["name"].strip().casefold()) for row in checked):
        raise VisualizationError("Participant ID differs from its supplied display name")
    ids = tuple(PublicId(row["id"]) for row in checked)
    answers = tuple(tuple(row[field].strip() for field in FIELDS) for row in checked)
    return AuthorizedCohort(
        ids, answers, content_hash(checked), "", PUBLIC_VIEW, projection_hash(ids, answers)
    )


@dataclass(frozen=True, slots=True)
class TextFeatures:
    """Full ordered matrices; zero-vector membership remains explicit."""

    ids: tuple[PublicId, ...]
    counts: csr_matrix
    tfidf: csr_matrix
    terms: tuple[str, ...]
    represented: tuple[int, ...]
    cosine: NDArray[np.float64]


def text_features(cohort: AuthorizedCohort) -> TextFeatures:
    """Fit a shared count vocabulary to answer bodies, retaining every cohort row."""
    vectorizer = CountVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)
    analyzer = vectorizer.build_analyzer()
    has_tokens = any(analyzer(document) for document in cohort.documents)
    if has_tokens:
        counts = csr_matrix(vectorizer.fit_transform(cohort.documents))
        terms = tuple(str(term) for term in vectorizer.get_feature_names_out())
        tfidf = csr_matrix(TfidfTransformer(sublinear_tf=True).fit_transform(counts))
        represented = tuple(int(i) for i in np.flatnonzero(counts.getnnz(axis=1)))
        cosine = np.asarray(cosine_similarity(tfidf), dtype=np.float64)
    else:
        counts = csr_matrix((len(cohort.ids), 0), dtype=np.int64)
        tfidf = csr_matrix((len(cohort.ids), 0), dtype=np.float64)
        terms, represented = (), ()
        cosine = np.zeros((len(cohort.ids), len(cohort.ids)), dtype=np.float64)
    mask = np.zeros(len(cohort.ids), dtype=bool)
    mask[list(represented)] = True
    cosine[~np.logical_and.outer(mask, mask)] = np.nan
    return TextFeatures(cohort.ids, counts, tfidf, terms, represented, cosine)


@dataclass(frozen=True, slots=True)
class TopicWeights:
    """Actual model output, or an explicit insufficient-data state; never fallback."""

    ids: tuple[PublicId, ...]
    weights: NDArray[np.float64]
    terms: tuple[tuple[str, ...], ...]
    actual_class: str
    status: str
    parameters: tuple[tuple[str, str | int | float], ...] = ()


def topic_weights(features: TextFeatures, *, nonnegative: bool = False) -> TopicWeights:
    """Fit two count-LDA topics or two TF-IDF NMF components with fixed seed."""
    ids = tuple(features.ids[i] for i in features.represented)
    if len(ids) < 2 or len(features.terms) < 2:
        return TopicWeights(ids, np.empty((0, 2)), (), "", "insufficient_data")
    model: NMF | LatentDirichletAllocation
    if nonnegative:
        model = NMF(n_components=2, init="nndsvda", random_state=SEED, max_iter=2000)
        weights = model.fit_transform(features.tfidf[list(features.represented)])
        parameters = (
            ("n_components", 2),
            ("random_state", SEED),
            ("max_iter", 2000),
            ("init", "nndsvda"),
            ("tol", 0.0001),
        )
    else:
        model = LatentDirichletAllocation(
            n_components=2, random_state=SEED, max_iter=100, learning_method="batch", n_jobs=1
        )
        weights = model.fit_transform(features.counts[list(features.represented)])
        parameters = (
            ("n_components", 2),
            ("random_state", SEED),
            ("max_iter", 100),
            ("learning_method", "batch"),
            ("n_jobs", 1),
        )
    if weights.shape != (len(ids), 2) or not np.isfinite(weights).all():
        raise VisualizationError("Topic model returned an invalid shape or nonfinite values")
    terms = tuple(
        tuple(features.terms[int(i)] for i in np.argsort(component)[::-1][:5])
        for component in model.components_
    )
    return TopicWeights(
        ids,
        weights,
        terms,
        type(model).__module__ + "." + type(model).__name__,
        "succeeded",
        parameters,
    )


@dataclass(frozen=True, slots=True)
class TextComparison:
    """Descriptive lengths compare texts without aligning separate embeddings."""

    participant_words: tuple[int, ...]
    presentation_words: tuple[int, ...]
    pending_abstracts: tuple[str, ...]
    distinct_presenter_display_strings: int


def compare_texts(bundle: PublicBundle, cohort: AuthorizedCohort) -> TextComparison:
    """Keep empty texts and whole presenter display/group strings as supplied."""
    return TextComparison(
        tuple(len(text.split()) for text in cohort.documents),
        tuple(len(row["abstract"].split()) for row in bundle["presentations"]),
        tuple(row["id"] for row in bundle["presentations"] if not row["abstract"].strip()),
        len({row["presenter"].strip() for row in bundle["presentations"]}),
    )
