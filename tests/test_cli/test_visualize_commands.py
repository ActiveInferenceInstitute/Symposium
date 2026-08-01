"""Real (no-mock) tests for the visualization CLI command bodies.

Exercise ``visualize_embeddings``, ``visualize_networks``, ``visualize_distributions``
and ``visualize_all`` against a temporary directory of Markdown documents and assert
that the expected output artifacts are produced on disk.
"""

import argparse


def _make_markdown_dir(tmp_path, n=4):
    """Create n Markdown docs in tmp_path (plus a nested people/ dir for 'all')."""
    docs = [
        ("alpha.md", "Active inference free energy principle predictive processing"),
        ("beta.md", "Machine learning neural networks deep learning"),
        ("gamma.md", "Cognitive science neuroscience computational modeling"),
        ("delta.md", "Bayesian inference probability belief updating"),
    ]
    for fname, text in docs[:n]:
        (tmp_path / fname).write_text(text)
    people = tmp_path / "people" / "researcher_one"
    people.mkdir(parents=True)
    (people / "profile.md").write_text("Active inference research background and methods")
    return tmp_path


def _args(**overrides):
    base = {
        "input_dir": "i",
        "output_dir": "o",
        "method": "pca",
        "n_components": 2,
        "threshold": 0.1,
        "max_terms": 50,
        "max_features": 5000,
        "label": None,
        "layout": "spring",
        "log_level": "WARNING",
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_visualize_embeddings_produces_files(tmp_path):
    from symposium.cli.visualize import visualize_embeddings

    src = _make_markdown_dir(tmp_path)
    out = tmp_path / "out"
    visualize_embeddings(_args(input_dir=str(src), output_dir=str(out)))

    assert (out / "embedding_pca_2d.png").exists()
    assert (out / "word_cloud.png").exists()
    assert (out / "term_frequency.png").exists()


def test_visualize_embeddings_single_file(tmp_path):
    from symposium.cli.visualize import visualize_embeddings

    md = tmp_path / "single.md"
    md.write_text("Active inference free energy principle")
    out = tmp_path / "out"
    visualize_embeddings(_args(input_dir=str(md), output_dir=str(out), label="doc"))

    # A single document cannot yield a multi-dimensional scatter, but the
    # aggregations (word cloud / term frequency) must still be produced.
    assert (out / "word_cloud.png").exists()
    assert (out / "term_frequency.png").exists()


def test_visualize_networks_produces_files(tmp_path):
    from symposium.cli.visualize import visualize_networks

    src = _make_markdown_dir(tmp_path)
    out = tmp_path / "out"
    visualize_networks(_args(input_dir=str(src), output_dir=str(out)))

    assert (out / "similarity_network_spring.png").exists()
    assert (out / "community_analysis.png").exists()


def test_visualize_distributions_produces_file(tmp_path):
    from symposium.cli.visualize import visualize_distributions

    src = _make_markdown_dir(tmp_path)
    out = tmp_path / "out"
    visualize_distributions(_args(input_dir=str(src), output_dir=str(out)))

    assert (out / "document_length_distribution.png").exists()


def test_visualize_all_produces_files(tmp_path):
    from symposium.cli.visualize import visualize_all

    src = _make_markdown_dir(tmp_path)
    out = tmp_path / "out"
    visualize_all(_args(input_dir=str(src), output_dir=str(out)))

    # Embeddings: 4 docs -> >=4 components -> rendered as a 3D plot.
    assert (out / "embedding_pca_3d.png").exists()
    assert (out / "word_cloud.png").exists()
    assert (out / "similarity_network_spring.png").exists()
    assert (out / "document_length_distribution.png").exists()
    assert (out / "community_analysis.png").exists()


def test_visualize_networks_single_file(tmp_path):
    """Single-file input must be accepted (previously silently yielded nothing)."""
    from symposium.cli.visualize import visualize_networks

    md = tmp_path / "single.md"
    md.write_text("Active inference free energy principle predictive processing")
    out = tmp_path / "out"
    visualize_networks(_args(input_dir=str(md), output_dir=str(out)))

    assert (out / "similarity_network_spring.png").exists()
