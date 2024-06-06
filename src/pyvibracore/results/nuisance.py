from __future__ import annotations

from typing import Any, List, Sequence, Tuple

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.interpolate import interpolate
from shapely.geometry import LineString, Point, Polygon

from pyvibracore.results.plot_utils import _north_arrow, _scalebar

# CUR 166-1997 Tabel 5.20 Factor Cfc
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

# SBR-B Trillingen meet en beoordelingsrichtlijnen hinder voor personen in gebouwen [2002] art. 10.5.4 Table 4
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
    target_value_one: List[float] | NDArray | Sequence,
    target_value_two: List[float] | NDArray | Sequence,
    target_value_three: List[float] | NDArray | Sequence,
    vibration_velocity_eff: List[float] | NDArray,
    vibration_velocity_per: List[float] | NDArray,
    distance: List[float] | NDArray,
) -> NDArray:
    """
    Based on the 'SBR-B Trillingen meet en beoordelingsrichtlijnen hinder voor personen in gebouwen [2002]'.

    Parameters
    ----------
    target_value_one:
        target value SBR-B [2002] art. 10.5.1 [-]
    target_value_two:
        target value SBR-B [2002] art. 10.5.1 [-]
    target_value_three:
        target value SBR-B [2002] art. 10.5.1 [-]
    vibration_velocity_eff:
        vibration velocity [mm/s]
    vibration_velocity_per: list
        vibration velocity [mm/s]
    distance:
        distance with respect to building [m]

    Returns
    -------
    space: NDArray
    """

    df = pd.DataFrame(
        {
            "vibrationVelocity_per": vibration_velocity_per,
            "vibrationVelocity_eff": vibration_velocity_eff,
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
    target_value_one_spaces = f_eff(target_value_one)
    target_value_two_spaces = f_eff(target_value_two)

    # interpolate and predict
    f_per = interpolate.interp1d(
        df["vibrationVelocity_per"],
        df["distance"],
        kind="cubic",
        assume_sorted=False,
        fill_value="extrapolate",
    )
    target_value_three_spaces = f_per(target_value_three)

    return np.min(
        [
            np.max([target_value_two_spaces, target_value_three_spaces], axis=0),
            target_value_one_spaces,
        ],
        axis=0,
    )


def df_nuisance(
    response_dict: dict,
    cfc: float,
    u_eff: float,
    period: float,
) -> pd.DataFrame:
    """
    Get a DataFrame that holds the distance of the different durations

    Parameters
    ----------
    response_dict:
        response of the single prepal or cur166 endpoint.
    u_eff:
        Vibration transfer to part of a building (u_eff) CUR 166-1997 page 514 [-]
    cfc:
        Vibration transfer to part of a building (Cfc) CUR 166-1997 table 5.20 or 5.21 [-]
    period:
        Operating period of the building code [hours]

    Returns
    -------
    dataframe
    """
    arr = np.array(response_dict["data"]["vibrationVelocity"])
    a_one, a_two, a_three = [*zip(*TARGET_VALUE.values())]

    distances = _nuisance_prediction(
        target_value_one=a_one,
        target_value_two=a_two,
        target_value_three=a_three,
        vibration_velocity_per=arr * cfc * u_eff * np.sqrt(period / 12),
        vibration_velocity_eff=arr * cfc * u_eff,
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
    a_one, a_two, a_three = [*zip(*levels)]

    distances = _nuisance_prediction(
        target_value_one=a_one,
        target_value_two=a_two,
        target_value_three=a_three,
        vibration_velocity_per=arr * cfc * u_eff * np.sqrt(period / 12),
        vibration_velocity_eff=arr * cfc * u_eff,
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
