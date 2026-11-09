# Barra et al. — análisis y figuras en Python

Código para reproducir los análisis, la Tabla S1 y las figuras del manuscrito
"Intrinsic freezing resistance of grain legumes" (Barra, López, Reyes,
Salvo-Garrido y Bravo; Frontiers) a partir de los datos crudos en `data/raw`.

## Uso

```bash
pip install -r requirements.txt
```

```bash
python run_all.py
```

`python run_all.py --perm 999` acelera la PERMANOVA (por defecto 9999 permutaciones).
La salida queda en `outputs/figures` (PNG y TIFF LZW a 300 dpi), `outputs/tables` (CSV) y
`outputs/run_log.txt`.

## Qué produce

| Salida | Datos de entrada | Estado |
|---|---|---|
| Tabla S1 (media ± SE, ANOVA de una vía, letras de Tukey HSD) | `FP.csv`, `LT_INT_*.csv`, `LT50_Damage_*.csv` | coincide con la versión publicada en todas las celdas |
| PERMANOVA sobre (LT50, INT), global y por pares (Bonferroni) | `LT_INT_*.csv` | completa |
| Fig. S1, programa de la cámara | `Chamber_program.csv` | completa |
| Fig. S2, LT10–LT90, LT50 e INT | `LT_INT_*.csv` | completa |
| Fig. 2 y Fig. 3, LT50 frente a INT | `LT_INT_*.csv` | completa |
| Fig. 4B y Fig. 4D, LT50 frente a daño | `LT50_Damage_*.csv` | completa (4A y 4C son fotos) |
| Fig. 5, azúcares control frente a congelación (Welch, n = 5 plantas) | `sugars_control_freezing.tsv` (columnas `A…`) | completa; los asteriscos coinciden con la figura publicada en las 54 comparaciones |
| Fig. 6, recuperación frente a LT50 | `Data_frio_maca_ll.csv` | completa |
| Fig. 7, azúcares frente a recuperación | `Data_frio_maca_ll.csv` | completa |
| Fig. 8, azúcares frente a LT50 | `Data_frio_maca_ll.csv` | completa |
| Regresiones (Tabla 1 del texto) | `Data_frio_maca_ll.csv` | las siete coinciden con lo publicado (pendiente, intercepto, R²) |

La Fig. 1 (imágenes de Fv/Fm del IMAGING-PAM) no se genera desde tablas.

## Decisiones de análisis

- Cada fila de un grupo es una hoja (`leaf` 1–15). Las tablas se emparejan por grupo y por
  posición de la fila.
- Azúcares y daño de especies se midieron por planta. Los archivos repiten cada planta en sus
  tres hojas: las pruebas a nivel de planta (daño de especies en la Tabla S1, Welch de la
  Fig. 5) usan las cinco primeras filas (n = 5).
- FP de *L. luteus* (especie) es el conjunto de las cuatro accesiones (60 hojas), como indica la
  Tabla S1.
- Se tratan como faltantes LT10 y LT90 de dos filas: *L. luteus* fila 15 (LT10 = LT90 = 0) y
  C226 fila 7 (LT10 = LT90 = −7.64). Con esa exclusión se reproducen los valores publicados.
- Figs. 6–8 y regresiones usan `Data_frio_maca_ll.csv` (una fila por hoja: Fv/Fm antes y
  después, % de recuperación, azúcares antes de la helada y LT50). Su LT50 de especies es la
  de `LT50_Damage_species.csv`. En la Tabla S1 y en las
  Figs. 2 y S2 la LT50 sale de `LT_INT_species.csv`. Ambos archivos difieren para *L. albus*
  (−6.43 frente a −6.76 °C) y, en menor medida, para *L. mutabilis* y *L. luteus*.
- Elipses: dos desviaciones estándar de la matriz de covarianza de cada grupo.
- PERMANOVA: distancia euclidiana sobre LT50 e INT sin estandarizar (ambas en °C).
- Las líneas discontinuas de la Fig. 4 son referencias visuales como en la figura original,
  no ajustes. `figures.fig4(reference_lines=False)` las quita.

## Control de calidad

`outputs/tables/QC_repeated_blocks.csv` marca los grupos donde las filas 11–15 repiten
exactamente las filas 6–10. Ocurre en `FP.csv` (los 9 grupos), en `LT_INT_species.csv`
(*P. sativum*, *L. angustifolius*, *V. faba*), en `LT_INT_accessions.csv` (C102, C195, C226) y
en la LT50 de `LT50_Damage_species.csv`. La Tabla S1 publicada usa las 15 filas, así que el
código las mantiene, pero en esos grupos hay 10 valores distintos, no 15.

### Corrección aplicada

C102, planta 3, control: la sacarosa es 2.64 mg g⁻¹ (confirmado por la autora). Los tres
archivos de azúcares traen 4.64. La corrección se aplica al leer los datos
(`SUGAR_CORRECTIONS` en `analysis/load.py`) y los archivos de `data/raw` quedan como se
recibieron. Con ella el total de esa planta es 7.57, igual en las Figs. 5, 7 y 8.
`outputs/tables/QC_total_sugar_vs_sum.csv` revisa que `Total Sugar` sea la suma de los cinco
azúcares en `Data_frio_maca_ll.csv`; después de la corrección no queda ninguna fila distinta.

## Estructura

```
analysis/config.py    rutas, orden de grupos, colores y marcadores
analysis/load.py      lectura y limpieza de data/raw
analysis/stats.py     ANOVA, Tukey + letras, Welch, OLS, PERMANOVA
analysis/plotting.py  estilo, elipses, guardado
analysis/tables.py    Tabla S1, PERMANOVA, regresiones, control de calidad
analysis/figures.py   Figs. S1, S2 y 2–8
run_all.py            ejecuta todo
```
