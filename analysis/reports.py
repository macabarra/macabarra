"""Genera un .md por figura y por análisis, y un .txt con los datos usados en cada uno.

Salidas:
    outputs/docs/figures/<Figura>.md
    outputs/docs/analyses/<Análisis>.md
    outputs/data_txt/<Figura o análisis>_data.txt   (tabulado, punto decimal)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import load, tables
from .config import ACCESSIONS, ALL_ENTRIES, OUT, SPECIES, SPECIES_SUBSET
from .figures import FIG5_ORDER, SUGAR_PANELS, regression_frame, sugar_contrasts
from .stats import ols

DOC_FIG = OUT / "docs" / "figures"
DOC_AN = OUT / "docs" / "analyses"
TXT = OUT / "data_txt"


# ---------------------------------------------------------------------------
def md_table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else floatfmt.format(v)
        return str(v).replace("*", "\\*")
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |",
             "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(fmt(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_txt(df: pd.DataFrame, name: str, header: str) -> str:
    TXT.mkdir(parents=True, exist_ok=True)
    path = TXT / f"{name}_data.txt"
    with open(path, "w", encoding="utf-8") as f:
        for line in header.strip().splitlines():
            f.write(f"# {line}\n")
        df.to_csv(f, sep="\t", index=False, float_format="%.6g", lineterminator="\n")
    return path.name


def write_md(folder, name: str, text: str):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.md").write_text(text.strip() + "\n", encoding="utf-8")


def mean_se(df, group_col, cols, order):
    rows = []
    for g in order:
        d = df[df[group_col] == g]
        row = {"Grupo": g, "n": int(d[cols[0]].notna().sum())}
        for c in cols:
            row[c] = f"{d[c].mean():.2f} ± {d[c].sem():.2f}"
        rows.append(row)
    return pd.DataFrame(rows)


def fit_line(fit) -> str:
    sign = "+" if fit["intercept"] >= 0 else "−"
    p = "P < 0,001" if fit["p"] < 0.001 else f"P = {fit['p']:.3f}"
    return (f"y = {fit['slope']:.2f}x {sign} {abs(fit['intercept']):.2f}; "
            f"R² = {fit['r2']:.3f}; {p}; n = {fit['n']}").replace(".", ",")


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def doc_supp_fig1():
    d = load.load_chamber()
    txt = write_txt(d[["time", "hour", "temp", "light"]], "FigS1",
                    "Programa de la cámara de congelación (Chamber_program.csv).\n"
                    "time: hora; hour: hora decimal; temp: °C; light: columna 'Luz' (0 = sin luz).")
    seg = (d["temp"] != d["temp"].shift()).cumsum()
    steps = d.groupby(seg).agg(Inicio=("time", "first"), Fin_h=("hour", "last"),
                               Temperatura=("temp", "first")).reset_index(drop=True)
    steps["Fin"] = (steps["Fin_h"] + 5 / 60).map(lambda h: f"{int(h):02d}:{round(h % 1 * 60):02d}")
    steps["Duración (h)"] = (steps["Fin_h"] + 5 / 60 - d.groupby(seg)["hour"].first().values).round(2)
    steps["Inicio"] = steps["Inicio"].map(lambda t: f"{int(t.split(':')[0]):02d}:{t.split(':')[1]}")
    steps = steps[["Inicio", "Fin", "Temperatura", "Duración (h)"]]
    steps.columns = ["Inicio", "Fin", "Temperatura (°C)", "Duración (h)"]
    light = d[d["light"] > 0]
    low = d[d["temp"] == d["temp"].min()]
    write_md(DOC_FIG, "FigS1_chamber_program", f"""
# Figura S1. Programa de temperatura de la cámara

Archivos: `outputs/figures/FigS1_chamber_program.tif` y `.png`.
Datos: `outputs/data_txt/{txt}` (de `data/raw/Chamber_program.csv`, registro cada 5 min).

## Qué muestra

Temperatura programada en la cámara durante el ciclo de 24 h del ensayo de helada con plantas
enteras. La línea escalonada es la temperatura; el sombreado gris marca los registros con
`Luz = 0`.

## Escalones del programa

{md_table(steps)}

