"""Estilo común, elipses de dispersión y guardado de figuras."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

from .config import DPI, FIG_DIR, FIG_FORMATS, color, marker

STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": True,
    "legend.fontsize": 9,
    "savefig.dpi": DPI,
}


def apply_style():
    plt.rcParams.update(STYLE)


def italic(name: str) -> str:
    """Nombre en cursiva para mathtext, sin poner en cursiva el código de accesión."""
    if "(" in name:
        sp, acc = name.split(" (", 1)
        return rf"$\it{{{sp.replace(' ', r'\ ')}}}$ ({acc}"
    return rf"$\it{{{name.replace(' ', r'\ ')}}}$"


def cov_ellipse(ax, x, y, n_std: float = 2.0, **kw):
    """Elipse de covarianza que abarca ``n_std`` desviaciones estándar.

    Representa la dispersión del grupo, no un intervalo de confianza de la media.
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if len(x) < 3:
        return None
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * n_std * np.sqrt(np.maximum(vals, 0))
    e = Ellipse((x.mean(), y.mean()), width, height, angle=angle, **kw)
    ax.add_patch(e)
    return e


def scatter_groups(ax, df, xcol, ycol, groups, *, ellipse=True, point_size=22,
                   mean_size=150, alpha=0.75, ellipse_alpha=0.15, mean_marker=None,
                   group_col="group"):
    """Puntos individuales, centro del grupo y elipse de 2 DE para cada grupo."""
    handles = []
    for g in groups:
        d = df[df[group_col] == g].dropna(subset=[xcol, ycol])
        if d.empty:
            continue
        c, m = color(g), marker(g)
        if ellipse:
            cov_ellipse(ax, d[xcol], d[ycol], facecolor=c, edgecolor=c,
                        alpha=ellipse_alpha, lw=0.8, zorder=1)
        ax.scatter(d[xcol], d[ycol], s=point_size, color=c, marker=m,
                   alpha=alpha, lw=0, zorder=2)
        h = ax.scatter(d[xcol].mean(), d[ycol].mean(), s=mean_size, color=c,
                       marker=mean_marker or m, edgecolor="white", lw=1.5,
                       zorder=3, label=italic(g))
        handles.append(h)
    return handles


def panel_label(ax, text, x=-0.08, y=1.04):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=13, fontweight="bold",
            va="bottom", ha="left")


def save(fig, name: str):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in FIG_FORMATS:
        p = FIG_DIR / f"{name}.{ext}"
        kw = {"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tif" else {}
        fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white", **kw)
        paths.append(p)
    plt.close(fig)
    return paths
