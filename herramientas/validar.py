#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida los datos del repo. Es el control de calidad: corre en cada pull request
y ningún aporte entra si no pasa.

Un repo de datos sin validador termina siendo una planilla compartida con
historial: nadie sabe si la fila que agregó alguien apunta a una comuna que
existe, si el CRS está bien escrito o si la forma de cumplimiento es una que
alguien se inventó. Acá eso se revienta antes de entrar, con el número de línea.

    python herramientas/validar.py

Sale con 0 si todo está bien y con 1 si hay algún reparo.
"""
import csv
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTROLA = ('si', 'no', 'sin_dato')
ORIGENES = ('explicita', 'inferida', 'manual')
CONFIANZAS = ('alta', 'media', 'baja')

# La consola de Windows llega en cp1252 y revienta con un acento.
for flujo in (sys.stdout, sys.stderr):
    if hasattr(flujo, 'reconfigure'):
        flujo.reconfigure(encoding='utf-8', errors='replace')

reparos = []
avisos = []


def reparo(archivo, linea, texto):
    reparos.append('%s:%s  %s' % (archivo, linea, texto))


def aviso(archivo, linea, texto):
    avisos.append('%s:%s  %s' % (archivo, linea, texto))


def leer(ruta):
    """Lee un CSV con ; y devuelve (filas, cabecera). La línea 1 es la cabecera."""
    completa = os.path.join(RAIZ, ruta)
    if not os.path.isfile(completa):
        reparo(ruta, 0, 'no existe')
        return [], []
    with io.open(completa, encoding='utf-8-sig', newline='') as f:
        lector = csv.DictReader(f, delimiter=';')
        return list(lector), (lector.fieldnames or [])


def exige_columnas(ruta, cabecera, esperadas):
    faltan = [c for c in esperadas if c not in cabecera]
    if faltan:
        reparo(ruta, 1, 'faltan columnas: %s' % ', '.join(faltan))
        return False
    return True


# --------------------------------------------------------------- Vocabularios

formas, cab = leer('vocabulario/formas.csv')
exige_columnas('vocabulario/formas.csv', cab, ['forma', 'nombre'])
FORMAS = {f['forma'] for f in formas}

comunas, cab = leer('datos/comunas.csv')
exige_columnas('datos/comunas.csv', cab, ['cut', 'comuna', 'region'])
CUTS = {}
for i, c in enumerate(comunas, start=2):
    if not re.fullmatch(r'\d{5}', c['cut'] or ''):
        reparo('datos/comunas.csv', i, 'el CUT «%s» no son 5 dígitos' % c['cut'])
    if c['cut'] in CUTS:
        reparo('datos/comunas.csv', i, 'CUT repetido: %s' % c['cut'])
    CUTS[c['cut']] = c['comuna']

if len(CUTS) != 346:
    aviso('datos/comunas.csv', 1, 'hay %d comunas y Chile tiene 346' % len(CUTS))

crs, cab = leer('datos/crs.csv')
exige_columnas('datos/crs.csv', cab, ['crs', 'nombre', 'cut_sede'])
CRS = {}
for i, r in enumerate(crs, start=2):
    if not re.fullmatch(r'[a-z0-9-]+', r['crs'] or ''):
        reparo('datos/crs.csv', i, 'la clave «%s» debe ser minúsculas, números y guiones' % r['crs'])
    if r['crs'] in CRS:
        reparo('datos/crs.csv', i, 'clave de CRS repetida: %s' % r['crs'])
    if r['cut_sede'] not in CUTS:
        reparo('datos/crs.csv', i, 'la sede %s no es una comuna conocida' % r['cut_sede'])
    CRS[r['crs']] = r['nombre']

# ------------------------------------------------------------- Jurisdicción

jur, cab = leer('datos/crs_jurisdiccion.csv')
exige_columnas('datos/crs_jurisdiccion.csv', cab, ['cut', 'comuna', 'crs', 'origen'])
asignadas = {}
for i, r in enumerate(jur, start=2):
    if r['cut'] not in CUTS:
        reparo('datos/crs_jurisdiccion.csv', i, 'CUT desconocido: %s' % r['cut'])
    elif CUTS[r['cut']] != r['comuna']:
        # El nombre es para leer; el CUT manda. Si discrepan, alguien se equivocó.
        reparo('datos/crs_jurisdiccion.csv', i,
               'el CUT %s es «%s», no «%s»' % (r['cut'], CUTS[r['cut']], r['comuna']))
    if r['crs'] not in CRS:
        reparo('datos/crs_jurisdiccion.csv', i, 'CRS desconocido: %s' % r['crs'])
    if r['origen'] not in ORIGENES:
        reparo('datos/crs_jurisdiccion.csv', i,
               'origen «%s»: debe ser uno de %s' % (r['origen'], '/'.join(ORIGENES)))
    if r.get('confianza') and r['confianza'] not in CONFIANZAS:
        reparo('datos/crs_jurisdiccion.csv', i, 'confianza «%s»' % r['confianza'])
    if r['cut'] in asignadas:
        reparo('datos/crs_jurisdiccion.csv', i,
               'la comuna %s ya estaba asignada en la línea %d' % (r['comuna'], asignadas[r['cut']]))
    asignadas[r['cut']] = i

# Una comuna sin CRS es un hueco real, no un error de formato: se avisa.
sin_crs = [nombre for cut, nombre in CUTS.items() if cut not in asignadas]
if sin_crs:
    aviso('datos/crs_jurisdiccion.csv', 1,
          '%d comuna(s) sin CRS asignado: %s' % (len(sin_crs), ', '.join(sorted(sin_crs)[:8])))

# ------------------------------------------------- Formas de cumplimiento

RUT = re.compile(r'\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b')
CELULAR = re.compile(r'\b(\+?56)?\s?9\s?\d{4}\s?\d{4}\b')

fmt, cab = leer('datos/crs_formas.csv')
exige_columnas('datos/crs_formas.csv', cab, ['crs', 'forma', 'controla', 'fuente', 'aportado_por', 'fecha'])
vistos = {}
for i, r in enumerate(fmt, start=2):
    if r['crs'] not in CRS:
        reparo('datos/crs_formas.csv', i, 'CRS desconocido: %s' % r['crs'])
    if r['forma'] not in FORMAS:
        reparo('datos/crs_formas.csv', i,
               'forma «%s»: no está en vocabulario/formas.csv' % r['forma'])
    if r['controla'] not in CONTROLA:
        reparo('datos/crs_formas.csv', i,
               'controla «%s»: debe ser %s' % (r['controla'], '/'.join(CONTROLA)))
    if not (r.get('fuente') or '').strip():
        reparo('datos/crs_formas.csv', i, 'falta la fuente: cómo se confirmó el dato')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r.get('fecha') or ''):
        reparo('datos/crs_formas.csv', i, 'la fecha debe ser AAAA-MM-DD')

    clave = (r['crs'], r['forma'])
    if clave in vistos:
        reparo('datos/crs_formas.csv', i,
               'ya hay una fila para %s + %s en la línea %d; corrige esa en vez de agregar otra'
               % (r['crs'], r['forma'], vistos[clave]))
    vistos[clave] = i

# --------------------------------------------- Nada personal, en ningún CSV
#
# Un RUT no tiene por qué aparecer nunca: este repo describe instituciones. Los
# celulares son distintos —Gendarmería publica algunos como contacto oficial de
# un CRS— así que se vigilan solo donde el riesgo es real: el archivo que llenan
# los colegas, donde alguien podría pegar el número de un funcionario.

TODOS = ('datos/comunas.csv', 'datos/crs.csv', 'datos/crs_jurisdiccion.csv',
         'datos/crs_formas.csv', 'datos/establecimientos.csv')

for ruta in TODOS:
    completa = os.path.join(RAIZ, ruta)
    if not os.path.isfile(completa):
        continue
    with io.open(completa, encoding='utf-8-sig') as f:
        for i, linea in enumerate(f, start=1):
            if RUT.search(linea):
                reparo(ruta, i, 'parece haber un RUT: este repo no lleva datos de personas')
            if CELULAR.search(linea) and ruta == 'datos/crs_formas.csv':
                reparo(ruta, i, 'parece haber un celular personal: pon el contacto institucional')

# ------------------------------------------------------------------ Informe

print('comunas %d · CRS %d · jurisdicción %d · formas registradas %d · establecimientos %d'
      % (len(CUTS), len(CRS), len(jur), len(fmt), len(leer('datos/establecimientos.csv')[0])))

for a in avisos:
    print('AVISO   %s' % a)
for r in reparos:
    print('REPARO  %s' % r)

if reparos:
    print('\n%d reparo(s): el aporte no puede entrar así.' % len(reparos))
    sys.exit(1)

print('\nTodo en orden.')