Mínimo: {d.temp.min():.0f} °C. Máximo: {d.temp.max():.0f} °C.
Luz encendida (`Luz > 0`): de {light.time.iloc[0]} a {light.time.iloc[-1]}
({len(light) * 5 / 60:.1f} h).

## Diferencias con la leyenda del material suplementario

La leyenda describe oscuridad de 00:00 a 08:00, fotoperiodo 16 h luz / 8 h oscuridad y unas
2,5 h a −6 °C. El archivo indica luz solo entre {light.time.iloc[0]} y {light.time.iloc[-1]} y
−6 °C entre las {low.time.iloc[0][:-3]} y las 08:05 ({len(low) * 5 / 60:.2f} h). La figura publicada tiene además escalones en horas distintas. Hay
que confirmar cuál fue el programa aplicado.
""")


def doc_supp_fig2():
    sp, n1 = load.load_lt_int("species")
    ac, n2 = load.load_lt_int("accessions")
    both = pd.concat([sp.assign(level="species"), ac.assign(level="accessions")])
    txt = write_txt(both[["level", "group", "leaf", "LT10", "LT50", "LT90", "INT"]], "FigS2",
                    "LT10, LT50, LT90 e INT por hoja (LT_INT_species.csv, LT_INT_accessions.csv).\n"
                    "LT10/LT90 vacíos = tratados como faltantes (ver limpieza en QC).")
    order_sp = list(sp.groupby("group")["LT50"].mean().sort_values(ascending=False).index)
    order_ac = ["L. luteus (C98)", "L. luteus (C195)", "L. luteus (C102)", "L. luteus (C226)"]
    cols = ["LT10", "LT50", "LT90", "INT"]
    write_md(DOC_FIG, "FigS2_PSII_thresholds_INT", f"""
# Figura S2. Umbrales de daño del PSII e INT

Archivos: `outputs/figures/FigS2_PSII_thresholds_INT.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Para cada grupo, la caja va de la media de LT₁₀ a la media de LT₉₀; la línea horizontal es la
media de LT₅₀ y el punto negro la media de INT. Las barras de error son el SE de LT₁₀ y de LT₉₀.
Panel A: especies, ordenadas por LT₅₀ de mayor a menor. Panel B: accesiones de *L. luteus*.
LT₁₀ sobre −1 °C y LT₉₀ bajo −12 °C son extrapolaciones de la regresión de cada hoja.

## Valores (media ± SE, °C)

Panel A, especies:

{md_table(mean_se(sp, "group", cols, order_sp))}

Panel B, accesiones:

{md_table(mean_se(ac, "group", cols, order_ac))}

La columna n corresponde a LT₁₀; LT₅₀ e INT tienen 15 hojas en todos los grupos.

## Limpieza

{chr(10).join("- " + n for n in n1 + n2)}
""")


def _lt_int_doc(level, name, title, order):
    df, _ = load.load_lt_int(level)
    txt = write_txt(df[["group", "leaf", "LT50", "INT"]], name,
                    f"LT50 e INT por hoja (LT_INT_{level}.csv).")
    m = df.groupby("group")[["LT50", "INT"]].agg(["mean", "sem"])
    rows = []
    for g in order:
        lt, it = m.loc[g, ("LT50", "mean")], m.loc[g, ("INT", "mean")]
        rows.append({"Grupo": g,
                     "LT50 (°C)": f"{lt:.2f} ± {m.loc[g, ('LT50', 'sem')]:.2f}",
                     "INT (°C)": f"{it:.2f} ± {m.loc[g, ('INT', 'sem')]:.2f}",
                     "INT − LT50 (°C)": round(it - lt, 2),
                     "Posición": "sobre la diagonal (daño antes de nuclear)" if it < lt
                     else "bajo la diagonal (daño después de nuclear)"})
    return txt, pd.DataFrame(rows)


def doc_fig2():
    txt, tab = _lt_int_doc("species", "Fig2", "", SPECIES)
    vf = tab.set_index("Grupo").loc["V. faba", "INT − LT50 (°C)"]
    write_md(DOC_FIG, "Fig2_LT50_INT_species", f"""
# Figura 2. LT₅₀ frente a INT en especies

Archivos: `outputs/figures/Fig2_LT50_INT_species.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Cada punto pequeño es una hoja (15 por especie); el rombo grande es la media del grupo y la
elipse abarca dos desviaciones estándar de la covarianza de LT₅₀ e INT. Ambos ejes están
invertidos. La diagonal discontinua es LT₅₀ = INT. Sobre la diagonal (INT más negativa que
LT₅₀) el PSII se daña antes de que nuclee el hielo; bajo la diagonal se daña después.

