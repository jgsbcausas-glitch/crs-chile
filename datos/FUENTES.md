# De dónde sale cada dato

| Archivo | Fuente | Fecha | Cómo se actualiza |
|---|---|---|---|
| `comunas.csv` | Nomenclatura oficial de comunas (346) con su CUT. `lat`/`lon` es un centroide aproximado —el promedio de los cuarteles de Carabineros de la comuna, o sea dónde está la gente— y a mano en las 3 sin cuartel (Negrete, Antártica, Río Verde). Solo sirve para ordenar por cercanía; no dibuja un límite comunal. | 2026-08 | Casi nunca. Cambia cuando se crea una comuna. |
| `crs.csv` | [gendarmeria.gob.cl/horarios1.html](https://www.gendarmeria.gob.cl/horarios1.html) | 2026-08-17 | Cuando Gendarmería publique cambios. |
| `crs_jurisdiccion.csv` | Tabla oficial de jurisdicción de los CRS por comuna | 2026-08-17 | **323 explícitas** de la tabla, **23 inferidas** por provincia. Las inferidas se corrigen con aportes. |
| `establecimientos.csv` | [gendarmeria.gob.cl/establecimientos.html](https://www.gendarmeria.gob.cl/establecimientos.html) | 2026-08-17 | Cuando Gendarmería publique cambios. |
| `crs_formas.csv` | **Aportes de la comunidad.** Nadie publica este dato. | continuo | Cada fila trae quién la aportó, cuándo y con qué fundamento. |
| `control_por_forma.csv` | **Aportes de la comunidad.** Excepciones a la regla «el CRS controla»: para una comuna y una forma, el establecimiento que la lleva de verdad (un CCP, un CDP, otro CRS). | continuo | Una fila por comuna y forma; `establecimiento` es una llave de `crs.csv` o de `establecimientos.csv`. |

## Investigación documental nacional (2026-08-18)

Una revisión de fuentes públicas de Gendarmería —informes de PSBC, cuentas
públicas, documentos de sistema abierto— dejó **71 combinaciones CRS × forma
confirmadas y 139 probables**, con su bibliografía en `fuentes.csv`.

La distinción se conserva en la columna `controla` y **no se colapsa**: un
`probable` sale de que el programa opere en los 41 CRS, no de que alguien haya
visto a este en particular. Presentarlos juntos habría llenado el catastro a
costa de volverlo poco fiable, que es lo contrario de para qué existe.

No se importó la base operativa comuna × forma (2.768 filas) que venía con la
investigación: es una vista derivada de la jurisdicción más las formas, y sus
únicas excepciones reales —las tres del CCP Buin— ya estaban acá. Duplicar un
dato derivado es garantizar que algún día discrepe de su origen.

**La expulsión salió del vocabulario** por decisión de uso: como pena
sustitutiva es excepcionalísima, y la investigación no encontró evidencia
alguna sobre ella (0 confirmadas, 0 probables, 41 desconocidas).

## El CUT manda sobre el nombre

Todos los cruces se hacen por **código único territorial**, nunca por el nombre de la
comuna. La razón es concreta: la tabla oficial de Gendarmería trae «Ránqui», que no existe
—es **Ninhue**, CUT 16207— y cruzando por nombre se pierde una comuna y se duplica otra.

## Tres orígenes distintos, y se dicen

En `crs_jurisdiccion.csv`, la columna `origen` distingue:

- **`explicita`** — está en la tabla oficial de Gendarmería. Se puede afirmar.
- **`inferida`** — la comuna no figura en la tabla; el CRS se dedujo por provincia.
  **Conviene confirmarlo.** Son 23.
- **`manual`** — alguien la corrigió con fundamento. Manda sobre lo publicado, y la nota
  dice por qué.

Presentar una deducción como si fuera dato oficial es la única forma segura de que este
repositorio deje de servir. Por eso se separan.
