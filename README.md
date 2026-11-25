# sebastianpinzon.com

Portafolio de Sebastián Pinzón Silva. Sitio estático, sin dependencias. Se publica en Cloudflare Pages.

## Cómo está organizado

```
contenido/                 ← lo que se edita
  sitio.json               menú de filtros y orden de proyectos en cada filtro
  proyectos/<clave>.json   un archivo por proyecto
  bio.html                 texto de la biografía
site/                      ← lo que se publica
  style.css, *.js          diseño y comportamiento (se editan directamente)
  assets/                  imágenes y fuentes
build.py                   genera las páginas HTML de site/ a partir de contenido/
```

`build.py` escribe en `site/` todas las páginas (`index.html`, filtros, proyectos, bio), `next-projects.js`, `project-details.js` y `sitemap.xml`. Esos archivos no están en git (ver `.gitignore`) y no se editan a mano.

## Cambios frecuentes

**Corregir un crédito o un texto de un proyecto:** editar `contenido/proyectos/<clave>.json`.
- `participacion`: tu rol, tal como aparece en la ficha.
- `rol`: el texto corto de la tarjeta en la portada.
- `estado`: por ejemplo `"En curso"`. Si se borra el campo, desaparece la etiqueta.
- `secciones`: bloques de la ficha. Los créditos son una lista de `["Cargo", "Nombres"]`.

**Cambiar en qué filtros aparece un proyecto o su orden:** editar `orden` en `contenido/sitio.json`. Un proyecto aparece en un filtro si su clave está en la lista de ese filtro. El orden de la lista es el orden en pantalla.

**Agregar un proyecto:**
1. Subir sus imágenes a `site/assets/optimized/` en `.webp` y en varios anchos con el mismo nombre base (`nombre-480.webp`, `nombre-960.webp`, `nombre-1600.webp`).
2. Copiar un archivo de `contenido/proyectos/` con la clave nueva (minúsculas y guiones, será la URL) y llenarlo.
3. Agregar la clave a `orden.todos` y a los filtros que correspondan en `contenido/sitio.json`.

**Agregar un filtro:** agregarlo a `filtros` (con `pagina`, que será su URL) y su lista a `orden` en `contenido/sitio.json`.

**Biografía:** editar `contenido/bio.html`.

## Ver el sitio en el computador

```
python3 build.py
cd site && python3 -m http.server 8000
```

y abrir http://localhost:8000.

## Publicar

Cloudflare Pages conectado a este repositorio:

- Build command: `python3 build.py`
- Build output directory: `site`

Cada cambio que llega a `main` se publica solo. Cada rama o pull request recibe una URL de vista previa. Si `build.py` encuentra un error (por ejemplo, una clave en `sitio.json` sin su archivo), el build falla y queda publicada la versión anterior.

El navegador recibe `style.css` y los `.js` con `?v=<huella>`. La huella se calcula en cada build, así que no hay que cambiar versiones a mano.

## Historia

El primer commit es una copia del sitio publicado el 2026-11-25. El generador original no se conservó; `build.py` lo reemplaza y produce el mismo HTML.
