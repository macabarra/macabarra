# PERMANOVA sobre LT₅₀ e INT

Datos: `outputs/data_txt/PERMANOVA_data.txt`.
Tablas: `outputs/tables/PERMANOVA_LT50_INT.csv` y `PERMANOVA_LT50_INT_pairwise.csv`.

## Método

PERMANOVA de una vía (Anderson 2001) con distancia euclidiana sobre el par (LT₅₀, INT) de cada
hoja, sin estandarizar (las dos variables están en °C). Estadístico pseudo-F; P por
9999 permutaciones de las etiquetas de grupo (semilla 1). Comparaciones por pares con la
misma prueba y corrección de Bonferroni.

## Resultado global

| Nivel | pseudo-F | R² | P | n | Grupos | Permutaciones |
|---|---|---|---|---|---|---|
| species | 394.2 | 0.9591 | 0.0001 | 90 | 6 | 9999 |
| accessions | 44.39 | 0.704 | 0.0001 | 60 | 4 | 9999 |

## Comparaciones por pares

| Nivel | Grupo 1 | Grupo 2 | pseudo-F | R² | P | P Bonferroni |
|---|---|---|---|---|---|---|
| species | L. mutabilis | P. sativum | 524.5 | 0.9493 | 0.0001 | 0.0015 |
| species | L. mutabilis | L. luteus | 882.2 | 0.9692 | 0.0001 | 0.0015 |
| species | L. mutabilis | L. albus | 624.4 | 0.9571 | 0.0001 | 0.0015 |
| species | L. mutabilis | L. angustifolius | 381.2 | 0.9316 | 0.0001 | 0.0015 |
| species | L. mutabilis | V. faba | 2094 | 0.9868 | 0.0001 | 0.0015 |
| species | P. sativum | L. luteus | 613.9 | 0.9564 | 0.0001 | 0.0015 |
| species | P. sativum | L. albus | 101.5 | 0.7837 | 0.0001 | 0.0015 |
| species | P. sativum | L. angustifolius | 55.75 | 0.6657 | 0.0001 | 0.0015 |
| species | P. sativum | V. faba | 852.5 | 0.9682 | 0.0001 | 0.0015 |
| species | L. luteus | L. albus | 196.4 | 0.8752 | 0.0001 | 0.0015 |
| species | L. luteus | L. angustifolius | 128.5 | 0.8211 | 0.0001 | 0.0015 |
| species | L. luteus | V. faba | 1104 | 0.9753 | 0.0001 | 0.0015 |
| species | L. albus | L. angustifolius | 0.664 | 0.02317 | 0.5172 | 1 |
| species | L. albus | V. faba | 247 | 0.8982 | 0.0001 | 0.0015 |
| species | L. angustifolius | V. faba | 132.9 | 0.826 | 0.0001 | 0.0015 |
| accessions | L. luteus (C98) | L. luteus (C195) | 46.11 | 0.6222 | 0.0001 | 0.0006 |
| accessions | L. luteus (C98) | L. luteus (C102) | 40.85 | 0.5933 | 0.0001 | 0.0006 |
| accessions | L. luteus (C98) | L. luteus (C226) | 29.06 | 0.5093 | 0.0001 | 0.0006 |
| accessions | L. luteus (C195) | L. luteus (C102) | 92.1 | 0.7669 | 0.0001 | 0.0006 |
| accessions | L. luteus (C195) | L. luteus (C226) | 7.654 | 0.2147 | 0.0033 | 0.0198 |
| accessions | L. luteus (C102) | L. luteus (C226) | 56 | 0.6667 | 0.0001 | 0.0006 |

El P mínimo posible con 9999 permutaciones es 0.0001.
