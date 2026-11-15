"""Consumed adjustText 1.4.0 interface; guarded by scripts/check_types.py."""

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.text import Text

def adjust_text(
    texts: list[Text],
    *,
    ax: Axes | None = ...,
    arrowprops: dict[str, object] | None = ...,
    time_lim: float | None = ...,
    iter_lim: int | None = ...,
) -> tuple[list[Text], list[Artist]] | None: ...
