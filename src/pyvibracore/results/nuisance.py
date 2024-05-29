from __future__ import annotations

from typing import Any, List, Tuple

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import interpolate
from scipy.interpolate import interpolate
from shapely.geometry import LineString, Point, Polygon

from pyvibracore.results.plot_utils import _north_arrow, _scalebar

# CUR 166-1997 Tabel 5.20 Factor Cfc voor flooren
CFC_FACTOR_FLOORS = {
    "driving": {
        "concrete": {"Cfc": 1.4, "Vfc": 0.17},
        "wood": {"Cfc": 1.4, "Vfc": 0.17},
    },
    "vibrate": {
        "concrete": {"Cfc": 1.7, "Vfc": 0.27},
        "wood": {"Cfc": 2.5, "Vfc": 0.44},
    },
}

TARGET_VALUE = {
    "<= 1 day": [0.8, 6, 0.4],
    "2 days": [0.72, 6, 0.38],
    "3 days": [0.64, 6, 0.34],
    "4 days": [0.56, 6, 0.36],
    "5 days": [0.48, 6, 0.32],
    ">= 6 days; <26 days": [0.4, 6, 0.3],
    ">= 26 days; <78 days": [0.3, 6, 0.2],
}


def _nuisance_prediction(
    A1: List[float],
    A2: List[float],
    A3: List[float],
    vibrationVelocity_eff: List[float],
    vibrationVelocity_per: List[float],
    distance: List[float],
) -> NDArray:
    """
    Based on the 'Handleiding meten en rekenen industrielawaai' 2004 methode l.
    More information: https://open.overheid.nl/Details/ronl-15eb5528-d835-4f6a-b3a1-fc0851b334f9/1

    Parameters
    ----------
    A1:
        target value [-]
    A2:
        target value [-]
    A3:
        target value [-]
    vibrationVelocity_eff:
        vibration velocity [mm/s]
    vibrationVelocity_per: list
        vibration velocity [mm/s]
    distance:
        distance with respect ot building [m]

    Returns
    -------
    space: NDArray
    """

    df = pd.DataFrame(
        {
            "vibrationVelocity_per": vibrationVelocity_per,
            "vibrationVelocity_eff": vibrationVelocity_eff,
            "distance": distance,
        }
    ).drop_duplicates(subset=["vibrationVelocity_per", "vibrationVelocity_eff"])

    # interpolate and predict
    f_eff = interpolate.interp1d(
        df["vibrationVelocity_eff"],
        df["distance"],
        kind="cubic",
        assume_sorted=False,
        fill_value="extrapolate",
    )
    A1_d = f_eff(A1)
    A2_d = f_eff(A2)

    # interpolate and predict
    f_per = interpolate.interp1d(
        df["vibrationVelocity_per"],
        df["distance"],
        kind="cubic",
        assume_sorted=False,
        fill_value="extrapolate",
    )
    A3_d = f_per(A3)

    return np.min([np.max([A2_d, A3_d], axis=0), A1_d], axis=0)


def df_nuisance(
    response_dict: dict,
    cfc: float,
    u_eff: float,
    period: float,
) -> pd.DataFrame:
    arr = np.array(response_dict["data"]["vibrationVelocity"])
    distances = _nuisance_prediction(
        *zip(*TARGET_VALUE.values()),
        vibrationVelocity_per=arr * cfc * u_eff * np.sqrt(period / 12),
        vibrationVelocity_eff=arr * cfc * u_eff,
        distance=response_dict["data"]["distance"],
    )

    return pd.DataFrame(
        {
            "labels": TARGET_VALUE.keys(),
            "distance": distances,
        }
    )


def map_nuisance(
    buildings: gpd.GeoDataFrame,
    source_location: Point | LineString | Polygon,
    building_name: str,
    response_dict: dict,
    cfc: float,
    u_eff: float,
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
    response_dict:
        response of the single prepal or cur166 endpoint.
    source_location:
        location of the vibration source
    building_name:
        name of the building
    u_eff:
        Vibration transfer to part of a building (u_eff) CUR 166-1997 page 514 [-]
    cfc:
        Vibration transfer to part of a building (Cfc) CUR 166-1997 table 5.20 or 5.21 [-]
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
                    "label": "<= 1 day",
                    "color": "darkred",
                },
                {
                    "label": ">= 6 days; <26 days",
                    "color": "orange",
                },
                {
                    "label": ">= 26 days; <78 days",
                    "color": "green",
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

    buildings.where(buildings["name"] == building_name).plot(
        ax=axes, zorder=2, color="gray", aspect=1
    )
    buildings.where(buildings["name"] != building_name).plot(
        ax=axes, zorder=2, color="lightgray", aspect=1
    )

    # plot contour
    levels = [TARGET_VALUE[values["label"]] for values in settings["levels"]]
    arr = np.array(response_dict["data"]["vibrationVelocity"])
    distances = _nuisance_prediction(
        *zip(*levels),
        vibrationVelocity_per=arr * cfc * u_eff * np.sqrt(period / 12),
        vibrationVelocity_eff=arr * cfc * u_eff,
        distance=response_dict["data"]["distance"],
    )
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