Flechas: en *L. luteus* y *L. mutabilis* van desde la INT media hasta la diagonal a la altura
de su LT₅₀; en *V. faba* va desde la diagonal hasta su LT₅₀, a la altura de su INT, con la
etiqueta "{vf:.1f} °C resistant" (INT − LT₅₀ = {vf:.2f} °C).

## Valores (media ± SE)

{md_table(tab)}

PERMANOVA sobre (LT₅₀, INT): ver `outputs/docs/analyses/PERMANOVA_LT50_INT.md`.
""")


def doc_fig3():
    txt, tab = _lt_int_doc("accessions", "Fig3", "", ACCESSIONS)
    write_md(DOC_FIG, "Fig3_LT50_INT_accessions", f"""
# Figura 3. LT₅₀ frente a INT en accesiones de *L. luteus*

Archivos: `outputs/figures/Fig3_LT50_INT_accessions.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Igual que la Figura 2, para C102, C195, C226 y C98, con un marcador por accesión. Ejes de 0 a
−14 °C, invertidos; diagonal LT₅₀ = INT.

## Valores (media ± SE)

{md_table(tab)}

Las cuatro accesiones quedan sobre la diagonal: el PSII se daña a temperaturas más altas que
la INT medida en el ensayo térmico.
""")


def doc_fig4():
    sp = load.load_damage("species")
    ac = load.load_damage("accessions")
    both = pd.concat([sp.assign(panel="B"), ac.assign(panel="D")])
    txt = write_txt(both[["panel", "group", "leaf", "plant", "LT50", "damage"]], "Fig4BD",
                    "Panel B: LT50_Damage_species.csv (daño medido por planta, repetido en sus 3 hojas).\n"
                    "Panel D: LT50_Damage_accessions.csv (daño por hoja).\n"
                    "damage = % de área foliar dañada 14 días después de la helada a −6 °C.")
    order_b = ["V. faba", "L. albus", "L. angustifolius", "P. sativum", "L. luteus", "L. mutabilis"]
    order_d = ["L. luteus (C98)", "L. luteus (C102)", "L. luteus (C226)", "L. luteus (C195)"]
    tb = mean_se(load.plants_only(sp), "group", ["damage"], order_b).rename(columns={"damage": "Daño (%)"})
    tb["LT50 (°C)"] = [f"{sp[sp.group == g].LT50.mean():.2f} ± {sp[sp.group == g].LT50.sem():.2f}" for g in order_b]
    td = mean_se(ac, "group", ["damage", "LT50"], order_d).rename(columns={"damage": "Daño (%)", "LT50": "LT50 (°C)"})
    write_md(DOC_FIG, "Fig4BD_LT50_damage", f"""
# Figura 4 (paneles B y D). LT₅₀ frente a daño visible

Archivos: `outputs/figures/Fig4BD_LT50_damage.tif` y `.png`. Los paneles A y C son fotografías
y no se generan con este código.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Eje X: daño visible (%) 14 días después de la helada a −6 °C en plantas enteras. Eje Y: LT₅₀
de hojas cortadas, invertido. Puntos pequeños = observaciones, punto grande = media, elipse =
2 DE. La línea discontinua es una referencia visual copiada de la figura original (de
(0, −12) a (100, 0) en B; de (0, −8) a (100, 0) en D); no es un ajuste.

## Valores (media ± SE)

Panel B, especies (daño con n = 5 plantas; LT₅₀ con las 15 filas del archivo):

{md_table(tb)}

Panel D, accesiones (n = 15 hojas):

{md_table(td)}

La LT₅₀ de especies de este archivo no es la de `LT_INT_species.csv` (Tabla S1, Fig. 2). Para
*L. albus* da −6,43 °C frente a −6,76 °C.
""")


def doc_fig5():
    res = sugar_contrasts()
    d = load.load_sugars_treatments()
    txt = write_txt(d[["group", "treatment", "plant"] + [s for s, _ in SUGAR_PANELS]], "Fig5",
                    "Azúcares solubles de hoja (mg g-1 peso seco), una fila por planta.\n"
                    "Fuente: sugars_control_freezing.tsv, columnas A*. total = suma de los cinco azúcares.\n"
                    "Corrección aplicada: L. luteus (C102), planta 3 (plant = 2), control, sacarosa 4.64 -> 2.64.")
    blocks = []
    for s, label in SUGAR_PANELS:
        r = res[res.sugar == s].set_index("group").loc[FIG5_ORDER].reset_index()
        t = pd.DataFrame({
            "Grupo": r["group"],
            "Control": [f"{a:.2f} ± {b:.2f}" for a, b in zip(r.control_mean, r.control_se)],
            "Congelación": [f"{a:.2f} ± {b:.2f}" for a, b in zip(r.freezing_mean, r.freezing_se)],
            "t de Welch": r["welch_t"].round(2),
            "P": r["p"].map(lambda p: "" if np.isnan(p) else ("< 0,001" if p < 0.001 else f"{p:.3f}")),
            "Signif.": r["signif"],
        })
        blocks.append(f"### {label}\n\n{md_table(t)}")
    write_md(DOC_FIG, "Fig5_soluble_sugars", f"""
# Figura 5. Azúcares solubles de hoja, control frente a congelación

Archivos: `outputs/figures/Fig5_soluble_sugars.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.
Tabla completa: `outputs/tables/Sugars_Welch.csv`.

