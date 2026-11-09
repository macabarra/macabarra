"""Rutas, orden de grupos, colores y marcadores comunes a todas las figuras."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
FIG_DIR = OUT / "figures"
TAB_DIR = OUT / "tables"

DPI = 300
FIG_FORMATS = ("png", "tif")

# Nombres canónicos -------------------------------------------------------
SPECIES = [
    "L. luteus",
    "L. albus",
    "L. angustifolius",
    "P. sativum",
    "L. mutabilis",
    "V. faba",
]
ACCESSIONS = [
    "L. luteus (C102)",
    "L. luteus (C195)",
    "L. luteus (C226)",
    "L. luteus (C98)",
]
# Subconjunto de cuatro especies usado en Fig. 7B y Fig. 8B
SPECIES_SUBSET = ["L. albus", "L. mutabilis", "P. sativum", "V. faba"]
# Nueve entradas (cinco especies + cuatro accesiones) usadas en Fig. 6 y en la
# regresión combinada (n = 135)
ALL_ENTRIES = [s for s in SPECIES if s != "L. luteus"] + ACCESSIONS

# Colores y marcadores fijos ------------------------------------------------
COLORS = {
    "L. luteus": "#1FA5C4",
    "L. albus": "#2F7FC1",
    "L. angustifolius": "#7090C4",
    "P. sativum": "#9A4FA3",
    "L. mutabilis": "#E4622C",
    "V. faba": "#2E9A55",
    "L. luteus (C102)": "#5BC4DB",
    "L. luteus (C195)": "#1E6F80",
    "L. luteus (C226)": "#8FD3E0",
    "L. luteus (C98)": "#2A8FA3",
}
MARKERS = {
    "L. luteus (C102)": "v",
    "L. luteus (C195)": "s",
    "L. luteus (C226)": "^",
    "L. luteus (C98)": "D",
}
DEFAULT_MARKER = "o"

SHORT_LABEL = {"L. angustifolius": "L. angust."}


def color(group: str) -> str:
    return COLORS[group]


def marker(group: str) -> str:
    return MARKERS.get(group, DEFAULT_MARKER)
