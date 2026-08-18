#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenera los formularios de aporte a partir de los datos.

Los formularios llevan la lista de los 41 CRS y las formas de cumplimiento
dentro. Escribirlas a mano garantiza que algún día no calcen con los CSV y que
un colega no pueda aportar sobre un CRS recién agregado. Acá se generan.

    python herramientas/generar_formularios.py            # los escribe
    python herramientas/generar_formularios.py --comprobar # solo avisa si cambiaron
"""
import argparse
import csv
import io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for flujo in (sys.stdout, sys.stderr):
    if hasattr(flujo, 'reconfigure'):
        flujo.reconfigure(encoding='utf-8', errors='replace')


def leer(ruta):
    with io.open(os.path.join(RAIZ, ruta), encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def construir():
    crs = sorted(leer('datos/crs.csv'), key=lambda r: r['nombre'])
    formas = leer('vocabulario/formas.csv')
    lista_crs = '\n'.join('        - "%s"' % r['nombre'] for r in crs)
    lista_formas = '\n'.join('        - label: "%s"' % f['nombre'] for f in formas)
    lista_formas_desplegable = '\n'.join('        - "%s"' % f['nombre'] for f in formas)

    # Quién puede controlar una forma: cualquier establecimiento, CRS incluidos.
    # El nombre ya trae el tipo adentro («CCP BUIN»), y la comuna desambigua.
    controladores = sorted(
        [(r['nombre'], r['comuna_sede']) for r in crs]
        + [(r['nombre'], r['comuna']) for r in leer('datos/establecimientos.csv')]
    )
    lista_controladores = '\n'.join('        - "%s (%s)"' % (n, c) for n, c in controladores)

    formulario_formas = '''name: Aportar formas de cumplimiento de un CRS
description: Decir qué penas sustitutivas controla un CRS. Es el dato que Gendarmería no publica.
title: "[FORMAS] "
labels: ["formas-de-cumplimiento", "por-revisar"]
body:
  - type: markdown
    attributes:
      value: |
        Gracias por aportar. Este formulario existe para que **no tengas que saber git**:
        lo llenas, alguien lo revisa y un robot lo convierte en una fila del archivo.

        Aporta solo lo que te conste. **Dejar una forma sin marcar no es decir que no la
        lleva** — es decir que no lo sabes, que es una respuesta perfectamente válida.

        Escribe el nombre del CRS en el título, después de `[FORMAS]`. Si se te
        olvida no pasa nada: al aprobarlo se corrige solo.

  - type: dropdown
    id: crs
    attributes:
      label: ¿Qué CRS?
      options:
%s
    validations:
      required: true

  - type: checkboxes
    id: controla
    attributes:
      label: Formas de cumplimiento que SÍ controla
      description: Marca solo las que te consten.
      options:
%s

  - type: checkboxes
    id: no_controla
    attributes:
      label: Formas que confirmaste que NO controla
      description: "Este dato vale tanto como el anterior y evita derivaciones inútiles."
      options:
%s

  - type: dropdown
    id: como
    attributes:
      label: ¿Cómo lo sabes?
      description: Sin esto el dato no se puede sostener frente a nadie.
      options:
        - "Me lo confirmó el CRS (llamada o correo)"
        - "Aparece en un documento oficial de Gendarmería"
        - "Lo sé por causas que tramito habitualmente en ese CRS"
        - "Me lo informó otro tribunal"
        - "Otro (lo explico abajo)"
    validations:
      required: true

  - type: input
    id: detalle
    attributes:
      label: Detalle de la fuente
      description: Con quién hablaste, qué documento, qué fecha. Una línea basta.
      placeholder: "Llamada al CRS el 12-08-2026, jefatura técnica."
    validations:
      required: true

  - type: textarea
    id: nota
    attributes:
      label: Algo más que convenga saber (opcional)
      placeholder: "Lleva PSBC solo con convenio municipal vigente."

  - type: checkboxes
    id: sin_datos_personales
    attributes:
      label: Confirmación
      options:
        - label: "No incluí nombres, RUT ni teléfonos personales de nadie."
          required: true
''' % (lista_crs, lista_formas, lista_formas)

    formulario_jur = '''name: Corregir la jurisdicción de una comuna
description: Decir que una comuna la atiende un CRS distinto del que figura.
title: "[JURISDICCIÓN] "
labels: ["jurisdiccion", "por-revisar"]
body:
  - type: markdown
    attributes:
      value: |
        La tabla que publica Gendarmería tiene erratas, y 23 comunas no figuran en ella:
        su CRS está **deducido por provincia** y puede estar mal. Si sabes cuál es el que
        de verdad la controla, esto lo arregla para todos.

  - type: input
    id: comuna
    attributes:
      label: Comuna
      placeholder: "Panguipulli"
    validations:
      required: true

  - type: dropdown
    id: crs
    attributes:
      label: CRS que la atiende
      options:
%s
    validations:
      required: true

  - type: input
    id: figura
    attributes:
      label: ¿Qué dice hoy el repo? (opcional)
      placeholder: "CRS VILLARRICA"

  - type: input
    id: detalle
    attributes:
      label: ¿Cómo lo sabes?
      placeholder: "Lo confirmó el CRS Valdivia por teléfono el 17-08-2026."
    validations:
      required: true
''' % lista_crs

    formulario_control = '''name: Informar que una forma la controla otro establecimiento
description: Cuando en una comuna una forma de cumplimiento no la lleva el CRS, sino un CCP, un CDP u otro.
title: "[CONTROL] "
labels: ["control-por-forma", "por-revisar"]
body:
  - type: markdown
    attributes:
      value: |
        La regla general es que el CRS competente controla las formas de cumplimiento. Pero
        hay excepciones: por ejemplo, **el CCP Buin supervisa la remisión condicional de Buin,
        Paine e Isla de Maipo**, aunque esas comunas dependan de dos CRS distintos.

        Este formulario es para esas excepciones. Una forma por aporte; las comunas que
        quieras.

  - type: dropdown
    id: forma
    attributes:
      label: ¿Qué forma de cumplimiento?
      options:
%s
    validations:
      required: true

  - type: dropdown
    id: establecimiento
    attributes:
      label: ¿Qué establecimiento la controla?
      description: Escribe las primeras letras para saltar en la lista (por ejemplo «CCP B»).
      options:
%s
    validations:
      required: true

  - type: textarea
    id: comunas
    attributes:
      label: ¿En qué comunas?
      description: Una por línea. Con el nombre basta; el código se resuelve solo.
      placeholder: |
        Buin
        Paine
        Isla de Maipo
    validations:
      required: true

  - type: dropdown
    id: como
    attributes:
      label: ¿Cómo lo sabes?
      options:
        - "Me lo confirmó el establecimiento (llamada o correo)"
        - "Aparece en un documento oficial de Gendarmería"
        - "Lo sé por causas que tramito habitualmente"
        - "Me lo informó otro tribunal"
        - "Otro (lo explico abajo)"
    validations:
      required: true

  - type: input
    id: detalle
    attributes:
      label: Detalle de la fuente
      placeholder: "Oficio de respuesta del CCP Buin, 10-08-2026."
    validations:
      required: true

  - type: textarea
    id: nota
    attributes:
      label: Algo más que convenga saber (opcional)
      placeholder: "Solo para sentenciados con domicilio en esas comunas; las demás formas siguen en el CRS."

  - type: checkboxes
    id: sin_datos_personales
    attributes:
      label: Confirmación
      options:
        - label: "No incluí nombres, RUT ni teléfonos personales de nadie."
          required: true
''' % (lista_formas_desplegable, lista_controladores)
    return {
        '.github/ISSUE_TEMPLATE/01-formas-de-cumplimiento.yml': formulario_formas,
        '.github/ISSUE_TEMPLATE/02-correccion-de-jurisdiccion.yml': formulario_jur,
        '.github/ISSUE_TEMPLATE/04-control-por-forma.yml': formulario_control,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--comprobar', action='store_true',
                   help='no escribe: falla si los formularios quedaron atrasados')
    args = p.parse_args()

    desfasados = []
    for ruta, contenido in construir().items():
        completa = os.path.join(RAIZ, ruta)
        actual = io.open(completa, encoding='utf-8').read() if os.path.isfile(completa) else None
        if actual == contenido:
            continue
        if args.comprobar:
            desfasados.append(ruta)
        else:
            io.open(completa, 'w', encoding='utf-8', newline='\n').write(contenido)
            print('actualizado %s' % ruta)

    if desfasados:
        print('Estos formularios no reflejan los datos actuales:')
        for r in desfasados:
            print('  - %s' % r)
        print('\nCorre: python herramientas/generar_formularios.py')
        sys.exit(1)

    print('Los formularios están al día.' if args.comprobar else 'Listo.')


if __name__ == '__main__':
    main()
