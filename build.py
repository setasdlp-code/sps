#!/usr/bin/env python3
"""Genera el sitio en site/ a partir de contenido/.

Uso:  python3 build.py

Lee:
  contenido/sitio.json             filtros del menú y orden de proyectos por filtro
  contenido/proyectos/<clave>.json un archivo por proyecto
  contenido/bio.html               cuerpo de la página de biografía

Escribe (no editar a mano; se regeneran en cada build):
  site/index.html, site/<filtro>/index.html, site/<proyecto>/index.html, site/bio/index.html,
  site/next-projects.js, site/project-details.js, site/sitemap.xml

Lo demás en site/ (style.css, *.js, assets/) es fuente y se edita directamente.
Solo usa la biblioteca estándar de Python 3.
"""
import hashlib
import html
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
CONTENIDO = os.path.join(RAIZ, 'contenido')
SITE = os.path.join(RAIZ, 'site')


def leer(ruta):
    with open(ruta, encoding='utf-8') as f:
        return f.read()


def escribir(rel, texto):
    ruta = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)


def esc(texto):
    """Escapa texto para HTML (contenido y atributos)."""
    return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def version(rel):
    """Huella corta del archivo, para que el navegador no use una copia vieja."""
    with open(os.path.join(SITE, rel), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def error(msg):
    sys.exit('ERROR: ' + msg)


# ---------------------------------------------------------------- datos

sitio = json.loads(leer(os.path.join(CONTENIDO, 'sitio.json')))
ORDEN = sitio['orden']
FILTROS = sitio['filtros']
CLAVES_FILTRO = [f['clave'] for f in FILTROS]
DOM = sitio['dominio']
NOMBRE = sitio['nombre']

proyectos = {}
for clave in ORDEN['todos']:
    ruta = os.path.join(CONTENIDO, 'proyectos', clave + '.json')
    if not os.path.exists(ruta):
        error(f'"{clave}" está en orden.todos de sitio.json pero no existe {ruta}')
    try:
        proyectos[clave] = json.loads(leer(ruta))
    except json.JSONDecodeError as e:
        error(f'{ruta} no es JSON válido: {e}')
for archivo in os.listdir(os.path.join(CONTENIDO, 'proyectos')):
    if archivo.endswith('.json') and archivo[:-5] not in proyectos:
        print(f'AVISO: contenido/proyectos/{archivo} no está en orden.todos y no se publica')
for filtro, claves in ORDEN.items():
    if filtro not in CLAVES_FILTRO:
        error(f'orden.{filtro} no corresponde a ningún filtro de sitio.json')
    for c in claves:
        if c not in proyectos:
            error(f'orden.{filtro} incluye "{c}", que no está en orden.todos')

V = {f: version(f) for f in ['style.css', 'app.js', 'bio.js', 'common.js', 'grid.js', 'contacto.js']}
CLAVE_FORMULARIO = sitio.get('contacto', {}).get('web3forms_clave', '').strip()


def categorias(clave):
    return [f for f in CLAVES_FILTRO[1:] if clave in ORDEN.get(f, [])]


def imagen(info, sizes, alt, extra):
    a = info['archivo']
    src = f'/assets/optimized/{a}-960.webp' if 960 in info['anchos'] else f'/assets/optimized/{a}-{info["anchos"][0]}.webp'
    srcset = ', '.join(f'/assets/optimized/{a}-{w}.webp {w}w' for w in info['anchos'])
    alt_attr = f' alt="{esc(alt)}"' if alt is not None else ''
    return f'<img src="{src}" srcset="{srcset}" sizes="{sizes}" width="{info["ancho"]}" height="{info["alto"]}"{alt_attr}{extra}>'


SIZES_GRANDE = '(max-width:620px) calc(100vw - 40px), (max-width:900px) calc(100vw - 64px), 900px'


def atributos_siguiente(info):
    """Atributos de la imagen de 'Siguiente proyecto' (los usa common.js)."""
    return imagen(info, SIZES_GRANDE, None, '')[5:-1]


# ---------------------------------------------------------------- piezas comunes

def cabeza(titulo, descripcion, url, img_url, img_alt):
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{esc(descripcion)}"><meta name="theme-color" content="#0e0e0e">'
        f'<title>{esc(titulo)}</title>'
        '<link rel="preload" href="/assets/fonts/space-grotesk-400.ttf" as="font" type="font/ttf" crossorigin>'
        '<link rel="preload" href="/assets/fonts/dm-sans-400.ttf" as="font" type="font/ttf" crossorigin>'
        f'<link rel="stylesheet" href="/style.css?v={V["style.css"]}"><link rel="canonical" href="{url}">'
        '<meta property="og:type" content="website"><meta property="og:locale" content="es_CO">'
        f'<meta property="og:site_name" content="{esc(NOMBRE)}"><meta property="og:title" content="{esc(titulo)}">'
        f'<meta property="og:description" content="{esc(descripcion)}"><meta property="og:url" content="{url}">'
        f'<meta property="og:image" content="{img_url}"><meta property="og:image:alt" content="{esc(img_alt)}">'
        '<meta name="twitter:card" content="summary_large_image"></head>'
    )


