from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Tuple

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Point, Polygon

from pyvibracore.results.plot_utils import _north_arrow, _scalebar


@dataclass(frozen=True)
class VibrationResults:
    """
    Dataclass that holds the information from `/cur166/validation/multi` or `/prepal/validation/multi`

    Attributes
    -----------
    gdf: gpd.GeoDataFrame

    """

    gdf: gpd.GeoDataFrame

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "VibrationResults":
        """
        Stores the response of the VibraCore endpoint

        Parameters
        ----------
        response_dict:
           The resulting response of a call to `/cur166/validation/multi` or `/prepal/validation/multi`
        """
        return cls(
            gpd.read_file(json.dumps(response_dict), driver="GeoJSON").set_crs(
                "EPSG:28992", allow_override=True
            )
        )

    def map(
        self,
        source_location: Point | LineString | Polygon,
        title: str = "Legend:",
        figsize: Tuple[float, float] = (10.0, 12.0),
        settings: dict | None = None,
        **kwargs: Any,
    ) -> plt.Figure:
        """
        Create map plot of the results

        Parameters
        ----------
        source_location:
            location of the vibration source
        title:
            Legend title
        figsize:
            Size of the activate figure, as the `plt.figure()` argument.
        settings:
            Plot settings used in plot: default settings are:

            .. code-block:: python

                {
                    "source_location": {"label": "Trillingsbron", "color": "black"},
                    "insufficient_cat1": {
                        "label": "Voldoet Niet - Cat.1",
                        "color": "orange",
                    },
                    "insufficient_cat2": {"label": "Voldoet Niet - Cat.2", "color": "red"},
                    "sufficient": {"label": "Voldoet", "color": "green"},
                }
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.

        Returns
        -------
        Figure
        """
        if settings is None:
            settings = {
                "source_location": {"label": "Trillingsbron", "color": "black"},
                "insufficient_cat1": {
                    "label": "Voldoet Niet - Cat.1",
                    "color": "orange",
                },
                "insufficient_cat2": {"label": "Voldoet Niet - Cat.2", "color": "red"},
                "sufficient": {"label": "Voldoet", "color": "green"},
            }

        kwargs_subplot = {
            "figsize": figsize,
            "tight_layout": True,
        }

        kwargs_subplot.update(kwargs)

        fig, axes = plt.subplots(**kwargs_subplot)

        gpd.GeoSeries(source_location).plot(
            ax=axes,
            color=settings["source_location"]["color"],
            alpha=1,
            zorder=1,
            aspect=1,
        )

        # plot category 1 zone of influence
        if "insufficient_cat1" in settings.keys():
            self.gdf.where(
                np.logical_and(self.gdf["cat"] == "one", ~self.gdf["check"])
            ).plot(
                ax=axes,
                zorder=2,
                color=settings["insufficient_cat1"]["color"],
                aspect=1,
            )

        if "insufficient_cat2" in settings.keys():
            self.gdf.where(
                np.logical_and(self.gdf["cat"] == "two", ~self.gdf["check"])
            ).plot(
                ax=axes,
                zorder=2,
                color=settings["insufficient_cat2"]["color"],
                aspect=1,
            )

        if "sufficient" in settings.keys():
            self.gdf.where(self.gdf.check).plot(
                ax=axes, zorder=2, color=settings["sufficient"]["color"], aspect=1
            )
        self.gdf.where(self.gdf.check).buffer(self.gdf.x_required).plot(
            ax=axes, alpha=0.25, zorder=1, aspect=1
        )
        self.gdf.where(~self.gdf.check).buffer(self.gdf.x_required).plot(
            ax=axes, alpha=0.6, zorder=1, aspect=1
        )

        for idx, row in self.gdf.iterrows():
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
                for value in settings.values()
            ],
        )

        _north_arrow(axes)
        _scalebar(axes)

        return fig