## Qué muestra

Seis paneles: (A) fructosa, (B) rafinosa, (C) glucosa, (D) sacarosa, (E) estaquiosa y (F)
azúcar total, en mg g⁻¹ de peso seco. Barra lisa = control (antes de la helada); barra con
trama = congelación (10 h después de la helada). Media ± SE, n = 5 plantas. La línea
horizontal separa las especies de las accesiones de *L. luteus*.

Prueba: t de Welch control frente a congelación en cada grupo y azúcar.
\\* P < 0,05; \\*\\* P < 0,01; \\*\\*\\* P < 0,001; n.s. no significativo. Cuando ambos tratamientos
tienen varianza cero (estaquiosa en *L. mutabilis*) no se calcula la prueba y se marca n.s.

## Valores (media ± SE, mg g⁻¹)

{chr(10).join(blocks)}

## Corrección

C102, planta 3, control: sacarosa 2,64 mg g⁻¹ (los archivos traen 4,64). Con esto la media
control de C102 es 3,40 en sacarosa y 7,49 en total; ambos contrastes siguen n.s.
""")


def _reg_txt(name, groups, cols, extra=""):
    df = regression_frame()
    d = df[df.group.isin(groups)][["group", "leaf_id", "plant"] + cols]
    return write_txt(d, name,
                     "Una fila por hoja. Fuente: Data_frio_maca_ll.csv.\n"
                     "recovery = 100 × Fv/Fm después / Fv/Fm antes (10 h a 15 °C en oscuridad).\n"
                     "total = azúcares solubles totales antes de la helada (mg g-1), valor de la planta.\n"
                     + extra)


def _group_means(df, groups, cols):
    rows = []
    for g in groups:
        d = df[df.group == g]
        row = {"Grupo": g, "n": len(d)}
        for c, lab in cols:
            row[lab] = f"{d[c].mean():.2f} ± {d[c].sem():.2f}"
        rows.append(row)
    return pd.DataFrame(rows)


def doc_fig6():
    df = regression_frame()
    groups = ["V. faba", "L. albus", "L. angustifolius", "P. sativum", "L. mutabilis",
              "L. luteus (C98)", "L. luteus (C102)", "L. luteus (C226)", "L. luteus (C195)"]
    txt = _reg_txt("Fig6", groups, ["LT50", "fvfm_before", "fvfm_after", "recovery"])
    fit = ols(df.LT50, df.recovery)
    write_md(DOC_FIG, "Fig6_recovery_LT50", f"""
# Figura 6. Recuperación fotoquímica frente a LT₅₀

