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
    return _finish(df)


def load_recovery(level: str) -> pd.DataFrame | None:
    """Recuperación fotoquímica por hoja: recovery_{level}.csv.

    Formato esperado (separador ';'): group;Fv/Fm initial;Fv/Fm final
    o bien group;Recovery. Las filas deben seguir el mismo orden que
    LT_INT_accessions.csv / LT50_Damage_species.csv. Devuelve None si falta.
    """
    path = RAW / f"recovery_{level}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, sep=None, engine="python", decimal=",")
    cols = [c.strip() for c in df.columns]
    df.columns = ["group"] + cols[1:]
    if len(cols) >= 3:
        df["recovery"] = 100 * df.iloc[:, 2].astype(float) / df.iloc[:, 1].astype(float)
    else:
        df["recovery"] = df.iloc[:, 1].astype(float)
    return _finish(df[["group", "recovery"]])


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
