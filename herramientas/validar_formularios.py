#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba que los formularios de aporte sean YAML válido y cumplan lo que
GitHub exige de un «issue form».

Existe por un error que costó caro: un texto sin comillas que llevaba dos
puntos —«vale tanto como el anterior: evita derivaciones»— hacía que GitHub
descartara el formulario ENTERO, y sin decir nada. Los otros dos aparecían, ese
no, y desde fuera parecía que el repositorio estaba bien.

Falla en silencio es lo peor que puede hacer una herramienta de colaboración:
el colega abre el enlace, ve un issue en blanco y se va.

    python herramientas/validar_formularios.py

Necesita PyYAML. En CI se instala solo; en una máquina sin salida a internet
este control se salta con aviso, y el de CI lo cubre igual.
"""
import glob
import io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for flujo in (sys.stdout, sys.stderr):
    if hasattr(flujo, 'reconfigure'):
        flujo.reconfigure(encoding='utf-8', errors='replace')

try:
    import yaml
except ImportError:
    print('AVISO: falta PyYAML, no se pudo revisar la sintaxis de los formularios.')
    print('       Instálalo con «pip install pyyaml»; en CI ya está.')
    sys.exit(0)

TIPOS = ('markdown', 'input', 'textarea', 'dropdown', 'checkboxes')
reparos = []


def reparo(archivo, texto):
    reparos.append('%s  %s' % (os.path.basename(archivo), texto))


for ruta in sorted(glob.glob(os.path.join(RAIZ, '.github/ISSUE_TEMPLATE/*.yml'))):
    nombre = os.path.basename(ruta)
    try:
        d = yaml.safe_load(io.open(ruta, encoding='utf-8').read())
    except yaml.YAMLError as e:
        # Acá cae el caso que motivó todo esto.
        reparo(ruta, 'no es YAML válido: %s' % str(e).replace('\n', ' ')[:200])
        continue

    if nombre == 'config.yml':
        if not isinstance(d, dict):
            reparo(ruta, 'debería ser un mapa de opciones')
        continue

    if not isinstance(d, dict):
        reparo(ruta, 'el archivo no define un formulario')
        continue
    for clave in ('name', 'description', 'body'):
        if not d.get(clave):
            reparo(ruta, 'falta «%s», que GitHub exige' % clave)
    if not isinstance(d.get('body'), list):
        continue

    ids = []
    for i, b in enumerate(d['body'], 1):
        if not isinstance(b, dict):
            reparo(ruta, 'el bloque %d no es un mapa' % i)
            continue
        t = b.get('type')
        a = b.get('attributes') or {}
        donde = 'bloque %d (%s)' % (i, t)

        if t not in TIPOS:
            reparo(ruta, '%s: tipo desconocido' % donde)
        if t != 'markdown':
            if not b.get('id'):
                reparo(ruta, '%s: sin id' % donde)
            else:
                ids.append(b['id'])
            if not a.get('label'):
                reparo(ruta, '%s: sin label' % donde)
        if t == 'dropdown':
            ops = a.get('options')
            if not ops:
                reparo(ruta, '%s: sin opciones' % donde)
            elif any(not isinstance(o, str) for o in ops):
                reparo(ruta, '%s: hay opciones que no son texto' % donde)
            elif len(ops) != len(set(ops)):
                reparo(ruta, '%s: opciones repetidas' % donde)
        if t == 'checkboxes':
            ops = a.get('options')
            if not ops:
                reparo(ruta, '%s: sin casillas' % donde)
            elif any(not isinstance(o, dict) or not o.get('label') for o in ops):
                reparo(ruta, '%s: hay casillas sin label' % donde)

    repetidos = {x for x in ids if ids.count(x) > 1}
    if repetidos:
        reparo(ruta, 'ids repetidos: %s' % ', '.join(sorted(repetidos)))

    print('%-40s %d bloque(s), %d campo(s) — bien' % (nombre, len(d['body']), len(ids)))

if reparos:
    print()
    for r in reparos:
        print('REPARO  %s' % r)
    print('\n%d reparo(s). GitHub descartaría el formulario sin avisar.' % len(reparos))
    sys.exit(1)

print('\nLos formularios son válidos.')
