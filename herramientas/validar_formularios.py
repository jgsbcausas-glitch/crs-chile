#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba que los formularios de aporte sean YAML válido y cumplan lo que
GitHub exige de un «issue form».

Existe por un error que costó caro: un texto sin comillas que llevaba dos
puntos —«vale tanto como el anterior: evita derivaciones»— hacía que GitHub
descartara el formulario ENTERO, y sin decir nada. Los otros dos aparecían, ese
no, y desde fuera parecía que el repositorio estaba bien. El colega abría el
enlace, se encontraba un issue en blanco y se iba.

Fallar en silencio es lo peor que puede hacer una herramienta de colaboración.

    python herramientas/validar_formularios.py

Con PyYAML hace la revisión completa. Sin él —el proxy del tribunal impide
instalarlo— hace una revisión mínima que igual atrapa ese error; la completa
corre en CI.
"""
import glob
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMULARIOS = os.path.join(RAIZ, '.github/ISSUE_TEMPLATE/*.yml')
TIPOS = ('markdown', 'input', 'textarea', 'dropdown', 'checkboxes')

for flujo in (sys.stdout, sys.stderr):
    if hasattr(flujo, 'reconfigure'):
        flujo.reconfigure(encoding='utf-8', errors='replace')


def revision_minima():
    """
    Lo que se puede comprobar sin analizador de YAML: tabulaciones y textos sin
    comillas con dos puntos, que es exactamente lo que rompió el formulario.
    """
    malos = []
    for ruta in sorted(glob.glob(FORMULARIOS)):
        texto = io.open(ruta, encoding='utf-8').read()
        for n, linea in enumerate(texto.split('\n'), 1):
            if '\t' in linea:
                malos.append((ruta, n, 'tiene una tabulación; YAML no las admite'))
            m = re.match(r'^\s*(?:- )?([a-z_]+):\s+(.*)$', linea)
            if not m:
                continue
            valor = m.group(2).strip()
            if not valor or valor[0] in '"\'|>[{#&*!':
                continue
            if re.search(r':\s', valor):
                malos.append((ruta, n,
                              'el texto de «%s» lleva dos puntos y no está entre comillas'
                              % m.group(1)))
    return malos


def informar(fallas, cierre):
    for ruta, n, texto in fallas:
        print('REPARO  %s:%s  %s' % (os.path.basename(ruta), n, texto))
    if fallas:
        print('\n%d reparo(s). GitHub descartaría el formulario sin avisar.' % len(fallas))
        sys.exit(1)
    print(cierre)
    sys.exit(0)


try:
    import yaml
except ImportError:
    print('AVISO: falta PyYAML; hago la revisión mínima (en CI se hace la completa).\n')
    informar(revision_minima(), 'Sin problemas evidentes de sintaxis.')


# ------------------------------------------------------- Revisión completa

fallas = []

for ruta in sorted(glob.glob(FORMULARIOS)):
    nombre = os.path.basename(ruta)
    try:
        d = yaml.safe_load(io.open(ruta, encoding='utf-8').read())
    except yaml.YAMLError as e:
        # Acá cae el caso que motivó todo esto.
        fallas.append((ruta, '-', 'no es YAML válido: %s' % str(e).replace('\n', ' ')[:180]))
        continue

    if nombre == 'config.yml':
        if not isinstance(d, dict):
            fallas.append((ruta, '-', 'debería ser un mapa de opciones'))
        else:
            print('%-40s opciones del selector — bien' % nombre)
        continue

    if not isinstance(d, dict):
        fallas.append((ruta, '-', 'el archivo no define un formulario'))
        continue
    for clave in ('name', 'description', 'body'):
        if not d.get(clave):
            fallas.append((ruta, '-', 'falta «%s», que GitHub exige' % clave))
    if not isinstance(d.get('body'), list):
        continue

    ids = []
    for i, b in enumerate(d['body'], 1):
        if not isinstance(b, dict):
            fallas.append((ruta, i, 'el bloque no es un mapa'))
            continue
        t = b.get('type')
        a = b.get('attributes') or {}
        donde = 'bloque %d (%s)' % (i, t)

        if t not in TIPOS:
            fallas.append((ruta, i, '%s: tipo desconocido' % donde))
        if t != 'markdown':
            if not b.get('id'):
                fallas.append((ruta, i, '%s: sin id' % donde))
            else:
                ids.append(b['id'])
            if not a.get('label'):
                fallas.append((ruta, i, '%s: sin label' % donde))
        if t == 'dropdown':
            ops = a.get('options')
            if not ops:
                fallas.append((ruta, i, '%s: sin opciones' % donde))
            elif any(not isinstance(o, str) for o in ops):
                fallas.append((ruta, i, '%s: hay opciones que no son texto' % donde))
            elif len(ops) != len(set(ops)):
                fallas.append((ruta, i, '%s: opciones repetidas' % donde))
        if t == 'checkboxes':
            ops = a.get('options')
            if not ops:
                fallas.append((ruta, i, '%s: sin casillas' % donde))
            elif any(not isinstance(o, dict) or not o.get('label') for o in ops):
                fallas.append((ruta, i, '%s: hay casillas sin label' % donde))

    repetidos = sorted({x for x in ids if ids.count(x) > 1})
    if repetidos:
        fallas.append((ruta, '-', 'ids repetidos: %s' % ', '.join(repetidos)))

    if not fallas:
        print('%-40s %d bloque(s), %d campo(s) — bien' % (nombre, len(d['body']), len(ids)))

print()
informar(fallas, 'Los formularios son válidos.')
