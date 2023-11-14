from __future__ import annotations

import logging
from typing import Any, List, Tuple

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import interpolate
from shapely.geometry import LineString, Point, Polygon

from pyvibracore.results.plot_utils import _north_arrow, _scalebar


def _sound_prediction(
    power: float, k2: float, period: float, levels: List[float]
) -> NDArray:
    distance = np.arange(1e-5, 500, step=0.2)
    noise = (
        power
        - (-10 * np.log10(period / 12))
        - (20 * np.log10(distance) + 0.005 * distance + 9.1)
        + k2
    )

    # interpolate and predict
    f = interpolate.interp1d(
        noise, distance, kind="cubic", assume_sorted=False, fill_value="extrapolate"
    )
    space = f(levels)

    # raise warning
    if any([item > 500 for item in space]):
        logging.warning(
            "One or more distances exceeds the 500 meter mark. "
            "Please note that this methode extrapolate the values from this point."
        )

    return space


def map_sound(
    buildings: gpd.GeoDataFrame,
    source_location: Point | LineString | Polygon,
    building_name: str,
    power: float,
    k2: float,
    period: float,
    title: str = "Legend:",
    figsize: Tuple[float, float] = (10.0, 12.0),
    settings: dict | None = None,
    **kwargs: Any,
) -> plt.Figure:
    """
    Create map of the input building settings.

    Parameters
    ----------
    buildings:
        GeoDataFrame of the input buildings
    source_location:
        location of the vibration source
    building_name:
        name of the building
    power:
        source power [dB]
    k2:
        Correction term [dB]
    period:
        Operating period of the building code [hours]
    title:
        Legend title
    figsize:
        Size of the activate figure, as the `plt.figure()` argument.
    settings:
        Plot settings used in plot: default settings are:

        .. code-block:: python

            {
                "source_location": {"label": "Trillingsbron", "color": "blue"},
                "levels": [
                    {
                        "label": ">80 db [0 dagen]",
                        "level": 80,
                        "color": "darkred",
                    },
                    {
                        "label": ">75 db [5 dagen]",
                        "level": 75,
                        "color": "red",
                    },
                    {
                        "label": ">70 db [15 dagen]",
                        "level": 70,
                        "color": "orange",
                    },
                    {
                        "label": ">65 db [30 dagen]",
                        "level": 65,
                        "color": "darkgreen",
                    },
                    {
                        "label": ">60 db [50 dagen]",
                        "level": 60,
                        "color": "green",
                    },
                ],
            }
    **kwargs:
        All additional keyword arguments are passed to the `pyplot.subplots()` call.

    Returns
    -------
    Figure
    """
    if settings is None:
        settings = {
            "source_location": {"label": "Trillingsbron", "color": "blue"},
            "levels": [
                {
                    "label": ">80 db [0 dagen]",
                    "level": 80,
                    "color": "darkred",
                },
                {
                    "label": ">75 db [5 dagen]",
                    "level": 75,
                    "color": "red",
                },
                {
                    "label": ">70 db [15 dagen]",
                    "level": 70,
                    "color": "orange",
                },
                {
                    "label": ">65 db [30 dagen]",
                    "level": 65,
                    "color": "darkgreen",
                },
                {
                    "label": ">60 db [50 dagen]",
                    "level": 60,
                    "color": "lightgreen",
                },
            ],
        }

    kwargs_subplot = {
        "figsize": figsize,
        "tight_layout": True,
    }

    kwargs_subplot.update(kwargs)

    fig, axes = plt.subplots(**kwargs_subplot)

    gpd.GeoSeries(source_location).plot(
        ax=axes, color=settings["source_location"]["color"], alpha=1, zorder=1, aspect=1
    )

    building = buildings.get(buildings["name"] == building_name)
    if building.empty:
        raise ValueError(f"No buildings with name {building_name}.")

    building.plot(ax=axes, zorder=2, color="gray", aspect=1)
    buildings.where(buildings["name"] != building_name).plot(
        ax=axes, zorder=2, color="lightgray", aspect=1
    )

    # plot contour
    levels = [values["level"] for values in settings["levels"]]
    distances = _sound_prediction(power, k2, period, levels=levels)
    colors = [values["color"] for values in settings["levels"]]
    for distance, color in zip(distances, colors):
        gpd.GeoSeries(building.buffer(distance).exterior).plot(
            ax=axes, zorder=3, color=color, aspect=1
        )

    # plot name
    for idx, row in buildings.iterrows():
        x = row.geometry.centroid.xy[0][0]
        y = row.geometry.centroid.xy[1][0]

        axes.annotate(
            idx,
            xy=(x, y),
            horizontalalignment="center",
        )

    # add legend
    axes.legend(
        title=title,
        title_fontsize=18,
        fontsize=15,
        loc="lower right",
        handles=[
            patches.Patch(
                facecolor=value["color"],
                label=value["label"],
                alpha=0.9,
                linewidth=2,
                edgecolor="black",
            )
            for value in settings["levels"]
        ],
    )

    _north_arrow(axes)
    _scalebar(axes)

    return fig


def get_normative_building(
    buildings: gpd.GeoDataFrame,
    location: Polygon | LineString | Point,
) -> str | None:
    """
    Get the name of the closest building with one of the follwing category:

        - "woonfunctie",
        - "gezondheidsfunctie",
        - "onderwijsfunctie"

    Parameters
    ----------
    buildings:
        GeoDataFrame that holds the building information
    location:
        Geometry of the source location

    Returns
    -------
    name: str
    """

    category = ["woonfunctie", "gezondheidsfunctie", "onderwijsfunctie"]

    gdf = buildings.get(
        [
            any(item in category for item in row.split(",")) if row else False
            for row in buildings["gebruiksdoel"].to_list()
        ]
    )
    if gdf.empty:
        logging.error(f"ValueError: No buildings with category {category}.")
        return None
    # FIXME: SettingWithCopyWarning
    with pd.option_context("mode.chained_assignment", None):
        gdf["distance"] = gdf.distance(location)
    return gdf.sort_values("distance", na_position="last").iloc[0].get("name")
