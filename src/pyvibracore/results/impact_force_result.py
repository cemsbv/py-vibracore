from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Sequence, Tuple

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar


@dataclass(frozen=True)
class MultiCalculationData:
    gdf: gpd.GeoDataFrame

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "MultiCalculationData":
        return cls(
            gdf=gpd.read_file(json.dumps(response_dict), driver="GeoJSON"),
        )

    def plot(
        self,
        figsize: Tuple[float, float] = (10.0, 12.0),
        settings: dict | None = None,
        **kwargs: Any,
    ) -> plt.Figure:
        """
        Plots the CPT and soil table data.

        Parameters
        ----------
        figsize:
            Size of the activate figure, as the `plt.figure()` argument.
        settings:
            Plot settings used in plot: default settings are:

            {
                "hue": "max",
                "title": "Maximale slagkracht [kN]",
                "xlabel": "X-coördinaat",
                "ylabel": "Y-coördinaat"
            }
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.

        Returns
        -------
        fig:
            The matplotlib Figure
        """
        kwargs_settings = {
            "hue": "max",
            "title": "Maximale slagkracht [kN]",
            "xlabel": "X-coördinaat",
            "ylabel": "Y-coördinaat",
        }

        if settings:
            kwargs_settings.update(settings)

        if kwargs_settings["hue"] not in ["max", "base", "Q90", "Q95"]:
            raise ValueError(
                f"The value {kwargs_settings['hue']} is not in [max, base, Q90, Q95]"
            )

        kwargs_subplot = {
            "figsize": figsize,
            "tight_layout": True,
        }

        kwargs_subplot.update(kwargs)

        fig, axes = plt.subplots(**kwargs_subplot)

        # Create figure
        self.gdf.plot(
            kwargs_settings.get("hue", "max"),
            ax=axes,
            legend=True,
            figsize=(15, 10),
            legend_kwds={"orientation": "vertical"},
            cmap="RdYlGn_r",  # 'jet',
            markersize=150,
            marker="v",
            aspect=1,
        )

        # add CPT name to plot
        for idx, row in self.gdf.iterrows():
            axes.annotate(
                row["id"],
                xy=(row["x"], row["y"]),
                horizontalalignment="center",
                fontsize=20,
                xytext=(row["x"], row["y"] + 3),
            )

        # Set label and title for figure
        axes.set_xlabel(xlabel=kwargs_settings.get("xlabel", ""), size=15)
        axes.set_ylabel(ylabel=kwargs_settings.get("ylabel", ""), size=15)
        axes.set_title(label=kwargs_settings.get("title", ""), size=25)

        # Add north arrow
        x, y, arrow_length = 0.95, 0.98, 0.1
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

        # scale bar
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

        return fig


@dataclass(frozen=True)
class ImpactForceTable:
    """
    Object that contains the impact force related data-traces.

    Attributes:
    ------------
    betaFrictionalResistance: Sequence[float]
        beta frictional resistance [kN]
    betaPointResistance: Sequence[float]
        beta point resistance [kN]
    correctedConeResistance: Sequence[float]
        corrected cone resistance [Mpa]
    depthOffset: Sequence[float]
        CPT depth [m w.r.t. Reference]
    frictionalResistance: Sequence[float]
        frictional resistance [kN]
    pointResistance: Sequence[float]
        point resistance [kN]
    sheetResistance: Sequence[float]
        sheet resistance [kN]
    slotResistance: Sequence[float]
        slot resistance [kN]
    totalResistance: Sequence[float]
        total resistance [kN]
    """

    betaFrictionalResistance: Sequence[float] | None
    betaPointResistance: Sequence[float] | None
    correctedConeResistance: Sequence[float]
    depthOffset: Sequence[float]
    frictionalResistance: Sequence[float]
    pointResistance: Sequence[float]
    sheetResistance: Sequence[float] | None
    slotResistance: Sequence[float]
    totalResistance: Sequence[float]

    def __post_init__(self) -> None:
        raw_lengths = []
        for values in self.__dict__.values():
            if values:
                raw_lengths.append(len(values))
        if len(list(set(raw_lengths))) > 1:
            raise ValueError("All values in this dataclass must have the same length.")

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "ImpactForceTable":
        """
        Stores the response of the VibraCore endpoint

        Parameters
        ----------
        response_dict:
           The resulting response of a call to `impact-force/calculation/single`
        """
        return cls(
            betaFrictionalResistance=response_dict.get("betaFrictionalResistance"),
            betaPointResistance=response_dict.get("betaPointResistance"),
            correctedConeResistance=response_dict.get("correctedConeResistance"),
            depthOffset=response_dict.get("depthOffset"),
            frictionalResistance=response_dict.get("frictionalResistance"),
            pointResistance=response_dict.get("pointResistance"),
            sheetResistance=response_dict.get("sheetResistance"),
            slotResistance=response_dict.get("slotResistance"),
            totalResistance=response_dict.get("totalResistance"),
        )

    @property
    def dataframe(self) -> pd.DataFrame:
        """The pandas.DataFrame representation"""
        return pd.DataFrame(self.__dict__).dropna(axis="rows", how="any")  # type: ignore


@dataclass(frozen=True)
class SingleCalculationData:
    """
    Object that contains the impact force related data.

    Attributes:
    ------------
    table: ImpactForceTable
    installationLevel: float
        installation level [m w.r.t. Reference]
    maximumForce: float
        total resistance [kN]
    pointForce: float
        resistance at the base [kN]
    """

    table: ImpactForceTable
    installationLevel: float
    maximumForce: float
    pointForce: float | None

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "SingleCalculationData":
        """
        Stores the response of the VibraCore endpoint

        Parameters
        ----------
        response_dict:
           The resulting response of a call to `impact-force/calculation/single`
        """
        return cls(
            table=ImpactForceTable.from_api_response(response_dict["data"]),
            installationLevel=response_dict["installationLevel"],
            maximumForce=response_dict["maximumForce"],
            pointForce=response_dict.get("pointForce"),
        )

    def plot(
        self,
        figsize: Tuple[float, float] = (10.0, 12.0),
        **kwargs: Any,
    ) -> plt.Figure:
        """
        Plots the resistance data.

        Parameters
        ----------
        figsize:
            Size of the activate figure, as the `plt.figure()` argument.
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.

        Returns
        -------
        fig:
            The matplotlib Figure
        """
        kwargs_subplot = {
            "figsize": figsize,
            "tight_layout": True,
        }

        kwargs_subplot.update(kwargs)

        fig, axes = plt.subplots(**kwargs_subplot)

        for item in [
            "totalResistance",
            "frictionalResistance",
            "slotResistance",
            "pointResistance",
        ]:
            axes.plot(
                self.table.__getattribute__(item),
                self.table.depthOffset,
                label=item,
            )

        axes.axvline(
            x=self.installationLevel,
            c="k",
            linestyle="dashed",
            label=f"max force ({self.maximumForce.__round__(2)})",
        )
        axes.axhline(
            y=self.installationLevel,
            c="k",
            linestyle="dotted",
            label=f"installation level ({self.installationLevel})",
        )
        axes.set_xlabel("Resistance [kN]")
        axes.grid()

        return fig
