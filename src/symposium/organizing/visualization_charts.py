"""Participant charts with external keys and explicit empty-text coverage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.text import Text

from .visualization_data import (
    FIELDS,
    SEED,
    THRESHOLD,
    AuthorizedCohort,
    TextFeatures,
    TopicWeights,
    VisualizationError,
)

BLUE: Final = "#1f647e"
TEAL: Final = "#46a395"
GRAY: Final = "#c3ccd0"


@dataclass(frozen=True, slots=True)
class ChartReceipt:
    """Final-draw text diagnostics, retained for subsequent independent visual review."""

    path: str
    text_items: int
    overlapping_text_pairs: int


def save_chart(figure: Figure, path: Path) -> ChartReceipt:
    """Draw final text boxes and save into a fresh private chart directory."""
    if path.exists() or path.is_symlink():
        raise VisualizationError("Chart output already exists")
    try:
        figure.set_dpi(180)
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        # Tick labels of a switched-off axis, or of ticks outside the view limits,
        # stay "visible" but are never drawn; they must not count as overlaps.
        undrawn: set[int] = set()
        for axes in figure.axes:
            for axis in (axes.xaxis, axes.yaxis):
                if not axes.axison:
                    undrawn.update(id(text) for text in axis.findobj(Text))
                    continue
                low, high = sorted(axis.get_view_interval())
                slack = 1e-9 * max(abs(high - low), 1.0)
                for tick in [*axis.get_major_ticks(), *axis.get_minor_ticks()]:
                    location = tick.get_loc()
                    if location is not None and not low - slack <= location <= high + slack:
                        undrawn.update((id(tick.label1), id(tick.label2)))
        texts = [
            text
            for text in figure.findobj(Text)
            if text.get_visible() and text.get_text() and id(text) not in undrawn
        ]
        boxes = [text.get_window_extent(renderer) for text in texts]
        overlaps = sum(
            int(first.overlaps(second))
            for i, first in enumerate(boxes)
            for second in boxes[i + 1 :]
        )
        figure.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
        return ChartReceipt(path.name, len(texts), overlaps)
    finally:
        plt.close(figure)


def participant_coverage(cohort: AuthorizedCohort) -> Figure:
    """Count all participants, including those with no substantive answers."""
    figure, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    counts = [sum(bool(row[i]) for row in cohort.answers) for i in range(len(FIELDS))]
    labels = [field.replace("_", " ").title() for field in FIELDS]
    axes[0].barh(labels, counts, color=BLUE)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, max(1, len(cohort.ids)) * 1.12)
    axes[0].set_xlabel("Participants with nonblank answers")
    for i, value in enumerate(counts):
        axes[0].text(value + 0.4, i, str(value), va="center")
    axes[1].hist(cohort.answered_counts, bins=np.arange(-0.5, 8.5), color=TEAL, rwidth=0.85)
    axes[1].set(xticks=range(8), xlabel="Answered substantive fields", ylabel="Participants")
    figure.suptitle(f"Participant response coverage · all {len(cohort.ids)} public-view records")
    return figure


def topic_distribution(topics: TopicWeights, total: int) -> Figure:
    """Show complementary two-topic LDA weights in one dimension without endpoint labels."""
    figure, axis = plt.subplots(figsize=(11, 5), layout="constrained")
    if topics.weights.size:
        axis.hist(topics.weights[:, 0], bins=np.linspace(0, 1, 16), color=BLUE, edgecolor="white")
        axis.set(
            xlim=(0, 1), xlabel="Topic 1 weight (Topic 2 = 1 − Topic 1)", ylabel="Participants"
        )
        axis.text(
            0, -0.24, "Topic 1: " + ", ".join(topics.terms[0]), transform=axis.transAxes, fontsize=9
        )
        axis.text(
            0, -0.33, "Topic 2: " + ", ".join(topics.terms[1]), transform=axis.transAxes, fontsize=9
        )
    else:
        axis.text(
            0.5,
            0.5,
            "Insufficient answer text for two topics",
            ha="center",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    axis.set_title(
        f"Answer-text topic weights · {len(topics.ids)}/{total} represented participants"
    )
    return figure


def nmf_projection(topics: TopicWeights, total: int) -> Figure:
    """Keep sparse component weights readable with symlog axes and an external ID key."""
    figure, axis = plt.subplots(figsize=(10, 7), layout="constrained")
    if topics.weights.size:
        axis.scatter(topics.weights[:, 0], topics.weights[:, 1], color=TEAL, alpha=0.7, s=48)
        axis.set_xscale("symlog", linthresh=0.001)
        axis.set_yscale("symlog", linthresh=0.001)
        axis.set(xlabel="NMF component 1 weight · symlog", ylabel="NMF component 2 weight · symlog")
        axis.grid(alpha=0.2)
        axis.text(
            0,
            -0.14,
            "Individual coordinates and public IDs: participant-nmf-key.csv. No point labels overlaid.",
            fontsize=9,
            transform=axis.transAxes,
        )
    else:
        axis.text(
            0.5,
            0.5,
            "Insufficient answer text for two components",
            ha="center",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    axis.set_title(
        f"Sparse answer-text components · {len(topics.ids)}/{total} represented participants"
    )
    return figure


@dataclass(frozen=True, slots=True)
class NetworkSummary:
    """Every cohort node remains accounted for; only supported text edges are drawn."""

    figure: Figure
    edges: tuple[tuple[str, str, float], ...]
    isolated_ids: tuple[str, ...]


def participant_network(features: TextFeatures) -> NetworkSummary:
    """Enlarge connected text edges; group isolated nodes without unreadable labels."""
    graph = nx.Graph()
    graph.add_nodes_from(features.ids)
    edges = tuple(
        (str(features.ids[i]), str(features.ids[j]), float(features.cosine[i, j]))
        for i in range(len(features.ids))
        for j in range(i + 1, len(features.ids))
        if np.isfinite(features.cosine[i, j]) and features.cosine[i, j] >= THRESHOLD
    )
    graph.add_weighted_edges_from(edges)
    isolates = tuple(
        str(identifier) for identifier in features.ids if graph.degree(identifier) == 0
    )
    # Small subgraph views can iterate a hash-dependent node set. Keep source order.
    connected = nx.Graph()
    connected.add_nodes_from(identifier for identifier in features.ids if graph.degree(identifier))
    connected.add_weighted_edges_from(edges)
    figure, axes = plt.subplots(
        1, 2, figsize=(12, 6), layout="constrained", gridspec_kw={"width_ratios": [2, 1]}
    )
    if connected.number_of_nodes():
        positions = nx.spring_layout(connected, seed=SEED)
        nx.draw_networkx(
            connected,
            positions,
            ax=axes[0],
            node_color=BLUE,
            node_size=90,
            width=3,
            edge_color=TEAL,
            with_labels=False,
        )
        # Each node ID is pushed away from that node's own edges, so it cannot sit
        # on an edge or on the edge's midpoint weight label in any orientation.
        for identifier, xy in positions.items():
            away = np.zeros(2)
            for neighbor in connected.neighbors(identifier):
                step = np.asarray(xy) - np.asarray(positions[neighbor])
                away += step / (np.linalg.norm(step) or 1.0)
            if np.linalg.norm(away) < 0.5:
                # Interior node of a straight chain: go perpendicular to its edges.
                neighbor = next(iter(connected.neighbors(identifier)))
                step = np.asarray(positions[neighbor]) - np.asarray(xy)
                away = np.array([-step[1], step[0]])
            away = away / (np.linalg.norm(away) or 1.0)
            axes[0].text(
                xy[0] + 0.1 * away[0],
                xy[1] + 0.1 * away[1],
                str(identifier)[7:15],
                fontsize=10,
                ha="left" if away[0] > 0.3 else "right" if away[0] < -0.3 else "center",
                va="bottom" if away[1] > 0.3 else "top" if away[1] < -0.3 else "center",
            )
        nx.draw_networkx_edge_labels(
            connected,
            positions,
            ax=axes[0],
            edge_labels={(u, v): f"{weight:.2f}" for u, v, weight in edges},
            font_size=10,
            rotate=False,
        )
        axes[0].margins(0.3)
    else:
        axes[0].text(
            0.5, 0.5, "No text pairs reach the threshold", transform=axes[0].transAxes, ha="center"
        )
    x = np.arange(len(isolates)) % 8
    y = -(np.arange(len(isolates)) // 8)
    axes[1].scatter(x, y, s=45, color=GRAY)
    axes[1].set_title(
        f"{len(isolates)} isolated records\nIDs retained in network.json", fontsize=11
    )
    for axis in axes:
        axis.set_axis_off()
    figure.suptitle(
        f"Answer-text similarity ≥ {THRESHOLD} · {len(edges)} edges · {len(features.ids)} records"
    )
    figure.supxlabel(
        "Text similarity is not evidence of collaboration, expertise or social relationships.",
        fontsize=10,
    )
    return NetworkSummary(figure, edges, isolates)
