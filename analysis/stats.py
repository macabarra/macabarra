"""Pruebas estadísticas: ANOVA de una vía + Tukey HSD con letras, Welch, OLS y
PERMANOVA."""
from __future__ import annotations

import string
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

ALPHA = 0.05


# ---------------------------------------------------------------------------
def anova_oneway(df: pd.DataFrame, value: str, group: str = "group"):
    d = df[[group, value]].dropna()
    samples = [g[value].values for _, g in d.groupby(group, sort=False)]
    f, p = stats.f_oneway(*samples)
    return float(f), float(p)


def tukey(df: pd.DataFrame, value: str, group: str = "group") -> pd.DataFrame:
    d = df[[group, value]].dropna()
    res = pairwise_tukeyhsd(d[value].values, d[group].values, alpha=ALPHA)
    t = pd.DataFrame(res._results_table.data[1:], columns=res._results_table.data[0])
    return t


def compact_letters(means: pd.Series, tukey_table: pd.DataFrame) -> dict[str, str]:
    """Letras de agrupamiento (algoritmo insertar-y-absorber).

    La letra 'a' corresponde al grupo de media más baja, como en la Tabla S1.
    """
    groups = list(means.sort_values().index)
    cols = [set(groups)]
    for _, r in tukey_table.iterrows():
        if not bool(r["reject"]):
            continue
        a, b = r["group1"], r["group2"]
        new = []
        for c in cols:
            if a in c and b in c:
                new += [c - {a}, c - {b}]
            else:
                new.append(c)
        # quitar duplicados y absorber columnas contenidas en otra
        uniq = []
        for c in new:
            if c not in uniq:
                uniq.append(c)
        cols = [c for c in uniq if not any(c < o for o in uniq)]
    rank = {g: i for i, g in enumerate(groups)}
    cols.sort(key=lambda c: min(rank[g] for g in c))
    letters = {g: "" for g in groups}
    for letter, c in zip(string.ascii_lowercase, cols):
        for g in c:
            letters[g] += letter
    return letters


def welch(a, b):
    t, p = stats.ttest_ind(np.asarray(a, float), np.asarray(b, float), equal_var=False)
    return float(t), float(p)


def stars(p: float) -> str:
    if p is None or np.isnan(p):
        return "n.s."
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def ols(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    r = stats.linregress(x, y)
    return {"slope": r.slope, "intercept": r.intercept, "r2": r.rvalue ** 2,
            "p": r.pvalue, "n": len(x)}


def format_eq(fit: dict, xname: str = "x") -> str:
    sign = "+" if fit["intercept"] >= 0 else "−"
    return f"y = {fit['slope']:.2f}{xname} {sign} {abs(fit['intercept']):.1f}".replace("-", "−")


def format_p(p: float) -> str:
    return "P < 0.001" if p < 0.001 else f"P = {p:.3f}"


# ---------------------------------------------------------------------------
def permanova(X: np.ndarray, labels, n_perm: int = 9999, seed: int = 1) -> dict:
    """PERMANOVA de una vía (Anderson 2001) con distancia euclidiana.

    X: matriz n × p (aquí LT50 e INT, ambos en °C, sin estandarizar).
    """
    X = np.asarray(X, float)
    labels = np.asarray(labels)
    n = len(labels)
    D2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    groups = np.unique(labels)
    a = len(groups)

    def pseudo_f(lab):
        ss_t = D2[np.triu_indices(n, 1)].sum() / n
        ss_w = 0.0
        for g in groups:
            idx = np.where(lab == g)[0]
            sub = D2[np.ix_(idx, idx)]
            ss_w += sub[np.triu_indices(len(idx), 1)].sum() / len(idx)
        ss_a = ss_t - ss_w
        return (ss_a / (a - 1)) / (ss_w / (n - a)), ss_a / ss_t

    f_obs, r2 = pseudo_f(labels)
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        f_p, _ = pseudo_f(rng.permutation(labels))
        count += f_p >= f_obs
    return {"pseudo_F": f_obs, "R2": r2, "p": (count + 1) / (n_perm + 1),
            "n": n, "groups": a, "permutations": n_perm}


def permanova_pairwise(X, labels, n_perm: int = 9999, seed: int = 1) -> pd.DataFrame:
    labels = np.asarray(labels)
    rows = []
    for g1, g2 in combinations(pd.unique(labels), 2):
        m = np.isin(labels, [g1, g2])
        r = permanova(np.asarray(X)[m], labels[m], n_perm, seed)
        rows.append({"group1": g1, "group2": g2, **r})
    out = pd.DataFrame(rows)
    # corrección de Bonferroni
    out["p_bonferroni"] = np.minimum(out["p"] * len(out), 1.0)
    return out
