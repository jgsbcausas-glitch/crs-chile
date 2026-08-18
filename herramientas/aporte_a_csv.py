#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte un aporte aprobado (un issue llenado con el formulario) en filas del
CSV correspondiente.

Es la pieza que hace que nadie tenga que saber git para colaborar: el colega
llena un formulario, quien mantiene el repo revisa y pone la etiqueta
«aprobado», y esto escribe la fila. Lo corre el workflow `aporte.yml`, pero
también sirve a mano:

    python herramientas/aporte_a_csv.py --cuerpo issue.txt --autor jperez --numero 42

GitHub entrega el cuerpo de un formulario como markdown predecible: un `### `
por cada campo y debajo su valor, con `- [X]` en las casillas marcadas. Eso es
lo único que se parsea acá.
"""
import argparse
import csv
import io
import os
import re
import sys
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# La consola de Windows llega en cp1252 y revienta con un acento o una flecha.
# Los datos son en español: la salida tiene que poder escribirlos.
for flujo in (sys.stdout, sys.stderr):
    if hasattr(flujo, 'reconfigure'):
        flujo.reconfigure(encoding='utf-8', errors='replace')


def leer_csv(ruta):
    with io.open(os.path.join(RAIZ, ruta), encoding='utf-8-sig', newline='') as f:
        lector = csv.DictReader(f, delimiter=';')
        return list(lector), lector.fieldnames


def escribir_csv(ruta, cabecera, filas):
    with io.open(os.path.join(RAIZ, ruta), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, cabecera, delimiter=';', lineterminator='\n', extrasaction='ignore')
        w.writeheader()
        w.writerows(filas)


def secciones(cuerpo):
    """{'título del campo': 'valor'} a partir del markdown del formulario."""
    out, actual, buffer = {}, None, []
    for linea in cuerpo.replace('\r\n', '\n').split('\n'):
        if linea.startswith('### '):
            if actual:
                out[actual] = '\n'.join(buffer).strip()
            actual, buffer = linea[4:].strip(), []
        elif actual:
            buffer.append(linea)
    if actual:
        out[actual] = '\n'.join(buffer).strip()
    return out


def marcadas(texto):
    """Las opciones con la casilla puesta, tal como las escribió el formulario."""
    return [m.strip() for m in re.findall(r'^\s*-\s*\[[xX]\]\s*(.+?)\s*$', texto or '', re.M)]


def sin_responder(v):
    return not v or v.strip() in ('', '_No response_', '_Sin respuesta_')


def clave_por_nombre(filas, campo_clave, campo_nombre, nombre):
    for f in filas:
        if f[campo_nombre].strip().lower() == (nombre or '').strip().lower():
            return f[campo_clave]
    return None


def formas_de_cumplimiento(campos, autor):
    crs_filas, _ = leer_csv('datos/crs.csv')
    formas_filas, _ = leer_csv('vocabulario/formas.csv')

    crs = clave_por_nombre(crs_filas, 'crs', 'nombre', campos.get('¿Qué CRS?'))
    if not crs:
        sys.exit('No reconocí el CRS «%s».' % campos.get('¿Qué CRS?'))

    def claves(titulo):
        out = []
        for nombre in marcadas(campos.get(titulo, '')):
            k = clave_por_nombre(formas_filas, 'forma', 'nombre', nombre)
            if not k:
                sys.exit('No reconocí la forma «%s».' % nombre)
            out.append(k)
        return out

    controla = claves('Formas de cumplimiento que SÍ controla')
    no_controla = claves('Formas que confirmaste que NO controla')
    if not controla and not no_controla:
        sys.exit('El aporte no marcó ninguna forma: no hay nada que registrar.')

    choque = set(controla) & set(no_controla)
    if choque:
        sys.exit('La misma forma está marcada como sí y como no: %s' % ', '.join(sorted(choque)))

    fuente = ' — '.join(x for x in [
        (campos.get('¿Cómo lo sabes?') or '').strip(),
        (campos.get('Detalle de la fuente') or '').strip(),
    ] if x and not sin_responder(x))
    nota = campos.get('Algo más que convenga saber (opcional)', '')
    nota = '' if sin_responder(nota) else nota.replace('\n', ' ').strip()

    filas, cabecera = leer_csv('datos/crs_formas.csv')
    indice = {(f['crs'], f['forma']): f for f in filas}
    nuevas, cambiadas = 0, 0

    for forma, valor in [(f, 'si') for f in controla] + [(f, 'no') for f in no_controla]:
        fila = {
            'crs': crs, 'forma': forma, 'controla': valor, 'fuente': fuente,
            'aportado_por': autor, 'fecha': date.today().isoformat(), 'nota': nota,
        }
        if (crs, forma) in indice:
            # Ya había un dato: se reemplaza y el pull request muestra el cambio,
            # que es donde corresponde discutirlo si dos colegas discrepan.
            indice[(crs, forma)].update(fila)
            cambiadas += 1
        else:
            filas.append(fila)
            indice[(crs, forma)] = fila
            nuevas += 1

    filas.sort(key=lambda f: (f['crs'], f['forma']))
    escribir_csv('datos/crs_formas.csv', cabecera, filas)

    nombre_crs = campos.get('¿Qué CRS?')

    return (
        '%s: %d forma(s) nueva(s) y %d actualizada(s)' % (nombre_crs, nuevas, cambiadas),
        '[FORMAS] %s' % nombre_crs,
    )


def jurisdiccion(campos, autor):
    comunas, _ = leer_csv('datos/comunas.csv')
    crs_filas, _ = leer_csv('datos/crs.csv')

    nombre_comuna = (campos.get('Comuna') or '').strip()
    cut = clave_por_nombre(comunas, 'cut', 'comuna', nombre_comuna)
    if not cut:
        sys.exit('No reconocí la comuna «%s».' % nombre_comuna)
    crs = clave_por_nombre(crs_filas, 'crs', 'nombre', campos.get('CRS que la atiende'))
    if not crs:
        sys.exit('No reconocí el CRS «%s».' % campos.get('CRS que la atiende'))

    filas, cabecera = leer_csv('datos/crs_jurisdiccion.csv')
    detalle = (campos.get('¿Cómo lo sabes?') or '').replace('\n', ' ').strip()
    antes = None
    for f in filas:
        if f['cut'] == cut:
            antes = f['crs']
            f.update({
                'crs': crs,
                # `manual` es lo que distingue una corrección del tribunal de lo
                # publicado, y lo que impide que la próxima carga oficial la pise.
                'origen': 'manual',
                'confianza': 'alta',
                'fuente': 'aporte de @%s' % autor,
                'nota': detalle,
            })
            break
    else:
        filas.append({'cut': cut, 'comuna': nombre_comuna, 'crs': crs, 'origen': 'manual',
                      'confianza': 'alta', 'fuente': 'aporte de @%s' % autor, 'nota': detalle})

    filas.sort(key=lambda f: f['cut'])
    escribir_csv('datos/crs_jurisdiccion.csv', cabecera, filas)

    return (
        '%s pasa de %s a %s' % (nombre_comuna, antes or 'sin CRS', crs),
        '[JURISDICCIÓN] %s → %s' % (nombre_comuna, campos.get('CRS que la atiende')),
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cuerpo', required=True, help='archivo con el cuerpo del issue')
    p.add_argument('--autor', required=True, help='usuario de GitHub que aportó')
    p.add_argument('--numero', required=True, help='número del issue')
    p.add_argument('--tipo', choices=['formas', 'jurisdiccion'], help='si no se da, se deduce')
    args = p.parse_args()

    with io.open(args.cuerpo, encoding='utf-8') as f:
        campos = secciones(f.read())

    tipo = args.tipo or ('formas' if '¿Qué CRS?' in campos else
                         'jurisdiccion' if 'CRS que la atiende' in campos else None)
    if not tipo:
        sys.exit('El issue no tiene la forma de ninguno de los formularios conocidos.')

    resumen, titulo = formas_de_cumplimiento(campos, args.autor) if tipo == 'formas' \
        else jurisdiccion(campos, args.autor)

    print('Aporte #%s de @%s → %s' % (args.numero, args.autor, resumen))
    # El workflow los usa para el título del pull request y para renombrar
    # el issue: GitHub no puede armar un título desde un desplegable, así
    # que todos llegan como «[FORMAS]» a secas y no hay cómo distinguirlos.
    if os.environ.get('GITHUB_OUTPUT'):
        with io.open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write('resumen=%s\n' % resumen)
            f.write('titulo=%s\n' % titulo)
            f.write('tipo=%s\n' % tipo)


if __name__ == '__main__':
    main()