def menu(actual=None, con_filtros=True):
    enlaces = []
    for f in FILTROS:
        cur = ' aria-current="page"' if f['clave'] == actual else ''
        df = f' data-filter="{f["clave"]}"' if con_filtros else ''
        enlaces.append(f'<a href="{f["ruta"]}"{cur}{df}>{esc(f["nombre"])}</a>')
    cur = ' aria-current="page"' if actual == 'bio' else ''
    enlaces.append(f'<a href="/bio/"{cur}>Biografía</a>')
    if CLAVE_FORMULARIO:
        cur = ' aria-current="page"' if actual == 'contacto' else ''
        enlaces.append(f'<a href="/contacto/"{cur}>Contacto</a>')
    etiqueta = f' aria-label="{esc(NOMBRE)}, inicio"' if actual in ('bio', 'contacto') else ''
    return (
        '<body><a class="skip" href="#contenido">Saltar al contenido</a><header>'
        '<nav aria-label="Navegación principal">' + ''.join(enlaces) + '</nav>'
        f'<p class="wordmark"><a href="/"{etiqueta}>{esc(NOMBRE)}</a></p></header>'
    )


PIE = (
    f'<footer><a href="/">{esc(NOMBRE)}</a><span>© <span id="year">2026</span></span>'
    '<a href="#contenido">Volver arriba ↑</a></footer>'
)


def scripts_proyecto():
    return (f'<script src="/next-projects.js?v={V_NEXT}"></script>'
            f'<script src="/common.js?v={V["common.js"]}"></script>')


# ---------------------------------------------------------------- ficha de proyecto

def ficha(clave, en_ventana):
    """Cuerpo de la ficha. en_ventana=True produce la versión de la ventana de la portada."""
    p = proyectos[clave]
    h_titulo = 'h2 id="dialog-title"' if en_ventana else 'h1'
    h_cierre = 'h2' if en_ventana else 'h1'
    h_sec = 'h3' if en_ventana else 'h2'
    detalle = p.get('estado') or (str(p['anio']) if p.get('anio') else '')
    tipo = p['tipo'] + (' · ' + detalle if detalle else '')
    part = ''.join(f'<span>{esc(x)}</span>' for x in p['participacion'])
    enlace = f'<a class="project-permalink" href="/{clave}/">Ver ficha completa ↗</a>' if en_ventana else ''
    secciones = []
    for s in p['secciones']:
        clase = 'project-block' + (' ' + s['clase'] if s.get('clase') else '')
        if 'creditos' in s:
            cuerpo = '<dl class="project-credits">' + ''.join(
                f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in s['creditos']) + '</dl>'
            cuerpo += s.get('html_despues', '')
        else:
            cuerpo = s['html']
        secciones.append(f'<section class="{clase}"><{h_sec}>{esc(s["titulo"])}</{h_sec}>'
                         f'<div class="project-block-content">{cuerpo}</div></section>')
    orden = ORDEN['todos']
    sig = orden[(orden.index(clave) + 1) % len(orden)]
    ps = proyectos[sig]
    img_sig = imagen(ps['imagen_siguiente'], SIZES_GRANDE, 'Imagen de ' + ps['titulo'], ' loading="lazy"')
    return (
        f'<section class="project-detail"><div class="project-media">{p["media"]}</div>'
        '<article class="project-editorial"><header class="project-heading">'
        f'<div><p class="project-kicker">{esc(tipo)}</p><{h_titulo} class="project-title">{esc(p["titulo"])}</{h_cierre}></div>'
        f'<aside class="project-participation"><p>Participación</p><div>{part}</div>{enlace}</aside></header>'
        + ''.join(secciones) +
        '</article></section>'
        '<section class="next-project" aria-label="Siguiente proyecto"><p>Siguiente proyecto</p>'
        f'<a class="next-project-link" href="/{sig}/">{img_sig}'
        f'<span class="next-project-caption"><span>{esc(ps["titulo"])}</span><span aria-hidden="true">↗</span></span></a></section>'
    )


