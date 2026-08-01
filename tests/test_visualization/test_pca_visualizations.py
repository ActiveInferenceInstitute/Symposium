#!/usr/bin/env python3
"""Real tests for the enhanced PCA analysis visualizations.

Covers every ``PCAAnalyzer`` method by asserting both the returned success
status AND that the expected output file is actually produced. These are
real-data tests (no mocks for the plotting pipeline).
"""

import numpy as np
import pytest
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from symposium.visualization.pca_analysis import PCAAnalyzer


def create_sample_documents():
    """Create sample documents for testing (reused from the old demo)."""
    documents = [
        "Active inference is a theoretical framework explaining perception action and learning based on free energy principle",
        "The free energy principle suggests that biological systems minimize surprise through predictive processing",
        "Bayesian brain hypothesis proposes that the brain implements probabilistic inference for perception",
        "Predictive coding is a neural theory where the brain constantly predicts sensory input",
        "Markov blankets define boundaries between systems and their environment in active inference",
        "Neural networks in the brain process information through synaptic connections and firing patterns",
        "Neuroscience research investigates brain structure function and cognitive processes",
        "Computational neuroscience models neural systems using mathematical and computational methods",
        "Machine learning algorithms learn patterns from data without explicit programming",
        "Deep learning uses artificial neural networks with multiple layers for complex pattern recognition",
        "Reinforcement learning trains agents through reward feedback in dynamic environments",
        "Cognitive science studies mental processes including attention memory and decision making",
        "Embodied cognition emphasizes the role of bodily experience in cognitive processes",
        "Consciousness and awareness remain fundamental questions in cognitive science research",
    ]
    labels = [
        "Active Inference",
        "Active Inference",
        "Active Inference",
        "Active Inference",
        "Active Inference",
        "Neuroscience",
        "Neuroscience",
        "Neuroscience",
        "Machine Learning",
        "Machine Learning",
        "Machine Learning",
        "Cognitive Science",
        "Cognitive Science",
        "Cognitive Science",
    ]
    return documents, labels


@pytest.fixture
def pca_data():
    """Build a vectorizer + fitted PCA from sample documents."""
    documents, labels = create_sample_documents()
    vectorizer = TfidfVectorizer(
        max_features=100, stop_words="english", min_df=1, ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    n_components = min(10, len(documents) - 1)
    pca = PCA(n_components=n_components, random_state=42, whiten=True)
    reduced_matrix = pca.fit_transform(tfidf_matrix.toarray())
    return pca, reduced_matrix, vectorizer, labels


def _assert_produced(analyzer_method, output_dir, filename, *args, **kwargs):
    """Call an analyzer method and assert success + file existence."""
    output = output_dir / filename
    result = analyzer_method(*args, output_path=output, **kwargs)
    assert result is True
    assert output.exists()


def test_scree_plot(pca_data, tmp_path):
    pca, _, _, _ = pca_data
    _assert_produced(PCAAnalyzer().create_scree_plot, tmp_path, "scree.png", pca, title="Scree")


def test_loadings_plot(pca_data, tmp_path):
    pca, _, vectorizer, _ = pca_data
    _assert_produced(
        PCAAnalyzer().create_loadings_plot, tmp_path, "loadings.png", pca, vectorizer, n_features=5
    )


def test_biplot(pca_data, tmp_path):
    pca, reduced, vectorizer, labels = pca_data
    _assert_produced(
        PCAAnalyzer().create_biplot, tmp_path, "biplot.png", pca, reduced, vectorizer, labels
    )


def test_loadings_heatmap(pca_data, tmp_path):
    pca, _, vectorizer, _ = pca_data
    _assert_produced(
        PCAAnalyzer().create_loadings_heatmap,
        tmp_path,
        "heatmap.png",
        pca,
        vectorizer,
        n_features=10,
    )


def test_component_correlation(pca_data, tmp_path):
    pca, reduced, _, _ = pca_data
    _assert_produced(
        PCAAnalyzer().create_component_correlation_plot, tmp_path, "corr.png", reduced, pca
    )


def test_3d_component_plot(pca_data, tmp_path):
    pca, reduced, _, labels = pca_data
    if reduced.shape[1] < 3:
        pytest.skip("Need >=3 components for 3D plot")
    _assert_produced(
        PCAAnalyzer().create_3d_component_plot, tmp_path, "3d.png", reduced, pca, labels
    )


def test_3d_component_plot_too_few_dims(tmp_path):
    """3D plot must refuse when fewer than 3 components are available."""
    analyzer = PCAAnalyzer()
    reduced = np.zeros((5, 2))
    assert analyzer.create_3d_component_plot(reduced, None, ["a"] * 5, tmp_path / "x.png") is False


def test_save_loadings_table(pca_data, tmp_path):
    pca, _, vectorizer, _ = pca_data
    out = tmp_path / "loadings.csv"
    assert PCAAnalyzer().save_loadings_table(pca, vectorizer, out) is True
    assert out.exists()
    content = out.read_text()
    assert "component" in content and "feature" in content


def test_comprehensive_pca_report(pca_data, tmp_path):
    pca, reduced, vectorizer, labels = pca_data
    results = PCAAnalyzer().create_comprehensive_pca_report(
        pca, reduced, vectorizer, labels, tmp_path, prefix="pca_test"
    )
    # Every requested visualization must succeed and leave a real file.
    assert results
    expected_files = [
        "pca_test_scree_plot.png",
        "pca_test_loadings.png",
        "pca_test_biplot.png",
        "pca_test_loadings_heatmap.png",
        "pca_test_component_correlations.png",
        "pca_test_loadings_table.csv",
    ]
    if reduced.shape[1] >= 3:
        expected_files.append("pca_test_3d_components.png")
    for name, ok in results.items():
        assert ok is True
    for fname in expected_files:
        assert (tmp_path / fname).exists()


def test_false_variance_annotation_guard(tmp_path):
    """Scree plot must not annotate unattained variance thresholds (fix #2)."""
    # Tiny cumulative variance that never reaches 80% would previously annotate
    # "1 component for 80% variance" via np.argmax(all-False)==0. Just ensure the
    # plot still renders without error in that edge case.
    pca = PCA(n_components=3, random_state=42)
    data = np.random.RandomState(0).rand(20, 5)
    pca.fit(data)
    out = tmp_path / "low_variance_scree.png"
    assert PCAAnalyzer().create_scree_plot(pca, out) is True
    assert out.exists()
