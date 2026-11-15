"""Failure evidence for batches that retain completed and partial output files."""

from collections.abc import Mapping
from pathlib import Path


class BatchIncompleteError(RuntimeError):
    """A batch finished its attempts but not all requested outputs persisted."""

    def __init__(
        self,
        requested: int,
        completed: Mapping[str, object],
        failures: Mapping[str, str],
        output_dir: Path,
    ) -> None:
        self.requested = requested
        self.completed = dict(completed)
        self.failures = dict(failures)
        self.output_dir = output_dir
        super().__init__(
            f"Batch incomplete: {len(completed)}/{requested} fully persisted; "
            f"failed: {', '.join(failures)}. Completed and partial files were preserved "
            f"under {output_dir}"
        )
