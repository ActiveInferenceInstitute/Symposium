"""Interpretable program and participant/presentation text comparisons."""

from __future__ import annotations

from collections import Counter
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from sklearn.feature_extraction.text import TfidfVectorizer

from .models import PublicBundle
from .visualization_charts import BLUE, TEAL
from .visualization_data import AuthorizedCohort, TextComparison, compare_texts


def program_overview(bundle: PublicBundle, comparison: TextComparison) -> Figure:
    """Count contributions and display descriptive abstract vocabulary, without person counts."""
    presentations = bundle["presentations"]
    counts = Counter(row["contribution_type"] for row in presentations)
    kinds = sorted(counts, key=lambda kind: (-counts[kind], kind))
    figure, axes = plt.subplots(
        2, 1, figsize=(8.27, 9.5), layout="constrained", gridspec_kw={"height_ratios": [1, 1.5]}
    )
    axes[0].barh([fill(kind, 33) for kind in kinds], [counts[kind] for kind in kinds], color=BLUE)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, max(counts.values(), default=1) * 1.15)
    axes[0].set_xlabel("Approved program contributions")
    for i, kind in enumerate(kinds):
        axes[0].text(counts[kind] + 0.3, i, str(counts[kind]), va="center")
    axes[0].set_title("Contribution formats")
    documents = [row["abstract"] for row in presentations if row["abstract"].strip()]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)
    if documents and any(vectorizer.build_analyzer()(text) for text in documents):
        matrix = vectorizer.fit_transform(documents)
        weights = np.asarray(matrix.mean(axis=0)).ravel()
        terms = vectorizer.get_feature_names_out()
        selected = sorted(range(len(terms)), key=lambda i: (-float(weights[i]), str(terms[i])))[:12]
        axes[1].barh(
            [str(terms[i]) for i in selected], [float(weights[i]) for i in selected], color=TEAL
        )
        axes[1].invert_yaxis()
        axes[1].set_xlabel("Mean TF-IDF weight across nonblank abstracts")
    else:
        axes[1].text(
            0.5, 0.5, "No abstract text available", ha="center", transform=axes[1].transAxes
        )
        axes[1].set_axis_off()
    axes[1].set_title("Descriptive abstract vocabulary")
    figure.suptitle(
        f"{bundle['event']['year']} Presenter Program\n{len(presentations)} contributions · "
        f"{len(comparison.pending_abstracts)} awaiting abstracts",
        fontsize=17,
    )
    figure.supxlabel(
        f"{comparison.distinct_presenter_display_strings} distinct presenter display/group strings; "
        "not a verified count of people.\nSubmitted text only; missing abstracts remain missing.",
        fontsize=9,
    )
    return figure


def text_comparison(bundle: PublicBundle, cohort: AuthorizedCohort) -> Figure:
    """Compare lengths in shared bins and completeness in separate source scopes."""
    comparison = compare_texts(bundle, cohort)
    figure, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    series = (comparison.participant_words, comparison.presentation_words)
    labels = (
        f"Participant answers (N={len(cohort.ids)})",
        f"Presentation abstracts (N={len(bundle['presentations'])})",
    )
    bins = np.histogram_bin_edges(np.concatenate(series), bins=15)
    for values, label, color in zip(series, labels, (BLUE, TEAL), strict=True):
        axes[0].hist(values, bins=bins, alpha=0.45, label=label, color=color)
    axes[0].set(xlabel="Whitespace-delimited words · blanks included", ylabel="Records")
    axes[0].legend(fontsize=8)
    missing = [sum(words == 0 for words in values) for values in series]
    totals = [len(values) for values in series]
    axes[1].barh(
        ("Participant substantive answers", "Presentation abstracts"),
        [total - blank for total, blank in zip(totals, missing, strict=True)],
        color=BLUE,
        label="Nonblank",
    )
    axes[1].barh(
        ("Participant substantive answers", "Presentation abstracts"),
        missing,
        left=[total - blank for total, blank in zip(totals, missing, strict=True)],
        color="#c3ccd0",
        label="Blank",
    )
    axes[1].set_xlabel("Records in their separate source scopes")
    axes[1].legend(fontsize=8)
    figure.suptitle("Participant answers and presentation abstracts · descriptive text comparison")
    return figure
