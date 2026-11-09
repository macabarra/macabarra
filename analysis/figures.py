"""Figuras 2-8 del manuscrito y Figuras S1-S2 del material suplementario.

Figura 1 (imágenes de Fv/Fm) y los paneles fotográficos 4A y 4C no se generan
desde tablas y quedan fuera de este código.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from . import load
from .config import (ACCESSIONS, ALL_ENTRIES, SHORT_LABEL, SPECIES,
                     SPECIES_SUBSET, color, marker)
from .plotting import italic, panel_label, save, scatter_groups
from .stats import format_eq, format_p, ols, stars, welch


# ---------------------------------------------------------------------------
# Figura S1. Programa de temperatura de la cámara
# ---------------------------------------------------------------------------
def supp_fig1():
    d = load.load_chamber()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    hours = np.append(d["hour"].values, 24.0)
    temps = np.append(d["temp"].values, d["temp"].values[-1])
    ymin, ymax = temps.min() - 0.8, temps.max() + 0.8

    # sombreado de los periodos sin luz según la columna 'Luz' del archivo
    dark = (d["light"].values == 0)
    start = None
    for i, is_dark in enumerate(np.append(dark, False)):
        if is_dark and start is None:
            start = hours[i]
        elif not is_dark and start is not None:
            ax.axvspan(start, hours[i], color="0.75", alpha=0.6, lw=0, zorder=0)
            start = None
    ax.step(hours, temps, where="post", color="#574AA0", lw=3, zorder=2)
    ax.set_xlim(0, 24)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(range(25))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(25)], rotation=90)
    ax.set_xlabel("Time (h)", fontweight="bold")
    ax.set_ylabel("Temperature (°C)", fontweight="bold")
    ax.legend(handles=[Patch(color="0.75", alpha=0.6, label="Lights off")],
              loc="upper left", frameon=False)
    return save(fig, "FigS1_chamber_program")


# ---------------------------------------------------------------------------
# Figura S2. Umbrales de daño del PSII e INT
# ---------------------------------------------------------------------------
def _supp_fig2_panel(ax, df, order, ylim, box_color=None):
    for i, g in enumerate(order):
        d = df[df["group"] == g]
        lt10, lt50, lt90, intt = (d[c].mean() for c in ("LT10", "LT50", "LT90", "INT"))
        se10, se90 = d["LT10"].sem(), d["LT90"].sem()
        c = box_color or color(g)
        ax.bar(i, lt10 - lt90, bottom=lt90, width=0.6, color=c, alpha=0.4,
               edgecolor="0.4", lw=1.2, zorder=1)
        ax.hlines(lt50, i - 0.3, i + 0.3, color="black", lw=2, zorder=3)
        ax.errorbar([i, i], [lt10, lt90], yerr=[se10, se90], fmt="none",
                    ecolor="black", capsize=5, lw=1.2, zorder=2)
        ax.scatter(i, intt, s=90, color="black", zorder=4)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([italic(SHORT_LABEL.get(g, g)) for g in order])
    ax.set_ylim(*ylim)
    ax.set_ylabel("Temperature (°C)")
    ax.yaxis.grid(True, ls=":", color="0.85")
    ax.legend(handles=[
        Patch(facecolor="0.85", edgecolor="0.4", label=r"LT$_{10}$–LT$_{90}$"),
        Line2D([], [], color="black", lw=2, label=r"LT$_{50}$"),
        Line2D([], [], color="black", marker="o", ls="", markersize=9, label="INT"),
    ], loc="upper right")


def supp_fig2():
    sp, _ = load.load_lt_int("species")
    ac, _ = load.load_lt_int("accessions")
    order_sp = list(sp.groupby("group")["LT50"].mean().sort_values(ascending=False).index)
    order_ac = ["L. luteus (C98)", "L. luteus (C195)", "L. luteus (C102)", "L. luteus (C226)"]
    fig, axes = plt.subplots(2, 1, figsize=(7, 9))
    _supp_fig2_panel(axes[0], sp, order_sp, (-20, 10))
    _supp_fig2_panel(axes[1], ac, order_ac, (-15, 5), box_color=color("L. luteus"))
    panel_label(axes[0], "A)", -0.12)
    panel_label(axes[1], "B)", -0.12)
    fig.tight_layout(h_pad=2.5)
    return save(fig, "FigS2_PSII_thresholds_INT")


# ---------------------------------------------------------------------------
# Figuras 2 y 3. LT50 frente a INT
# ---------------------------------------------------------------------------
def _lt_int_axes(ax, lim):
    ax.plot(lim, lim, ls="--", color="0.6", lw=1.3, zorder=0)
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[0], lim[1])
    ax.set_xlabel(r"LT$_{50}$ (°C)")
    ax.set_ylabel("INT (°C)")
    ax.text(0.07, 0.93, "Freezing\navoiders", transform=ax.transAxes,
            style="italic", fontsize=12, va="top")
    ax.text(0.86, 0.17, "Freezing\nresistant", transform=ax.transAxes,
            style="italic", fontsize=12, va="top")


def fig2():
    df, _ = load.load_lt_int("species")
    fig, ax = plt.subplots(figsize=(8, 7.5))
    _lt_int_axes(ax, (1.7, -13.3))
    handles = scatter_groups(ax, df, "LT50", "INT", SPECIES, mean_marker="D",
                             mean_size=260)
    m = df.groupby("group")[["LT50", "INT"]].mean()
    arrow = dict(arrowstyle="-|>", lw=2, mutation_scale=16)
    # L. luteus y L. mutabilis: de INT a la diagonal (LT50 = INT)
    for g in ("L. luteus", "L. mutabilis"):
        lt, it = m.loc[g]
        ax.annotate("", xy=(lt, lt), xytext=(lt, it),
                    arrowprops={**arrow, "color": color(g)}, zorder=4)
    lt, it = m.loc["L. luteus"]
    ax.text(lt + 0.25, (lt + it) / 2, r"LT$_{50}$ $\it{L.~lut}$", rotation=90,
            ha="right", va="center", color="0.3")
    # V. faba: de la diagonal a LT50
    lt, it = m.loc["V. faba"]
    ax.annotate("", xy=(lt, it), xytext=(it, it),
                arrowprops={**arrow, "color": color("V. faba")}, zorder=4)
    ax.text((lt + it) / 2, it + 0.25, f"{it - lt:.1f} °C resistant", ha="center",
            va="top", color="0.3")
    ax.legend(handles=handles, title="Species", loc="lower center", markerscale=0.55,
              bbox_to_anchor=(0.5, 0.02))
    return save(fig, "Fig2_LT50_INT_species")


def fig3():
    df, _ = load.load_lt_int("accessions")
    fig, ax = plt.subplots(figsize=(8, 7.5))
    _lt_int_axes(ax, (0, -14))
    handles = scatter_groups(ax, df, "LT50", "INT", ACCESSIONS, mean_size=260)
    ax.legend(handles=handles, title="Accession", loc="lower center", markerscale=0.55,
              bbox_to_anchor=(0.5, 0.02))
    return save(fig, "Fig3_LT50_INT_accessions")


# ---------------------------------------------------------------------------
# Figura 4B y 4D. LT50 frente a daño visible
# ---------------------------------------------------------------------------
def fig4(reference_lines=True):
    sp = load.load_damage("species")
    ac = load.load_damage("accessions")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    for ax, df, groups, ylim, title, lab in (
        (axes[0], sp, ["V. faba", "L. albus", "L. angustifolius", "P. sativum",
                       "L. luteus", "L. mutabilis"], (0.5, -12.5), "Species", "B)"),
        (axes[1], ac, ["L. luteus (C98)", "L. luteus (C102)", "L. luteus (C226)",
                       "L. luteus (C195)"], (0.3, -8.3), "Accession", "D)"),
    ):
        if reference_lines:
            # línea de referencia visual (no es un ajuste) como en la figura original
            ax.plot([0, 100], [ylim[1] + 0.3, 0], ls="--", color="0.7", lw=1)
        h = scatter_groups(ax, df, "damage", "LT50", groups, point_size=18,
                           mean_size=110)
        ax.set_xlim(0, 100)
        ax.set_ylim(*ylim)
        ax.set_xlabel("Damage (%)")
        ax.set_ylabel(r"LT$_{50}$ (°C)")
        ax.set_title(r"LT$_{50}$ vs. Damage (%)", style="italic")
        ax.grid(True, ls="--", color="0.92")
        ax.legend(handles=h, title=title, loc="lower left", fontsize=8, markerscale=0.7)
        panel_label(ax, lab, -0.12)
    fig.tight_layout()
    return save(fig, "Fig4BD_LT50_damage")


# ---------------------------------------------------------------------------
# Figura 5. Azúcares solubles, control frente a congelación
# ---------------------------------------------------------------------------
SUGAR_PANELS = [("fructose", "Fructose"), ("raffinose", "Raffinose"),
                ("glucose", "Glucose"), ("sucrose", "Sucrose"),
                ("stachyose", "Stachyose"), ("total", "Total sugar")]
FIG5_ORDER = ["V. faba", "P. sativum", "L. mutabilis", "L. angustifolius", "L. albus",
              "L. luteus (C98)", "L. luteus (C226)", "L. luteus (C195)", "L. luteus (C102)"]


def sugar_contrasts():
    """Medias ± SE y prueba de Welch (n = 5 plantas) para cada azúcar y entrada.

    Datos: sugars_control_freezing.tsv. Devuelve None si el archivo no existe.
    """
    d = load.load_sugars_treatments()
    if d is None:
        return None
    parts = []
    for g in FIG5_ORDER:
        c = d[(d.group == g) & (d.treatment == "control")]
        f = d[(d.group == g) & (d.treatment == "freezing")]
        for s, _ in SUGAR_PANELS:
            a, b = c[s], f[s]
            if a.std() == 0 and b.std() == 0:
                t, p = np.nan, np.nan
            else:
                t, p = welch(a, b)
            parts.append({"group": g, "sugar": s, "n_control": len(a),
                          "n_freezing": len(b), "control_mean": a.mean(),
                          "control_se": a.sem(), "freezing_mean": b.mean(),
                          "freezing_se": b.sem(), "welch_t": t, "p": p,
                          "signif": stars(p)})
    return pd.DataFrame(parts)


def fig5():
    res = sugar_contrasts()
    if res is None:
        print("  Fig. 5 omitida: falta data/raw/sugars_control_freezing.tsv")
        return None
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    y = np.arange(len(FIG5_ORDER))[::-1]
    h = 0.38
    for ax, (s, label), lab in zip(axes.ravel(), SUGAR_PANELS, "ABCDEF"):
        d = res[res.sugar == s].set_index("group").loc[FIG5_ORDER]
        for yi, (g, r) in zip(y, d.iterrows()):
            c = color(g if g in FIG5_ORDER[:5] else "L. luteus")
            ax.barh(yi + h / 2, r.control_mean, h, xerr=r.control_se, color=c,
                    alpha=0.6, error_kw=dict(capsize=3, lw=1))
            ax.barh(yi - h / 2, r.freezing_mean, h, xerr=r.freezing_se, color=c,
                    alpha=0.6, hatch="////", edgecolor="white",
                    error_kw=dict(capsize=3, lw=1))
            xr = max(r.control_mean + r.control_se, r.freezing_mean + r.freezing_se)
            ax.text(xr * 1.03 + 0.01, yi, r.signif, va="center", fontsize=9,
                    style="italic" if r.signif == "n.s." else "normal")
        ax.axhline(y[4] - 0.5, color="0.2", lw=1)
        ax.set_yticks(y)
        ax.set_yticklabels([italic(g) for g in FIG5_ORDER])
        ax.set_xlabel(rf"{label} (mg g$^{{-1}}$ dry weight)", style="italic")
        ax.xaxis.grid(True, ls=":", color="0.85")
        ax.set_xlim(0, ax.get_xlim()[1] * 1.12)
        panel_label(ax, f"{lab})", -0.02)
    fig.legend(handles=[Patch(facecolor="0.75", label="Control"),
                        Patch(facecolor="0.75", hatch="////", edgecolor="white",
                              label="Freezing")],
               loc="lower center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return save(fig, "Fig5_soluble_sugars")


# ---------------------------------------------------------------------------
# Figuras 6-8. Regresiones
# ---------------------------------------------------------------------------
def regression_frame() -> pd.DataFrame:
    """Una fila por hoja con LT50, azúcares totales (antes de la helada) y
    recuperación (si existe), para las 9 entradas.

    LT50 de especies: LT50_Damage_species.csv (es la columna que reproduce la
    Fig. 8B: y = −0.57x + 4.3, R² = 0.636). LT50 de accesiones:
    LT_INT_accessions.csv. Las filas se emparejan por grupo y orden.
    """
    sp = load.load_damage("species")[["group", "leaf", "LT50"]]
    ac, _ = load.load_lt_int("accessions")
    lt = pd.concat([sp, ac[["group", "leaf", "LT50"]]])
    sug = pd.concat([load.load_sugars("species"), load.load_sugars("accessions")])
    df = lt.merge(sug[["group", "leaf", "total"]], on=["group", "leaf"], how="left")
    rec = [load.load_recovery(l) for l in ("species", "accessions")]
    rec = [r for r in rec if r is not None]
    if rec:
        df = df.merge(pd.concat(rec), on=["group", "leaf"], how="left")
    else:
        df["recovery"] = np.nan
    return df


def _reg_panel(ax, df, xcol, ycol, groups, title, invert_y=False):
    d = df[df.group.isin(groups)].dropna(subset=[xcol, ycol])
    h = scatter_groups(ax, d, xcol, ycol, groups, point_size=22, mean_size=140)
    fit = ols(d[xcol], d[ycol])
    xs = np.linspace(d[xcol].min(), d[xcol].max(), 50)
    ax.plot(xs, fit["intercept"] + fit["slope"] * xs, color="0.15", lw=1.4)
    ax.text(0.97, 0.05, f"{format_eq(fit)}\n$R^2$ = {fit['r2']:.3f}\n{format_p(fit['p'])}",
            transform=ax.transAxes, ha="right", va="bottom")
    ax.legend(handles=h, title=title, loc="upper left", markerscale=0.7)
    ax.grid(True, color="0.93")
    if invert_y:
        ax.invert_yaxis()
    return fit


def fig6(df=None):
    df = regression_frame() if df is None else df
    if df["recovery"].isna().all():
        print("  Fig. 6 omitida: faltan data/raw/recovery_species.csv y recovery_accessions.csv")
        return None
    fig, ax = plt.subplots(figsize=(10, 6.3))
    groups = ["V. faba", "L. albus", "L. angustifolius", "P. sativum", "L. mutabilis",
              "L. luteus (C98)", "L. luteus (C102)", "L. luteus (C226)", "L. luteus (C195)"]
    _reg_panel(ax, df, "LT50", "recovery", groups, "Species / Accession")
    ax.invert_xaxis()
    ax.set_xlabel(r"LT$_{50}$ (°C)")
    ax.set_ylabel("Fv/Fm Recovery (%)")
    return save(fig, "Fig6_recovery_LT50")


def _sugar_fig(df, ycol, ylabel, name, invert_y):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    _reg_panel(axes[0], df, "total", ycol, ACCESSIONS, "Accession", invert_y)
    _reg_panel(axes[1], df, "total", ycol, SPECIES_SUBSET, "Species", invert_y)
    for ax, lab in zip(axes, "AB"):
        ax.set_xlabel(r"Total Sugars (mg g$^{-1}$ dry weight)")
        ax.set_ylabel(ylabel)
        panel_label(ax, f"{lab})", -0.1)
    fig.tight_layout()
    return save(fig, name)


def fig7(df=None):
    df = regression_frame() if df is None else df
    if df["recovery"].isna().all():
        print("  Fig. 7 omitida: faltan los archivos de recuperación")
        return None
    return _sugar_fig(df, "recovery", "Fv/Fm Recovery (%)", "Fig7_sugars_recovery", False)


def fig8(df=None):
    df = regression_frame() if df is None else df
    return _sugar_fig(df, "LT50", r"LT$_{50}$ (°C)", "Fig8_sugars_LT50", True)
