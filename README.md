# CRS Chile — quién controla las penas sustitutivas, comuna por comuna

Un tribunal que despacha una pena sustitutiva necesita saber tres cosas:

1. **Qué CRS atiende esa comuna.** Gendarmería lo publica, pero la tabla tiene erratas.
2. **Qué formas de cumplimiento controla ese CRS.** Esto **no lo publica nadie**.
3. **A quién derivar si el competente no lleva esa forma.** Hoy se resuelve llamando por teléfono.

Este repositorio existe para responder las tres, y para que la respuesta la construyamos
entre quienes trabajamos con esto todos los días. **La segunda es la que falta**, y es la
razón de ser del proyecto: el dato vive repartido en la cabeza de mucha gente y en ninguna
base de datos.

> [!IMPORTANT]
> **Esto no es oficial ni vinculante.** Es un dato de referencia construido por
> funcionarios judiciales a partir de fuentes públicas y de lo que cada cual verifica en
> su trabajo. Gendarmería no lo revisa ni lo respalda. **Antes de despachar, confirme con
> el CRS.** Sirve para no partir de cero, no para reemplazar esa confirmación.

## Qué hay acá

| Archivo | Qué contiene | Estado |
|---|---|---|
| [`datos/comunas.csv`](datos/comunas.csv) | Las 346 comunas con su código oficial (CUT), región y provincia | completo |
| [`datos/crs.csv`](datos/crs.csv) | Los 41 Centros de Reinserción Social, con sede, dirección y teléfono | completo |
| [`datos/crs_jurisdiccion.csv`](datos/crs_jurisdiccion.csv) | Qué CRS atiende cada comuna | 323 de la tabla oficial · **23 deducidas** |
| [`datos/crs_formas.csv`](datos/crs_formas.csv) | Qué formas de cumplimiento controla cada CRS | **lo que estamos construyendo** |
| [`datos/establecimientos.csv`](datos/establecimientos.csv) | Los otros 175 establecimientos de Gendarmería, con llave estable | completo |
| [`datos/control_por_forma.csv`](datos/control_por_forma.csv) | Excepciones: cuando una forma **no** la controla el CRS sino otro establecimiento | **se construye con aportes** |
| [`vocabulario/formas.csv`](vocabulario/formas.csv) | Las formas de cumplimiento, con su norma | completo |

**Regla general y excepciones.** Lo normal es que el CRS competente controle las formas
de cumplimiento, y eso es lo que responde `crs_jurisdiccion.csv`. Pero no siempre: el
**CCP Buin** supervisa la remisión condicional de Buin, Paine e Isla de Maipo, aunque esas
comunas dependan de dos CRS distintos. Esas excepciones van en `control_por_forma.csv`,
por comuna y forma, y pueden apuntar a cualquier establecimiento —un CCP, un CDP, otro CRS—.
La ficha de la comuna muestra primero el CRS y debajo las excepciones.

El **CUT** (código único territorial) es la llave de todo. Los nombres de comuna están
para leer: cruzarlos es como se pierden comunas —así descubrimos que «Ránqui», en la tabla
oficial de Gendarmería, es en realidad **Ninhue**—.

## Cómo aportar (no necesitas saber git)

> **¿Vas a invitar a colegas?** Compárteles la
> [invitación con el paso a paso](https://jgsbcausas-glitch.github.io/crs-chile/participa.html):
> explica el porqué, guía la creación de la cuenta botón por botón, y trae un texto listo
> para pegar en un correo o un grupo. Se imprime como volante.

1. Entra a **[Issues → New issue](../../issues/new/choose)**.
2. Elige el formulario que corresponda y llénalo. Todo son listas desplegables y casillas.
3. Listo. Alguien lo revisa y un robot lo convierte en una fila del archivo.

Solo hace falta una cuenta de GitHub, que es gratis. La guía completa está en
**[CONTRIBUIR.md](CONTRIBUIR.md)** y se lee en tres minutos.

**Aporta solo lo que te conste, y di cómo lo sabes.** Un dato sin fuente no se puede
sostener frente a nadie, así que el formulario la pide. Y **no marcar una forma no
significa que el CRS no la lleve**: significa que no lo sabes, que es una respuesta
perfectamente válida y bastante mejor que adivinar.

## Cómo usar los datos

Los CSV son UTF-8 con `;` como separador —así los abre Excel en Chile de un doble clic—.
Para leerlos desde un programa, la dirección estable de cada archivo es:

```
https://raw.githubusercontent.com/jgsbcausas-glitch/crs-chile/main/datos/crs_formas.csv
```

Están bajo **[CC BY 4.0](LICENCIA-DATOS.md)**: úsalos donde quieras, incluso
comercialmente, citando la fuente. Las herramientas están bajo [MIT](LICENSE).

## Cómo se mantiene la calidad

Cada cambio pasa por [`herramientas/validar.py`](herramientas/validar.py), que corre
automáticamente en cada propuesta y **rechaza** lo que no cuadra:

- una comuna que no existe, o cuyo nombre no calza con su CUT;
- un CRS mal escrito, o una forma de cumplimiento que no está en el vocabulario;
- dos filas para el mismo CRS y la misma forma —eso se corrige, no se duplica—;
- una fila sin fuente o con la fecha mal puesta;
- **cualquier cosa que parezca un RUT**: este repositorio describe instituciones, no personas.

```bash
python herramientas/validar.py
```

## De dónde salen los datos

- **CRS, jurisdicción y establecimientos**: [gendarmeria.gob.cl](https://www.gendarmeria.gob.cl/establecimientos.html)
  y su tabla de jurisdicciones, agosto de 2026.
- **Comunas y CUT**: nomenclatura oficial vigente (346 comunas).
- **Formas de cumplimiento**: aportes de quienes trabajan con cada CRS. Cada fila dice
  quién la aportó, cuándo y con qué fundamento.

Las 23 comunas que no figuran en la tabla oficial llevan `origen = inferida`: su CRS se
dedujo por provincia y **conviene confirmarlo**. Son las primeras que vale la pena
arreglar — [están acá](../../issues/new?template=02-correccion-de-jurisdiccion.yml).

## Nada de datos personales

Solo direcciones y teléfonos **institucionales**, de los que Gendarmería ya publica. Nunca
nombres de funcionarios, RUT ni teléfonos particulares. El validador lo revisa en cada
cambio, pero si algo se cuela, [avísanos](../../issues/new/choose) y se saca de inmediato.

---

Coordinado por **F. Barrera**, a partir de fuentes públicas y de lo que aporta cada
colega. Nació de un problema concreto: cuando la agenda ofrece una audiencia de control de
ejecución, hay que saber a qué CRS se dirige el oficio. Se abrió porque el problema no es
de un tribunal, es de todos.
