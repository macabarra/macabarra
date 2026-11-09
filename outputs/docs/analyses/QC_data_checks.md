# Control de calidad de los datos

Datos: `outputs/data_txt/QC_data.txt`. Tablas: `outputs/tables/QC_repeated_blocks.csv` y
`QC_total_sugar_vs_sum.csv`.

## Limpieza aplicada

- LT_INT_species.csv: L. luteus, fila 15: LT10 = LT90 = 0.0 -> LT10 y LT90 tratados como faltantes
- LT_INT_accessions.csv: L. luteus (C226), fila 7: LT10 = LT90 = -7.6381 -> LT10 y LT90 tratados como faltantes

Con esta exclusión los valores de LT₁₀ y LT₉₀ coinciden con la Tabla S1 publicada.

## Corrección confirmada

- *L. luteus* (C102), planta 3, control: sacarosa 2,64 mg g⁻¹ (los archivos traen 4,64). Se
  aplica al leer los datos (`SUGAR_CORRECTIONS` en `analysis/load.py`).

## Bloques de filas repetidos

En cada grupo de 15 filas se comparó el bloque 11–15 con los bloques 1–5 y 6–10. En los
siguientes grupos las filas 11–15 son idénticas a las filas 6–10:

| Archivo | Grupo | Columnas comparadas |
|---|---|---|
| FP.csv | L. luteus (C98) | FP |
| FP.csv | L. luteus (C195) | FP |
| FP.csv | L. luteus (C102) | FP |
| FP.csv | L. luteus (C226) | FP |
| FP.csv | L. albus | FP |
| FP.csv | L. angustifolius | FP |
| FP.csv | P. sativum | FP |
| FP.csv | V. faba | FP |
| LT_INT_species.csv | P. sativum | LT50+INT |
| LT_INT_species.csv | L. angustifolius | LT50+INT |
| LT_INT_species.csv | V. faba | LT50+INT |
| LT_INT_accessions.csv | L. luteus (C195) | LT50+INT |
| LT_INT_accessions.csv | L. luteus (C102) | LT50+INT |
| LT_INT_accessions.csv | L. luteus (C226) | LT50+INT |
| LT50_Damage_species.csv | V. faba | LT50 |
| LT50_Damage_species.csv | L. albus | LT50 |
| LT50_Damage_species.csv | L. angustifolius | LT50 |
| LT50_Damage_species.csv | P. sativum | LT50 |
| LT50_Damage_species.csv | L. mutabilis | LT50 |

En esos grupos hay 10 valores distintos y no 15. La Tabla S1 publicada usa las 15 filas y el
código las mantiene; los SE y P calculados con n = 15 son menores que con n = 10.

## Azúcar total frente a suma de componentes

Después de la corrección, `Total Sugar` coincide con la suma de los cinco azúcares en todas las
filas de `Data_frio_maca_ll.csv`.
