"""Lectura y limpieza de los archivos de data/raw.

Cada función devuelve una tabla ordenada con una columna ``group`` (nombre
canónico de especie o accesión) y una columna ``leaf`` (posición 0-14 de la
fila dentro del grupo, en el orden del archivo). Las tablas que se cruzan entre
sí (LT50 con azúcares o con recuperación) se emparejan por ``group`` y ``leaf``.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .config import RAW

SUGARS = ["fructose", "glucose", "sucrose", "raffinose", "stachyose", "total"]


# Correcciones confirmadas por la autora sobre los archivos de data/raw.
# Los archivos crudos se mantienen tal como se recibieron; la corrección se
# aplica al leerlos.
# C102, planta 3, control: sacarosa 4.64 -> 2.64 mg g-1 (total 7.57, el valor
# publicado en las Figs. 7A y 8A).
SUGAR_CORRECTIONS = [
    {"group": "L. luteus (C102)", "plant": 2, "sugar": "sucrose",
     "old": 4.64, "new": 2.64},
]


def _apply_sugar_corrections(df: pd.DataFrame, total_col: str | None = "total",
                             treatment: str | None = None) -> pd.DataFrame:
    for c in SUGAR_CORRECTIONS:
        m = (df["group"] == c["group"]) & (df["plant"] == c["plant"]) & \
            np.isclose(df[c["sugar"]], c["old"])
        if treatment is not None:
            m &= df["treatment"] == treatment
        df.loc[m, c["sugar"]] = c["new"]
        if total_col is not None:
            df.loc[m, total_col] = df.loc[m, SUGARS[:-1]].sum(axis=1).round(2)
    return df


def normalize_name(name: str) -> str:
    """'L.luteus(C98)', 'gL. luteus (C98)', 'V.faba', 'P. sativum ' -> forma canónica."""
    s = str(name).strip()
    s = re.sub(r"^[a-z](?=[A-Z]\.)", "", s)          # prefijo de orden en sugar_accession
    s = re.sub(r"^([A-Z])\.\s*", r"\1. ", s)          # 'L.luteus' -> 'L. luteus'
    s = re.sub(r"\s*\(\s*", " (", s)                  # 'luteus(C98)' -> 'luteus (C98)'
    s = re.sub(r"\s+", " ", s)
    return s


def _finish(df: pd.DataFrame) -> pd.DataFrame:
    df["group"] = df["group"].map(normalize_name)
    df["leaf"] = df.groupby("group").cumcount()
    df["plant"] = df["leaf"] % 5
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
def load_lt_int(level: str) -> tuple[pd.DataFrame, list[str]]:
    """LT10, LT50, LT90 e INT por hoja. ``level`` = 'species' o 'accessions'.

    Limpieza (necesaria para reproducir la Tabla S1):
    * filas con LT10 = LT90 = 0 -> LT10 y LT90 faltantes (L. luteus, especie);
    * filas con LT10 = LT90 distinto de 0 -> LT10 y LT90 faltantes (C226).
    """
    df = pd.read_csv(RAW / f"LT_INT_{level}.csv")
    df = df.rename(columns={"Grain.Legumes": "group"})
    df = _finish(df)
    notes = []
    bad = df["LT10"].notna() & (df["LT10"] == df["LT90"])
    for _, r in df[bad].iterrows():
        notes.append(
            f"LT_INT_{level}.csv: {r.group}, fila {r.leaf + 1}: LT10 = LT90 = {r.LT10} "
            "-> LT10 y LT90 tratados como faltantes"
        )
    df.loc[bad, ["LT10", "LT90"]] = np.nan
    return df, notes


def load_fp() -> pd.DataFrame:
    df = pd.read_csv(RAW / "FP.csv", sep=";", decimal=",", encoding="utf-8-sig")
    df.columns = ["group", "FP"]
    return _finish(df)


def load_damage(level: str) -> pd.DataFrame:
    """Daño visible (%) y LT50. En especies el daño se midió por planta."""
    if level == "species":
        df = pd.read_csv(RAW / "LT50_Damage_species.csv", sep=";")
        df.columns = ["group", "LT50", "damage"]
    else:
        df = pd.read_csv(RAW / "LT50_Damage_accessions.csv")
        df.columns = ["group", "damage", "LT50"]
    return _finish(df)


def load_sugars(level: str, treatment: str = "control") -> pd.DataFrame | None:
    """Azúcares solubles (mg g-1 peso seco). Medidos por planta (5 por grupo).

    ``treatment='freezing'`` busca sugar_freezing_{level}.csv con el mismo
    formato; devuelve None si el archivo no existe.
    """
    if treatment == "control":
        path = RAW / f"sugar_{level}.csv"
    else:
        path = RAW / f"sugar_freezing_{level}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, sep=";", encoding="latin-1", decimal=".")
    df.columns = ["group"] + SUGARS
    for c in SUGARS:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")
    return _apply_sugar_corrections(_finish(df))


def load_sugars_treatments() -> pd.DataFrame | None:
    """Azúcares de hoja en control y congelación (sugars_control_freezing.tsv).

    Usa las columnas que empiezan con 'A' (las que coinciden con
    sugar_species.csv y sugar_accessions.csv). Las columnas 'N' no se usan.
    El total es la suma de los cinco azúcares. Una fila por planta.
    """
    path = RAW / "sugars_control_freezing.tsv"
    if not path.exists():
        return None
    df = pd.read_csv(path, sep="\t", decimal=",")
    a = {c: c for c in df.columns if c.startswith("A")}
    ren = {"Genotype": "group", "Treatment": "treatment"}
    for c in a:
        low = c.lower()
        for key, name in (("fructose", "fructose"), ("glucose", "glucose"),
                          ("sacarose", "sucrose"), ("rafinose", "raffinose"),
                          ("estaquiose", "stachyose")):
            if key in low:
                ren[c] = name
    df = df.rename(columns=ren)[["group", "treatment"] + SUGARS[:-1]]
    df["total"] = df[SUGARS[:-1]].sum(axis=1)
    df["treatment"] = df["treatment"].str.strip().str.lower()
    df["group"] = (df["group"].map(normalize_name)
                   .str.replace("angustifolium", "angustifolius"))
    df["plant"] = df.groupby(["group", "treatment"]).cumcount()
    df = _apply_sugar_corrections(df, treatment="control")
    return df.reset_index(drop=True)


LATIN = {"Lupinus": "L.", "Pisum": "P.", "Vicia": "V."}


def load_master() -> pd.DataFrame:
    """Data_frio_maca_ll.csv: una fila por hoja con Fv/Fm antes y después de la
    helada, % de recuperación, azúcares de la planta (antes de la helada) y LT50.

    Es la fuente de las Figs. 6, 7 y 8 y de las regresiones.
    """
    df = pd.read_csv(RAW / "Data_frio_maca_ll.csv", sep=";", encoding="utf-8-sig",
                     dtype=str)
    df.columns = ["group", "leaf_id", "t0", "fvfm_before", "t1", "fvfm_after",
                  "recovery", "total", "LT50"] + SUGARS[:-1]
    for c in ["fvfm_before", "fvfm_after", "recovery", "total", "LT50"] + SUGARS[:-1]:
        df[c] = df[c].str.replace(",", ".").astype(float)
    g = df["group"].str.replace(" ", " ").str.strip()
    g = g.str.replace(r"\s+L$", "", regex=True)          # 'Lupinus albus L' -> 'Lupinus albus'
    for genus, abbr in LATIN.items():
        g = g.str.replace(rf"^{genus}\s+", f"{abbr} ", regex=True)
    df["group"] = g
    df = df.drop(columns=["t0", "t1"])
    df["leaf"] = df.groupby("group").cumcount()
    df["plant"] = df["leaf"] % 5
    df = _apply_sugar_corrections(df, total_col=None)
    df["sugar_sum"] = df[SUGARS[:-1]].sum(axis=1)
    return df.reset_index(drop=True)


def load_chamber() -> pd.DataFrame:
    df = pd.read_csv(RAW / "Chamber_program.csv", sep=";")
    df.columns = ["time", "temp", "light"]
    t = pd.to_timedelta(df["time"])
    df["hour"] = t.dt.total_seconds() / 3600
    return df


def plants_only(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por planta (las cinco primeras de cada grupo).

    Los archivos de daño (especies) y de azúcares repiten el valor de cada
    planta en sus tres hojas; para las pruebas a nivel de planta se usa n = 5.
    """
    return df[df["leaf"] < 5].copy()
