"""Consumed wordcloud 1.9.6 interface; guarded by scripts/check_types.py."""

from typing import Literal, Self

import numpy as np
from numpy.typing import NDArray

class WordCloud:
    def __init__(
        self,
        *,
        width: int = ...,
        height: int = ...,
        background_color: str | None = ...,
        max_words: int = ...,
        colormap: str | None = ...,
        contour_width: float = ...,
        contour_color: str = ...,
        min_font_size: int = ...,
        max_font_size: int | None = ...,
        font_step: int = ...,
        prefer_horizontal: float = ...,
        relative_scaling: float | Literal["auto"] = ...,
        normalize_plurals: bool = ...,
        stopwords: set[str] | None = ...,
    ) -> None: ...
    def generate(self, text: str) -> Self: ...
    def to_array(self, copy: bool | None = ...) -> NDArray[np.uint8]: ...
    def __array__(self, copy: bool | None = ...) -> NDArray[np.uint8]: ...
