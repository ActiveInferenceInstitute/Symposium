"""Real tests for DistributionPlotter statistical visualization paths."""

from sklearn.feature_extraction.text import TfidfVectorizer

from symposium.visualization.distributions import DistributionPlotter


def _docs():
    return [
        "Active inference free energy principle predictive processing surprise",
        "Machine learning neural networks deep learning pattern recognition",
        "Cognitive science neuroscience computational modeling Bayesian inference",
        "Bayesian inference probability belief updating active perception",
    ]


def test_plot_document_length_distribution(tmp_path):
    out = tmp_path / "len.png"
    assert (
        DistributionPlotter().plot_document_length_distribution(
            _docs(), ["a", "b", "c", "d"], "Title", out
        )
        is True
    )
    assert out.exists()


def test_plot_tfidf_distribution(tmp_path):
    docs = _docs()
    vectorizer = TfidfVectorizer(max_features=50, stop_words="english")
    matrix = vectorizer.fit_transform(docs)
    out = tmp_path / "tfidf.png"
    assert DistributionPlotter().plot_tfidf_distribution(matrix, vectorizer, "TF-IDF", out) is True
    assert out.exists()


def test_plot_tfidf_distribution_single_document(tmp_path):
    """Single-document input must not crash or silently zero the CI (fix #5)."""
    docs = ["Only a single document with several words in it."]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(docs)
    out = tmp_path / "tfidf1.png"
    assert DistributionPlotter().plot_tfidf_distribution(matrix, vectorizer, "TF-IDF", out) is True
    assert out.exists()


def test_plot_category_comparison(tmp_path):
    out = tmp_path / "cat.png"
    assert (
        DistributionPlotter().plot_category_comparison(_docs(), ["a", "b", "b", "a"], "Cats", out)
        is True
    )
    assert out.exists()
