# Figura S2. Umbrales de daño del PSII e INT

Archivos: `outputs/figures/FigS2_PSII_thresholds_INT.tif` y `.png`.
Datos: `outputs/data_txt/FigS2_data.txt`.

## Qué muestra

Para cada grupo, la caja va de la media de LT₁₀ a la media de LT₉₀; la línea horizontal es la
media de LT₅₀ y el punto negro la media de INT. Las barras de error son el SE de LT₁₀ y de LT₉₀.
Panel A: especies, ordenadas por LT₅₀ de mayor a menor. Panel B: accesiones de *L. luteus*.
LT₁₀ sobre −1 °C y LT₉₀ bajo −12 °C son extrapolaciones de la regresión de cada hoja.

## Valores (media ± SE, °C)

Panel A, especies:

| Grupo | n | LT10 | LT50 | LT90 | INT |
|---|---|---|---|---|---|
| L. mutabilis | 8 | 5.41 ± 0.44 | -0.52 ± 0.02 | -5.75 ± 0.18 | -5.09 ± 0.15 |
| P. sativum | 10 | 4.03 ± 0.98 | -4.89 ± 0.07 | -13.70 ± 0.91 | -4.59 ± 0.10 |
| L. luteus | 14 | -1.43 ± 0.26 | -5.01 ± 0.09 | -9.06 ± 0.58 | -8.83 ± 0.09 |
| L. albus | 12 | -2.65 ± 0.26 | -6.76 ± 0.12 | -12.14 ± 0.86 | -6.01 ± 0.16 |
| L. angustifolius | 12 | -1.50 ± 0.20 | -6.93 ± 0.25 | -12.22 ± 0.48 | -5.78 ± 0.16 |
| V. faba | 10 | -3.20 ± 0.15 | -10.74 ± 0.08 | -18.00 ± 0.14 | -5.12 ± 0.14 |

Panel B, accesiones:

| Grupo | n | LT10 | LT50 | LT90 | INT |
|---|---|---|---|---|---|
| L. luteus (C98) | 13 | -2.27 ± 0.23 | -6.06 ± 0.20 | -10.70 ± 0.91 | -8.15 ± 0.15 |
| L. luteus (C195) | 14 | 0.89 ± 0.39 | -3.45 ± 0.14 | -7.91 ± 0.75 | -8.17 ± 0.26 |
| L. luteus (C102) | 14 | -2.97 ± 0.13 | -6.21 ± 0.06 | -9.31 ± 0.12 | -10.21 ± 0.20 |
| L. luteus (C226) | 13 | -1.08 ± 0.46 | -4.30 ± 0.12 | -9.20 ± 0.83 | -8.79 ± 0.21 |

La columna n corresponde a LT₁₀; LT₅₀ e INT tienen 15 hojas en todos los grupos.

## Limpieza

- LT_INT_species.csv: L. luteus, fila 15: LT10 = LT90 = 0.0 -> LT10 y LT90 tratados como faltantes
- LT_INT_accessions.csv: L. luteus (C226), fila 7: LT10 = LT90 = -7.6381 -> LT10 y LT90 tratados como faltantes
