"""Tabla S1, PERMANOVA, regresiones y control de calidad de los datos."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import load
from .config import ACCESSIONS, ALL_ENTRIES, SPECIES, SPECIES_SUBSET, TAB_DIR
from .stats import (anova_oneway, compact_letters, ols, permanova,
                    permanova_pairwise, tukey)

VARS = ["FP", "INT", "LT10", "LT50", "LT90", "damage"]

# Valores publicados en la Tabla S1 (media, SE) para comparar
PUBLISHED = {
    "species": {
        "V. faba": [(-3.89, .12), (-5.12, .14), (-3.20, .15), (-10.74, .08), (-18.00, .14), (54.78, 5.48)],
        "L. mutabilis": [(-1.68, .08), (-5.09, .15), (5.41, .44), (-0.52, .02), (-5.75, .18), (97.72, .16)],
        "L. albus": [(-3.44, .19), (-6.01, .16), (-2.65, .26), (-6.76, .12), (-12.14, .86), (34.92, 2.05)],
        "L. angustifolius": [(-4.20, .11), (-5.78, .16), (-1.50, .20), (-6.93, .25), (-12.22, .48), (82.02, 1.50)],
        "P. sativum": [(-2.40, .04), (-4.59, .10), (4.03, .98), (-4.89, .07), (-13.70, .91), (37.28, 2.75)],
        "L. luteus": [(-3.44, .15), (-8.83, .09), (-1.43, .26), (-5.01, .09), (-9.06, .58), (53.10, 1.31)],
    },
    "accessions": {
        "L. luteus (C102)": [(-4.74, .28), (-10.21, .20), (-2.97, .13), (-6.21, .06), (-9.31, .12), (7.44, .76)],
        "L. luteus (C98)": [(-2.41, .06), (-8.15, .15), (-2.27, .23), (-6.06, .20), (-10.70, .91), (16.31, .82)],
        "L. luteus (C226)": [(-3.82, .22), (-8.79, .21), (-1.08, .46), (-4.30, .12), (-9.20, .83), (92.39, .71)],
        "L. luteus (C195)": [(-2.78, .15), (-8.17, .26), (0.89, .39), (-3.45, .14), (-7.91, .75), (93.53, .23)],
    },
}
PUBLISHED_F = {
    "species": [18.7, 124.9, 60.5, 712.6, 36.6, 82.0],
    "accessions": [28.8, 21.8, 27.3, 94.5, 2.6, 4915],
}


def supp_table1_data(level: str) -> pd.DataFrame:
    """Tabla larga group / variable / valor con las fuentes de la Tabla S1."""
    lt, _ = load.load_lt_int(level)
    fp = load.load_fp()
    dmg = load.load_damage(level)
    if level == "species":
        fp = fp.copy()
        # FP de L. luteus = las cuatro accesiones juntas (60 hojas)
        fp.loc[fp.group.isin(ACCESSIONS), "group"] = "L. luteus"
        fp = fp[fp.group.isin(SPECIES)]
        dmg = load.plants_only(dmg)          # daño medido por planta: n = 5
    else:
        fp = fp[fp.group.isin(ACCESSIONS)]
    parts = [fp.melt(id_vars="group", value_vars=["FP"]),
             lt.melt(id_vars="group", value_vars=["INT", "LT10", "LT50", "LT90"]),
             dmg.melt(id_vars="group", value_vars=["damage"])]
    return pd.concat(parts).dropna(subset=["value"])


def supp_table1(level: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    long = supp_table1_data(level)
    groups = list(PUBLISHED[level])
    out = pd.DataFrame(index=groups)
    rows = []
    for j, v in enumerate(VARS):
        d = long[long.variable == v].rename(columns={"value": v})
        f, p = anova_oneway(d, v)
        means = d.groupby("group")[v].mean()
        ses = d.groupby("group")[v].sem()
        ns = d.groupby("group")[v].count()
        letters = compact_letters(means, tukey(d, v)) if p < 0.05 else {g: "" for g in groups}
        for g in groups:
            out.loc[g, v] = f"{means[g]:.2f} ± {ses[g]:.2f} {letters[g]}".strip()
            pm, pse = PUBLISHED[level][g][j]
            rows.append({"group": g, "variable": v, "n": int(ns[g]),
                         "mean": round(means[g], 2), "se": round(ses[g], 2),
                         "letters": letters[g], "published_mean": pm,
                         "published_se": pse,
                         "matches": abs(round(means[g], 2) - pm) < 0.011
                         and abs(round(ses[g], 2) - pse) < 0.011})
        ptxt = "<0.001" if p < 0.001 else f"{p:.3f}"
        out.loc["ANOVA F (P)", v] = f"{f:.1f} ({ptxt})"
        rows.append({"group": "ANOVA F", "variable": v, "mean": round(f, 1),
                     "se": p, "published_mean": PUBLISHED_F[level][j],
                     "matches": abs(round(f, 1) - PUBLISHED_F[level][j]) <= max(0.051, 0.001 * PUBLISHED_F[level][j])})
    out.columns = ["FP (°C)", "INT (°C)", "LT10 (°C)", "LT50 (°C)", "LT90 (°C)", "Damage (%)"]
    return out, pd.DataFrame(rows)


def permanova_tables(n_perm: int = 9999):
    res = []
    pairs = []
    for level, groups in (("species", SPECIES), ("accessions", ACCESSIONS)):
        df, _ = load.load_lt_int(level)
        X = df[["LT50", "INT"]].values
        r = permanova(X, df["group"].values, n_perm)
        res.append({"level": level, **r})
        pw = permanova_pairwise(X, df["group"].values, n_perm)
        pw.insert(0, "level", level)
        pairs.append(pw)
    return pd.DataFrame(res), pd.concat(pairs)


def regression_table(df: pd.DataFrame) -> pd.DataFrame:
    """Las regresiones del manuscrito (Tabla 1, Figs. 6-8)."""
    published = {
        ("recovery ~ LT50", "all entries"): (-4.39, 47.8, 0.618),
        ("recovery ~ total sugars", "L. luteus accessions"): (6.68, 19.8, 0.574),
        ("LT50 ~ total sugars", "L. luteus accessions"): (-0.56, -0.9, 0.433),
        ("recovery ~ total sugars", "four-species subset"): (2.69, 26.0, 0.649),
        ("LT50 ~ total sugars", "four-species subset"): (-0.57, 4.3, 0.636),
        ("recovery ~ total sugars", "all entries"): (np.nan, np.nan, 0.264),
        ("LT50 ~ total sugars", "all entries"): (np.nan, np.nan, 0.246),
    }
    sets = {"all entries": ALL_ENTRIES, "L. luteus accessions": ACCESSIONS,
            "four-species subset": SPECIES_SUBSET}
    rows = []
    for (model, subset), (b, a, r2) in published.items():
        y, x = [s.strip() for s in model.split("~")]
        xcol = {"LT50": "LT50", "total sugars": "total"}[x]
        d = df[df.group.isin(sets[subset])].dropna(subset=[xcol, y])
        row = {"model": model, "subset": subset, "n": len(d),
               "published_slope": b, "published_intercept": a, "published_R2": r2}
        if len(d) > 2:
            f = ols(d[xcol], d[y])
            row.update(slope=round(f["slope"], 3), intercept=round(f["intercept"], 2),
                       R2=round(f["r2"], 3), p=f["p"])
        else:
            row.update(slope=np.nan, intercept=np.nan, R2=np.nan, p=np.nan,
                       note="faltan datos de recuperación")
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
def quality_report() -> pd.DataFrame:
    """Bloques de hojas repetidos dentro de cada grupo.

    Para cada grupo de 15 filas compara el bloque de filas 11-15 con los
    bloques 1-5 y 6-10 en las columnas medidas por hoja. Un bloque idéntico
    indica que esas cinco filas son copia de otras y no hojas independientes.
    """
    checks = [
        ("FP.csv", load.load_fp(), ["FP"]),
        ("LT_INT_species.csv", load.load_lt_int("species")[0], ["LT50", "INT"]),
        ("LT_INT_accessions.csv", load.load_lt_int("accessions")[0], ["LT50", "INT"]),
        ("LT50_Damage_species.csv", load.load_damage("species"), ["LT50"]),
        ("LT50_Damage_accessions.csv", load.load_damage("accessions"), ["damage"]),
    ]
    rows = []
    for fname, df, cols in checks:
        for g, d in df.groupby("group", sort=False):
            v = d.sort_values("leaf")[cols].round(4).values
            b1, b2, b3 = v[0:5], v[5:10], v[10:15]
            rows.append({"file": fname, "group": g, "columns": "+".join(cols),
                         "rows": len(d),
                         "rows_11_15_equal_rows_6_10": bool(np.array_equal(b3, b2)),
                         "rows_11_15_equal_rows_1_5": bool(np.array_equal(b3, b1)),
                         "rows_6_10_equal_rows_1_5": bool(np.array_equal(b2, b1))})
    out = pd.DataFrame(rows)
    out["any_repeated_block"] = out.filter(like="equal").any(axis=1)
    return out


def sugar_total_check() -> pd.DataFrame:
    """Filas de Data_frio_maca_ll.csv donde 'Total Sugar' no es la suma de los
    cinco azúcares de la misma fila."""
    m = load.load_master()
    bad = m[(m["total"] - m["sugar_sum"]).abs() > 0.02]
    return bad[["group", "leaf_id", "total", "sugar_sum"] + ["fructose", "glucose",
               "sucrose", "raffinose", "stachyose"]]


def save_table(df: pd.DataFrame, name: str, index=False):
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    p = TAB_DIR / f"{name}.csv"
    df.to_csv(p, index=index, encoding="utf-8-sig")
    return p