def map_payload(
    gdf: gpd.GeoDataFrame,
    source_location: Point | LineString | Polygon,
    title: str = "Legend:",
    figsize: Tuple[float, float] = (10.0, 12.0),
    settings: dict | None = None,
    **kwargs: Any,
) -> plt.Figure:
    """
    Create map of the input building settings.

    Parameters
    ----------
    gdf:
        GeoDataFrame of the input buildings
    source_location:
        location of the vibration source
    title:
        Legend title
    figsize:
        Size of the activate figure, as the `plt.figure()` argument.
    settings:
        Plot settings used in plot: default settings are:

        .. code-block:: python

            {
                "source_location": {"label": "Trillingsbron", "color": "black"},
                "sensitive_cat1": {
                    "label": "Monumentaal/ gevoelig - Cat.1",
                    "color": "blue",
                },
                "sensitive_cat2": {
                    "label": "Monumentaal/ gevoelig - Cat.2",
                    "color": "cyan",
                },
                "normal_cat1": {"label": "Normaal - Cat.1", "color": "orange"},
                "normal_cat2": {"label": "Normaal - Cat.2", "color": "olive"},
            }

    **kwargs:
        All additional keyword arguments are passed to the `pyplot.subplots()` call.

    Returns
    -------
    Figure
    """
    if settings is None:
        settings = {
            "source_location": {"label": "Trillingsbron", "color": "black"},
            "sensitive_cat1": {
                "label": "Monumentaal/ gevoelig - Cat.1",
                "color": "blue",
            },
            "sensitive_cat2": {
                "label": "Monumentaal/ gevoelig - Cat.2",
                "color": "cyan",
            },
            "normal_cat1": {"label": "Normaal - Cat.1", "color": "orange"},
            "normal_cat2": {"label": "Normaal - Cat.2", "color": "olive"},
        }

    kwargs_subplot = {
        "figsize": figsize,
        "tight_layout": True,
    }

    kwargs_subplot.update(kwargs)

    fig, axes = plt.subplots(**kwargs_subplot)

    if "source_location" in settings.keys():
        gpd.GeoSeries(source_location).plot(
            ax=axes,
            color=settings["source_location"]["color"],
            alpha=1,
            zorder=1,
            aspect=1,
        )

    if "sensitive_cat1" in settings.keys():
        gdf.where(
            np.logical_and(
                gdf["category"] == "one",
                np.logical_or(gdf["monumental"], gdf["vibrationSensitive"]),
            )
        ).plot(ax=axes, zorder=2, color=settings["sensitive_cat1"]["color"], aspect=1)

    if "normal_cat1" in settings.keys():
        gdf.where(
            np.logical_and(
                gdf["category"] == "one",
                ~np.logical_or(gdf["monumental"], gdf["vibrationSensitive"]),
            )
        ).plot(ax=axes, zorder=2, color=settings["normal_cat1"]["color"], aspect=1)

    if "sensitive_cat2" in settings.keys():
        gdf.where(
            np.logical_and(
                gdf["category"] == "two",
                np.logical_or(gdf["monumental"], gdf["vibrationSensitive"]),
            )
        ).plot(ax=axes, zorder=2, color=settings["sensitive_cat2"]["color"], aspect=1)

    if "normal_cat2" in settings.keys():
        gdf.where(
            np.logical_and(
                gdf["category"] == "two",
                ~np.logical_or(gdf["monumental"], gdf["vibrationSensitive"]),
            )
        ).plot(ax=axes, zorder=2, color=settings["normal_cat2"]["color"], aspect=1)

    for idx, row in gdf.iterrows():
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
            for value in settings.values()
        ],
    )

    _north_arrow(axes)
    _scalebar(axes)

    return fig


def plot_reduction(
    response_dict: dict,
    sensitive: bool = False,
    figsize: Tuple[float, float] = (8, 8),
    **kwargs: Any,
) -> plt.Figure:
    """
    PLot single vibration prediction reduction plot

    Parameters
    ----------
    response_dict:
        response of the single prepal or cur166 endpoint.
    sensitive:
        Default is False
        Flag that indicates if vibration sensitive results are included
    figsize:
        Size of the activate figure, as the `plt.figure()` argument.
    **kwargs:
        All additional keyword arguments are passed to the `pyplot.subplots()` call.

    Returns
    -------

    """
    kwargs_subplot = {
        "figsize": figsize,
        "tight_layout": True,
    }

    kwargs_subplot.update(kwargs)

    fig, axes = plt.subplots(**kwargs_subplot)

    axes.axvline(
        x=response_dict["calculation"]["distance"],
        linestyle="-",
        label="Building distance",
        color="green",
    )

    # normal
    axes.axhline(
        y=response_dict["calculation"]["failureValueVibrationVelocity"],
        linestyle="-",
        label="Vr",
        color="orange",
    )
    axes.axvline(
        x=response_dict["calculation"]["distanceRequired"],
        linestyle="-",
        label="Distance required",
        color="black",
    )
    axes.plot(
        response_dict["data"]["distance"],
        response_dict["data"]["vibrationVelocity"],
        linestyle="-",
        label="Vd",
        color="blue",
    )

    # sensitive
    if sensitive:
        axes.axhline(
            y=response_dict["calculation"][
                "failureValueVibrationVelocityVibrationSensitive"
            ],
            linestyle="--",
            label="$Vr_{sensitive}$",
            color="orange",
        )
        axes.axvline(
            x=response_dict["calculation"][
                "distanceRequiredVelocityVibrationSensitive"
            ],
            linestyle="--",
            label="Distance required",
            color="black",
        )
        # excitation
        axes.axhline(
            y=response_dict["calculation"]["failureValueExcitationVelocity"],
            linestyle="-.",
            label="$Vr_{velocity}$",
            color="orange",
        )
        axes.axvline(
            x=response_dict["calculation"]["distanceRequiredExcitationVelocity"],
            linestyle="-.",
            label="Distance required",
            color="black",
        )
        axes.plot(
            response_dict["data"]["distance"],
            response_dict["data"]["vibrationVelocityVibrationSensitive"],
            linestyle="--",
            label="Vd",
            color="blue",
        )

    axes.set_xlabel("Distance from source [m]")
    axes.set_ylabel("Vibration velocity [mm/s]")
    axes.set_xlim(0, 50)
    axes.set_ylim(0, 30)
    axes.legend(
        title=f"Vibration prediction: {response_dict.get('ID')}",
        title_fontsize=12,
        fontsize=9,
        loc="upper right",
    )

    return fig