Archivos: `outputs/figures/Fig6_recovery_LT50.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Recuperación de Fv/Fm en plantas enteras (%) frente a la LT₅₀ de hojas cortadas, para las 9
entradas (5 especies y 4 accesiones de *L. luteus*; 15 hojas cada una, n = 135). Eje X
invertido. Puntos pequeños = hojas, marcador grande = media, elipse = 2 DE. La recta es la
regresión de mínimos cuadrados sobre las 135 hojas.

## Regresión

{fit_line(fit)}

## Medias por grupo (± SE)

{md_table(_group_means(df, groups, [("LT50", "LT50 (°C)"), ("recovery", "Recuperación (%)")]))}

Las hojas de una planta no son independientes; el P está calculado con n = 135 y puede estar
subestimado (lo reconoce la Discusión del manuscrito).
""")


def _sugar_doc(name, ycol, ylab, fig_title, extra_note=""):
    df = regression_frame()
    txt = _reg_txt(name.split("_")[0], ACCESSIONS + SPECIES_SUBSET, ["total", ycol])
    fa = ols(*[df[df.group.isin(ACCESSIONS)][c] for c in ("total", ycol)])
    fb = ols(*[df[df.group.isin(SPECIES_SUBSET)][c] for c in ("total", ycol)])
    fall = ols(*[df[df.group.isin(ALL_ENTRIES)][c] for c in ("total", ycol)])
    cols = [("total", "Azúcar total (mg g⁻¹)"), (ycol, ylab)]
    write_md(DOC_FIG, name, f"""
# {fig_title}

Archivos: `outputs/figures/{name}.tif` y `.png`.
Datos: `outputs/data_txt/{txt}`.

## Qué muestra

Panel A: accesiones de *L. luteus* (C102, C195, C226, C98; n = 60 hojas). Panel B:
subconjunto de cuatro especies (*L. albus*, *L. mutabilis*, *P. sativum*, *V. faba*; n = 60).
Puntos pequeños = hojas; marcador grande = media; elipse = 2 DE. Los azúcares se midieron por
planta antes de la helada, de modo que las tres hojas de una planta comparten el valor de X.
La recta es la regresión de mínimos cuadrados de cada panel. {extra_note}

## Regresiones

- Panel A: {fit_line(fa)}
- Panel B: {fit_line(fb)}
- Las 9 entradas juntas (sin figura): {fit_line(fall)}

## Medias por grupo (± SE)

Panel A:

{md_table(_group_means(df, ACCESSIONS, cols))}

Panel B:

{md_table(_group_means(df, SPECIES_SUBSET, cols))}

*L. luteus* (especie) y *L. angustifolius* no entran en el panel B; el criterio está en
Métodos y el análisis se presenta como exploratorio.
""")


def doc_fig7():
    _sugar_doc("Fig7_sugars_recovery", "recovery", "Recuperación (%)",
               "Figura 7. Azúcares solubles totales frente a recuperación fotoquímica")


def doc_fig8():
    _sugar_doc("Fig8_sugars_LT50", "LT50", "LT50 (°C)",
               "Figura 8. Azúcares solubles totales frente a LT₅₀",
               "El eje Y está invertido: LT₅₀ más negativa (más resistente) aparece arriba.")


# ---------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------
def doc_table_s1():
    parts = []
    for level in ("species", "accessions"):
        long = tables.supp_table1_data(level)
        long.insert(0, "level", level)
        parts.append(long)
    txt = write_txt(pd.concat(parts), "TableS1",
                    "Datos de la Tabla S1 en formato largo: level / group / variable / value.\n"
                    "FP de L. luteus (especie) = las 60 hojas de las cuatro accesiones.\n"
                    "Daño de especies: una fila por planta (n = 5). Resto: una fila por hoja.")
    out = []
    for level, title in (("species", "Especies"), ("accessions", "Accesiones de *L. luteus*")):
        wide, check = tables.supp_table1(level)
        w = wide.reset_index().rename(columns={"index": "Grupo"})
        ok = int(check["matches"].sum()), len(check)
        out.append(f"## {title}\n\n{md_table(w)}\n\nCoincidencia con la Tabla S1 publicada: "
                   f"{ok[0]} de {ok[1]} valores (medias, SE y F).")
    write_md(DOC_AN, "TableS1_ANOVA_Tukey", f"""
# Tabla S1. Parámetros de resistencia a la congelación: ANOVA de una vía y Tukey HSD

Datos: `outputs/data_txt/{txt}`.
Tablas: `outputs/tables/TableS1_species.csv`, `TableS1_accessions.csv` y los archivos
`*_vs_published.csv` con la comparación celda por celda.

## Método

Para cada variable (FP, INT, LT₁₀, LT₅₀, LT₉₀, daño) se hizo un ANOVA de una vía entre grupos
(`scipy.stats.f_oneway`). Si P < 0,05 se aplicó Tukey HSD (`statsmodels`, α = 0,05) y se
asignaron letras con el algoritmo de insertar y absorber; la letra "a" corresponde a la media
más baja. Si el ANOVA no es significativo no se ponen letras. Valores: media ± SE.

Fuentes: FP de `FP.csv`; INT y LT de `LT_INT_species.csv` y `LT_INT_accessions.csv`; daño de
`LT50_Damage_species.csv` (n = 5 plantas) y `LT50_Damage_accessions.csv` (n = 15 hojas).
LT₁₀ y LT₉₀ de dos filas se tratan como faltantes (ver `QC_data_checks.md`).

{chr(10).join(out)}
""")


def doc_permanova(n_perm):
    parts = []
    for level in ("species", "accessions"):
        df, _ = load.load_lt_int(level)
        parts.append(df[["group", "leaf", "LT50", "INT"]].assign(level=level))
    txt = write_txt(pd.concat(parts)[["level", "group", "leaf", "LT50", "INT"]], "PERMANOVA",
                    "LT50 e INT por hoja usados en la PERMANOVA (LT_INT_species.csv, LT_INT_accessions.csv).")
    glob, pairs = tables.permanova_tables(n_perm)
    g = glob[["level", "pseudo_F", "R2", "p", "n", "groups", "permutations"]].copy()
    g.columns = ["Nivel", "pseudo-F", "R²", "P", "n", "Grupos", "Permutaciones"]
    p = pairs[["level", "group1", "group2", "pseudo_F", "R2", "p", "p_bonferroni"]].copy()
    p.columns = ["Nivel", "Grupo 1", "Grupo 2", "pseudo-F", "R²", "P", "P Bonferroni"]
    write_md(DOC_AN, "PERMANOVA_LT50_INT", f"""
# PERMANOVA sobre LT₅₀ e INT

Datos: `outputs/data_txt/{txt}`.
Tablas: `outputs/tables/PERMANOVA_LT50_INT.csv` y `PERMANOVA_LT50_INT_pairwise.csv`.

## Método

PERMANOVA de una vía (Anderson 2001) con distancia euclidiana sobre el par (LT₅₀, INT) de cada
hoja, sin estandarizar (las dos variables están en °C). Estadístico pseudo-F; P por
{n_perm} permutaciones de las etiquetas de grupo (semilla 1). Comparaciones por pares con la
misma prueba y corrección de Bonferroni.

## Resultado global

{md_table(g, "{:.4g}")}

## Comparaciones por pares

{md_table(p, "{:.4g}")}

El P mínimo posible con {n_perm} permutaciones es {1 / (n_perm + 1):.4f}.
""")


def doc_regressions():
    df = regression_frame()
    txt = write_txt(df[["group", "leaf_id", "plant", "LT50", "total", "fvfm_before",
                        "fvfm_after", "recovery"]], "Regressions",
                    "Datos de las siete regresiones (Data_frio_maca_ll.csv), una fila por hoja.")
    rt = tables.regression_table(df)
    t = rt[["model", "subset", "n", "slope", "intercept", "R2", "p", "published_slope",
            "published_intercept", "published_R2"]].copy()
    t.columns = ["Modelo", "Subconjunto", "n", "Pendiente", "Intercepto", "R²", "P",
                 "Pend. publicada", "Int. publicado", "R² publicado"]
    write_md(DOC_AN, "Regressions_OLS", f"""
# Regresiones lineales (Tabla 1 del manuscrito; Figs. 6, 7 y 8)

Datos: `outputs/data_txt/{txt}`. Tabla: `outputs/tables/Regressions.csv`.

## Método

Mínimos cuadrados ordinarios (`scipy.stats.linregress`) con la hoja como observación. P es el
de la pendiente. Subconjuntos: todas las entradas (5 especies + 4 accesiones, n = 135),
accesiones de *L. luteus* (n = 60) y cuatro especies (*L. albus*, *L. mutabilis*,
*P. sativum*, *V. faba*; n = 60). Azúcares totales medidos antes de la helada.

## Resultados

{md_table(t, "{:.4g}")}

Las siete regresiones coinciden con los valores publicados.
""")


def doc_welch():
    res = sugar_contrasts()
    d = load.load_sugars_treatments()
    txt = write_txt(d[["group", "treatment", "plant"] + [s for s, _ in SUGAR_PANELS]], "Sugars_Welch",
                    "Azúcares de hoja por planta, control y congelación (sugars_control_freezing.tsv, columnas A*).\n"
                    "Corrección: C102 planta 3 control, sacarosa 2.64.")
    piv = res.pivot(index="group", columns="sugar", values="signif").loc[FIG5_ORDER]
    piv = piv[[s for s, _ in SUGAR_PANELS]].reset_index()
    piv.columns = ["Grupo"] + [lab for _, lab in SUGAR_PANELS]
    write_md(DOC_AN, "Sugars_Welch", f"""
# Azúcares solubles: pruebas de Welch control frente a congelación

Datos: `outputs/data_txt/{txt}`. Tabla completa (medias, SE, t, P):
`outputs/tables/Sugars_Welch.csv`. Figura: `outputs/docs/figures/Fig5_soluble_sugars.md`.

## Método

t de Welch (varianzas distintas) entre control y congelación, n = 5 plantas por tratamiento,
para cada azúcar y cada una de las 9 entradas. El total es la suma de fructosa, glucosa,
sacarosa, rafinosa y estaquiosa.

## Significancia

{md_table(piv)}

Las 54 marcas coinciden con la Figura 5 publicada.
""")


def doc_qc():
    qc = tables.quality_report()
    rep = qc[qc.any_repeated_block][["file", "group", "columns"]]
    rep.columns = ["Archivo", "Grupo", "Columnas comparadas"]
    _, n1 = load.load_lt_int("species")
    _, n2 = load.load_lt_int("accessions")
    txt = write_txt(qc, "QC", "Resultado de la revisión de bloques repetidos (filas 11-15 frente a 1-5 y 6-10).")
    write_md(DOC_AN, "QC_data_checks", f"""
# Control de calidad de los datos

Datos: `outputs/data_txt/{txt}`. Tablas: `outputs/tables/QC_repeated_blocks.csv` y
`QC_total_sugar_vs_sum.csv`.

## Limpieza aplicada

{chr(10).join("- " + n for n in n1 + n2)}

Con esta exclusión los valores de LT₁₀ y LT₉₀ coinciden con la Tabla S1 publicada.

## Corrección confirmada

- *L. luteus* (C102), planta 3, control: sacarosa 2,64 mg g⁻¹ (los archivos traen 4,64). Se
  aplica al leer los datos (`SUGAR_CORRECTIONS` en `analysis/load.py`).

## Bloques de filas repetidos

En cada grupo de 15 filas se comparó el bloque 11–15 con los bloques 1–5 y 6–10. En los
siguientes grupos las filas 11–15 son idénticas a las filas 6–10:

{md_table(rep)}

En esos grupos hay 10 valores distintos y no 15. La Tabla S1 publicada usa las 15 filas y el
código las mantiene; los SE y P calculados con n = 15 son menores que con n = 10.

## Azúcar total frente a suma de componentes

Después de la corrección, `Total Sugar` coincide con la suma de los cinco azúcares en todas las
filas de `Data_frio_maca_ll.csv`.
""")


def build_all(n_perm: int = 9999):
    for fn in (doc_supp_fig1, doc_supp_fig2, doc_fig2, doc_fig3, doc_fig4, doc_fig5,
               doc_fig6, doc_fig7, doc_fig8, doc_table_s1, doc_regressions, doc_welch,
               doc_qc):
        fn()
    doc_permanova(n_perm)
