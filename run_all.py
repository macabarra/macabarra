"""Reproduce los análisis y figuras de Barra et al. (Frontiers).

Uso:
    python run_all.py              # todo
    python run_all.py --perm 999   # PERMANOVA más rápida

Resultados en outputs/figures (PNG y TIFF a 300 dpi) y outputs/tables (CSV).
"""
import argparse

import pandas as pd

from analysis import figures, load, tables
from analysis.plotting import apply_style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=9999, help="permutaciones PERMANOVA")
    args = ap.parse_args()
    apply_style()
    pd.set_option("display.width", 200)

    print("Limpieza de datos")
    for level in ("species", "accessions"):
        for note in load.load_lt_int(level)[1]:
            print("  " + note)

    print("\nTabla S1")
    for level in ("species", "accessions"):
        wide, check = tables.supp_table1(level)
        tables.save_table(wide, f"TableS1_{level}", index=True)
        tables.save_table(check, f"TableS1_{level}_vs_published")
        print(wide.to_string())
        bad = check[~check["matches"]]
        if len(bad):
            print("  Valores que difieren de la Tabla S1 publicada:")
            print(bad.to_string(index=False))
        print()

    print("PERMANOVA (LT50, INT)")
    glob, pairs = tables.permanova_tables(args.perm)
    tables.save_table(glob, "PERMANOVA_LT50_INT")
    tables.save_table(pairs, "PERMANOVA_LT50_INT_pairwise")
    print(glob.to_string(index=False))

    print("\nRegresiones")
    reg = figures.regression_frame()
    rt = tables.regression_table(reg)
    tables.save_table(rt, "Regressions")
    print(rt.to_string(index=False))

    print("\nContrastes de azúcares (Welch)")
    sc = figures.sugar_contrasts()
    if sc is not None:
        tables.save_table(sc, "Sugars_Welch")
    else:
        print("  omitidos: faltan los datos de azúcares tras la congelación")

    print("\nControl de calidad")
    qc = tables.quality_report()
    tables.save_table(qc, "QC_repeated_blocks")
    print(qc[qc.any_repeated_block].to_string(index=False))

    print("\nFiguras")
    for fn in (figures.supp_fig1, figures.supp_fig2, figures.fig2, figures.fig3,
               figures.fig4, figures.fig5):
        out = fn()
        if out:
            print("  " + ", ".join(p.name for p in out))
    for fn in (figures.fig6, figures.fig7, figures.fig8):
        out = fn(reg)
        if out:
            print("  " + ", ".join(p.name for p in out))


if __name__ == "__main__":
    main()