def pagina_proyecto(clave):
    p = proyectos[clave]
    soc = p['imagen_social']
    return (
        cabeza(f'{p["titulo"]} — {NOMBRE}', p['descripcion'], f'{DOM}/{clave}/',
               f'{DOM}/assets/optimized/{soc["archivo"]}-{soc["ancho"]}.webp', p['titulo'])
        + menu() + '<main id="contenido">' + ficha(clave, False) + '</main>' + PIE
        + scripts_proyecto() + '</body></html>'
    )


# ---------------------------------------------------------------- cuadrícula

def rol_tarjeta(p):
    return (f'{p["anio"]} · ' if p.get('anio') and not p.get('estado') else '') + p['rol']


def tarjeta(clave, filtro, primera):
    p = proyectos[clave]
    cats = categorias(clave)
    rangos = ''.join(
        f' data-rank-{f}="{ORDEN[f].index(clave) if clave in ORDEN.get(f, []) else 99}"' for f in CLAVES_FILTRO)
    oculta = filtro != 'todos' and clave not in ORDEN.get(filtro, [])
    film = f' data-film="{clave}"' if p.get('ventana') else ''
    if primera:
        img = imagen(p['imagen_tarjeta'], '(max-width:620px) calc(100vw - 40px), (max-width:900px) 60vw, 720px',
                     'Fotograma de ' + p['titulo'], ' fetchpriority="high"')
    else:
        img = imagen(p['imagen_tarjeta'], '(max-width:620px) 50vw, (max-width:900px) 50vw, 600px',
                     'Fotograma de ' + p['titulo'], ' loading="lazy"')
    estado = f'<p class="tile-status">{esc(p["estado"])}</p>' if p.get('estado') else ''
    return (
        f'<a class="project-tile" href="/{clave}/" data-key="{clave}" data-categories="{" ".join(cats)}"{rangos}{film}'
        f'{" hidden" if oculta else ""}>{img}<div class="tile-caption">{estado}<p>{esc(rol_tarjeta(p))}</p>'
        f'<h2>{esc(p["titulo"])}</h2><span aria-hidden="true">↗</span></div></a>'
    )


def pagina_cuadricula(f):
    clave_f = f['clave']
    visibles = ORDEN['todos'] if clave_f == 'todos' else ORDEN.get(clave_f, [])
    resto = [c for c in ORDEN['todos'] if c not in visibles]
    tarjetas = ''.join(tarjeta(c, clave_f, i == 0) for i, c in enumerate(visibles + resto))
    n = len(visibles)
    titulo = ('Portafolio' if clave_f == 'todos' else f['nombre']) + ' — ' + NOMBRE
    url = DOM + ('/' if clave_f == 'todos' else f['ruta'])
    soc = sitio['imagen_social']
    return (
        cabeza(titulo, sitio['descripcion'], url, f'{DOM}/assets/optimized/{soc["archivo"]}-{soc["ancho_max"]}.webp', soc['alt'])
        + menu(clave_f) +
        '<main id="contenido"><section class="portfolio" aria-labelledby="portfolio-title">'
        f'<h1 id="portfolio-title" class="sr-only">Proyectos de {esc(NOMBRE)}</h1>'
        f'<p class="grid-count sr-only" role="status" aria-live="polite">{n} proyecto{"" if n == 1 else "s"}</p>'
        f'<div class="project-mosaic" data-initial-filter="{clave_f}" data-visible-count="{n}">{tarjetas}</div>'
        '</section></main>' + PIE + scripts_proyecto() +
        '<dialog id="film-dialog" aria-labelledby="dialog-title"><div class="film-toolbar"><span>Películas</span>'
        '<button class="close" aria-label="Cerrar película">Cerrar ×</button></div><div id="dialog-body"></div></dialog>'
        f'<script src="/project-details.js?v={V_DETALLES}"></script>'
        f'<script src="/app.js?v={V["app.js"]}"></script><script src="/grid.js?v={V["grid.js"]}"></script></body></html>'
    )


