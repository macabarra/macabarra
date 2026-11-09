# Tabla S1. Parámetros de resistencia a la congelación: ANOVA de una vía y Tukey HSD

Datos: `outputs/data_txt/TableS1_data.txt`.
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

## Especies

| Grupo | FP (°C) | INT (°C) | LT10 (°C) | LT50 (°C) | LT90 (°C) | Damage (%) |
|---|---|---|---|---|---|---|
| V. faba | -3.89 ± 0.12 ab | -5.12 ± 0.14 c | -3.20 ± 0.15 a | -10.74 ± 0.08 a | -18.00 ± 0.14 a | 54.78 ± 5.48 b |
| L. mutabilis | -1.68 ± 0.08 c | -5.09 ± 0.15 c | 5.41 ± 0.44 c | -0.52 ± 0.02 d | -5.75 ± 0.18 d | 97.72 ± 0.16 d |
| L. albus | -3.44 ± 0.19 ab | -6.01 ± 0.16 b | -2.65 ± 0.26 ab | -6.76 ± 0.12 b | -12.14 ± 0.86 b | 34.92 ± 2.05 a |
| L. angustifolius | -4.20 ± 0.11 a | -5.78 ± 0.16 b | -1.50 ± 0.20 ab | -6.93 ± 0.25 b | -12.22 ± 0.48 b | 82.02 ± 1.50 c |
| P. sativum | -2.40 ± 0.04 c | -4.59 ± 0.10 c | 4.03 ± 0.98 c | -4.89 ± 0.07 c | -13.70 ± 0.91 b | 37.28 ± 2.75 a |
| L. luteus | -3.44 ± 0.15 b | -8.83 ± 0.09 a | -1.43 ± 0.26 b | -5.01 ± 0.09 c | -9.06 ± 0.58 c | 53.10 ± 1.31 b |
| ANOVA F (P) | 18.7 (<0.001) | 124.9 (<0.001) | 60.5 (<0.001) | 712.6 (<0.001) | 36.6 (<0.001) | 82.0 (<0.001) |

Coincidencia con la Tabla S1 publicada: 42 de 42 valores (medias, SE y F).
## Accesiones de *L. luteus*

| Grupo | FP (°C) | INT (°C) | LT10 (°C) | LT50 (°C) | LT90 (°C) | Damage (%) |
|---|---|---|---|---|---|---|
| L. luteus (C102) | -4.74 ± 0.28 a | -10.21 ± 0.20 a | -2.97 ± 0.13 a | -6.21 ± 0.06 a | -9.31 ± 0.12 | 7.44 ± 0.76 a |
| L. luteus (C98) | -2.41 ± 0.06 c | -8.15 ± 0.15 b | -2.27 ± 0.23 ab | -6.06 ± 0.20 a | -10.70 ± 0.91 | 16.31 ± 0.82 b |
| L. luteus (C226) | -3.82 ± 0.22 b | -8.79 ± 0.21 b | -1.08 ± 0.46 b | -4.30 ± 0.12 b | -9.20 ± 0.83 | 92.39 ± 0.71 c |
| L. luteus (C195) | -2.78 ± 0.15 c | -8.17 ± 0.26 b | 0.89 ± 0.39 c | -3.45 ± 0.14 c | -7.91 ± 0.75 | 93.53 ± 0.23 c |
| ANOVA F (P) | 28.8 (<0.001) | 21.8 (<0.001) | 27.3 (<0.001) | 94.5 (<0.001) | 2.6 (0.066) | 4915.1 (<0.001) |

Coincidencia con la Tabla S1 publicada: 30 de 30 valores (medias, SE y F).
