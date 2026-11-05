"""Real separate-process rendering keeps sparse-network labels tied to source IDs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from matplotlib import get_cachedir

from symposium.organizing.models import PublicBundle, canonical_bytes, content_hash
from symposium.organizing.visualizations import CohortDocument
from tests.test_organizing_site import bundle as bundle
from tests.test_organizing_visualizations import document as document
from tests.test_organizing_visualizations import person


def test_sparse_network_labeled_positions_match_across_python_hash_seeds(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    # Given six admitted records with exactly one pair of matching answer texts.
    rows = [
        person("Synthetic Alpha", "robot control learning"),
        person("Synthetic Beta", "robot control learning"),
        person("Synthetic Gamma", "ocean ecology"),
        person("Synthetic Delta", "music harmony"),
        person("Synthetic Epsilon", "soil microbiology"),
        person("Synthetic Empty"),
    ]
    document["participants"] = rows
    document["participant_order"] = [row["id"] for row in rows]
    document["records_sha256"] = content_hash(rows)
    document["source"]["included_participants"] = len(rows)
    document["source"]["public_view_total_rows"] = len(rows)
    cohort_path = tmp_path / "cohort.json"
    cohort_path.write_bytes(canonical_bytes(document))
    bundle_path = tmp_path / "program.json"
    bundle_path.write_bytes(canonical_bytes(bundle))
    program = """
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from symposium.organizing.models import load_bundle
from symposium.organizing.visualization_charts import participant_network
from symposium.organizing.visualization_data import text_features
from symposium.organizing.visualizations import load_authorized_cohort

cohort = load_authorized_cohort(Path(sys.argv[1]), load_bundle(Path(sys.argv[2])))
features = text_features(cohort)
network = participant_network(features)
try:
    assert len(network.edges) == 1 and len(network.isolated_ids) == 4
    network.figure.canvas.draw()
    labels = {str(identifier)[7:15] for identifier in cohort.ids}
    positions = sorted(
        (text.get_text(), tuple(round(float(value), 12) for value in text.get_position()))
        for text in network.figure.axes[0].texts if text.get_text() in labels
    )
    assert len(positions) == 2
    print(json.dumps(positions))
finally:
    plt.close(network.figure)
"""
    observations: list[str] = []
    # When the real chart is drawn in interpreters with different string-hash seeds.
    for seed in map(str, range(8)):
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = seed
        environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        environment["MPLCONFIGDIR"] = get_cachedir()
        result = subprocess.run(
            [sys.executable, "-B", "-c", program, str(cohort_path), str(bundle_path)],
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        observations.append(json.dumps(json.loads(result.stdout), sort_keys=True))
    # Then identical numeric seeds assign the same actual label positions to the same IDs.
    assert len(set(observations)) == 1
