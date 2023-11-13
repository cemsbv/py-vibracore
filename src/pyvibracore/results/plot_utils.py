from __future__ import annotations

from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar


def _north_arrow(axes: plt.Axes) -> None:
    """Add north arrow to axes"""
    x, y, arrow_length = 0.05, 0.98, 0.1
    axes.annotate(
        "N",
        xy=(x, y),
        xytext=(x, y - arrow_length),
        arrowprops=dict(facecolor="black", width=5, headwidth=15),
        ha="center",
        va="center",
        fontsize=20,
        xycoords=axes.transAxes,
    )


def _scalebar(axes: plt.Axes) -> None:
    """Add size bar to axes"""
    scalebar = AnchoredSizeBar(
        axes.transData,
        20,
        "20 m",
        "lower left",
        pad=1,
        color="black",
        frameon=True,
        size_vertical=2,
    )

    axes.add_artist(scalebar)