def pagina_bio():
    soc = sitio['imagen_social']
    desc = 'Biografía de Sebastián Pinzón Silva, documentalista colombiano, director de fotografía y editor.'
    return (
        cabeza('Biografía — ' + NOMBRE, desc, DOM + '/bio/',
               f'{DOM}/assets/optimized/{soc["archivo"]}-{soc["ancho_max"]}.webp', soc['alt'])
        + menu('bio', con_filtros=False)
        + '<main id="contenido" class="bio-page">' + leer(os.path.join(CONTENIDO, 'bio.html')).rstrip('\n') + '</main>'
        + PIE + f'<script src="/bio.js?v={V["bio.js"]}"></script></body></html>'
    )


def pagina_contacto():
    soc = sitio['imagen_social']
    desc = 'Escríbele a Sebastián Pinzón Silva.'
    cuerpo = (
        '<section class="bio-layout contact-layout" aria-labelledby="contact-heading">'
        '<div class="bio-side"><h1 id="contact-heading">Contacto</h1></div>'
        '<div class="bio-main">'
        '<p class="bio-lead">Escríbeme para proyectos, proyecciones o colaboraciones.</p>'
        '<form class="contact-form" action="https://api.web3forms.com/submit" method="POST">'
        f'<input type="hidden" name="access_key" value="{esc(CLAVE_FORMULARIO)}">'
        '<input type="hidden" name="subject" value="Mensaje desde sebastianpinzon.com">'
        '<input type="hidden" name="from_name" value="sebastianpinzon.com">'
        f'<input type="hidden" name="redirect" value="{DOM}/contacto/?enviado=1">'
        '<input type="checkbox" name="botcheck" class="contact-trap" tabindex="-1" autocomplete="off" aria-hidden="true">'
        '<label>Nombre<input type="text" name="name" autocomplete="name" required maxlength="200"></label>'
        '<label>Correo<input type="email" name="email" autocomplete="email" required maxlength="200"></label>'
        '<label>Mensaje<textarea name="message" rows="7" required maxlength="5000"></textarea></label>'
        '<button type="submit">Enviar <span aria-hidden="true">↗</span></button>'
        '<p class="contact-status" role="status" aria-live="polite"></p>'
        '</form></div></section>'
    )
    return (
        cabeza('Contacto — ' + NOMBRE, desc, DOM + '/contacto/',
               f'{DOM}/assets/optimized/{soc["archivo"]}-{soc["ancho_max"]}.webp', soc['alt'])
        + menu('contacto', con_filtros=False)
        + '<main id="contenido" class="bio-page">' + cuerpo + '</main>'
        + PIE + f'<script src="/contacto.js?v={V["contacto.js"]}"></script></body></html>'
    )


# ---------------------------------------------------------------- escribir

catalogo = {c: {'title': p['titulo'], 'imageAttributes': atributos_siguiente(p['imagen_siguiente'])}
            for c, p in proyectos.items()}
escribir('next-projects.js',
         'const projectCatalogue = ' + json.dumps(catalogo, ensure_ascii=False) + ';\n'
         'const projectOrders = ' + json.dumps(ORDEN, ensure_ascii=False) + ';\n')
detalles = {c: ficha(c, True) for c, p in proyectos.items() if p.get('ventana')}
escribir('project-details.js', 'const projectDetails = ' + json.dumps(detalles, ensure_ascii=False) + ';\n')
V_NEXT = version('next-projects.js')
V_DETALLES = version('project-details.js')

rutas = ['/']
for f in FILTROS:
    if f['clave'] == 'todos':
        escribir('index.html', pagina_cuadricula(f))
    elif f.get('pagina'):
        escribir(f['pagina'] + '/index.html', pagina_cuadricula(f))
        rutas.append(f'/{f["pagina"]}/')
for c in proyectos:
    escribir(c + '/index.html', pagina_proyecto(c))
escribir('bio/index.html', pagina_bio())
if CLAVE_FORMULARIO:
    escribir('contacto/index.html', pagina_contacto())
else:
    print('AVISO: contenido/sitio.json no tiene contacto.web3forms_clave; no se publica /contacto/')
rutas = ['/', '/bio/'] + [f'/{c}/' for c in proyectos] + rutas[1:] + (['/contacto/'] if CLAVE_FORMULARIO else [])
escribir('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
         + ''.join(f'<url><loc>{DOM}{r}</loc></url>' for r in rutas) + '</urlset>\n')
print(f'Sitio generado en site/: {len(proyectos)} proyectos, {len(rutas)} páginas.')
