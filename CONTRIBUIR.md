# Cómo aportar

Tres minutos de lectura. La idea es que puedas ayudar **sin saber git ni programar**.

## Lo que hace falta

El dato que falta es **qué formas de cumplimiento controla cada CRS**. No todos llevan
todas: los más chicos suelen tener remisión condicional y reclusión parcial, pero no
libertad vigilada intensiva ni monitoreo telemático. Eso obliga a derivar, y hoy no está
escrito en ninguna parte.

Si trabajas con un CRS y sabes qué lleva, eso es exactamente lo que se necesita.

## Cómo se aporta

1. Entra a **[Issues → New issue](../../issues/new/choose)**.
2. Elige:
   - **Aportar formas de cumplimiento** — el aporte principal.
   - **Corregir la jurisdicción de una comuna** — si un CRS distinto atiende esa comuna.
   - **Informar que una forma la controla otro establecimiento** — cuando en una comuna una
     forma no la lleva el CRS sino un CCP, un CDP u otro (como el CCP Buin con la remisión
     condicional de Buin, Paine e Isla de Maipo).
   - **Corregir un dato de contacto** — una dirección o teléfono que cambió.
3. Llena el formulario. Son listas y casillas: no hay forma de romper el formato.
4. Envíalo y listo.

Quien mantiene el repositorio lo revisa. Si está en orden, le pone la etiqueta
**`aprobado`** y un robot escribe la fila y abre la propuesta de cambio. Recibirás un
aviso cuando entre.

## Tres reglas

**Aporta solo lo que te conste.** Es preferible una respuesta corta y firme que una larga
y a medias. Este dato termina en resoluciones.

**Di cómo lo sabes.** El formulario pide la fuente y es obligatoria: con quién hablaste,
qué documento, qué fecha. Un dato sin fuente no se puede defender frente a nadie, y dentro
de seis meses nadie recordará de dónde salió.

**No marcar no es decir que no.** Dejar una forma sin marcar significa «no lo sé», que es
una respuesta perfectamente válida. Si confirmaste que un CRS **no** lleva algo, eso va en
la segunda lista del formulario — y vale tanto como lo afirmativo, porque evita
derivaciones inútiles.

## Si alguien ya dijo algo distinto

Puede pasar: dos colegas informan cosas distintas del mismo CRS. Es normal —cambian los
convenios, los programas se abren y se cierran— y no es un problema, es información.

Cuando ocurre, la propuesta de cambio muestra el dato anterior y el nuevo lado a lado, con
sus fuentes y sus fechas. Ahí se conversa en el issue y se decide. **Gana la fuente más
firme y más reciente**, no quien llegó primero.

## Nada de datos personales

Este repositorio describe **instituciones**. Nunca:

- nombres de funcionarios (ni de Gendarmería ni de tribunales),
- RUT de nadie,
- teléfonos o correos particulares.

Direcciones y teléfonos **institucionales** sí, porque ya son públicos. El validador
rechaza automáticamente cualquier cosa que parezca un RUT.

Tu nombre de usuario de GitHub sí queda registrado como autor del aporte —es lo que
permite volver a preguntarte si algo no calza—. Si prefieres no aparecer, dilo en el issue
y se anota como `anonimo`.

## Si sí sabes git

Los pull requests directos son bienvenidos. Antes de enviarlo:

```bash
python herramientas/validar.py
```

Si tocas `datos/crs.csv` o `vocabulario/formas.csv`, hay que regenerar los formularios,
porque llevan esas listas adentro:

```bash
python herramientas/generar_formularios.py
```

Ambos corren solos en cada propuesta, así que si algo falla te vas a enterar igual.

## Cómo revisar (para quien mantiene)

1. Lee el issue: ¿la fuente sostiene lo que afirma?
2. Si sí, etiqueta **`aprobado`** → el robot abre la propuesta.
3. Revisa el diff. Ojo con las filas **modificadas**: ahí alguien está contradiciendo un
   dato anterior, y conviene mirar las dos fuentes antes de combinar.
4. Combina. El issue se cierra solo.

Si el aporte no basta, no lo cierres sin más: pregunta en el issue. Casi siempre falta un
detalle de la fuente, y la persona lo tiene a mano.
