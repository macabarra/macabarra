# Regresiones lineales (Tabla 1 del manuscrito; Figs. 6, 7 y 8)

Datos: `outputs/data_txt/Regressions_data.txt`. Tabla: `outputs/tables/Regressions.csv`.

## Método

Mínimos cuadrados ordinarios (`scipy.stats.linregress`) con la hoja como observación. P es el
de la pendiente. Subconjuntos: todas las entradas (5 especies + 4 accesiones, n = 135),
accesiones de *L. luteus* (n = 60) y cuatro especies (*L. albus*, *L. mutabilis*,
*P. sativum*, *V. faba*; n = 60). Azúcares totales medidos antes de la helada.

## Resultados

| Modelo | Subconjunto | n | Pendiente | Intercepto | R² | P | Pend. publicada | Int. publicado | R² publicado |
|---|---|---|---|---|---|---|---|---|---|
| recovery ~ LT50 | all entries | 135 | -4.393 | 47.76 | 0.618 | 1.457e-29 | -4.39 | 47.8 | 0.618 |
| recovery ~ total sugars | L. luteus accessions | 60 | 6.682 | 19.82 | 0.574 | 2.516e-12 | 6.68 | 19.8 | 0.574 |
| LT50 ~ total sugars | L. luteus accessions | 60 | -0.562 | -0.91 | 0.433 | 1.108e-08 | -0.56 | -0.9 | 0.433 |
| recovery ~ total sugars | four-species subset | 60 | 2.692 | 26.02 | 0.649 | 8.218e-15 | 2.69 | 26 | 0.649 |
| LT50 ~ total sugars | four-species subset | 60 | -0.566 | 4.34 | 0.636 | 2.402e-14 | -0.57 | 4.3 | 0.636 |
| recovery ~ total sugars | all entries | 135 | 1.258 | 56.74 | 0.264 | 1.887e-10 |  |  | 0.264 |
| LT50 ~ total sugars | all entries | 135 | -0.217 | -2.87 | 0.246 | 9.584e-10 |  |  | 0.246 |

Las siete regresiones coinciden con los valores publicados.
