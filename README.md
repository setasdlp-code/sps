# sebastianpinzon.com

Fuente del portafolio publicado en Cloudflare Pages (proyecto `sebastian-pinzon`, Direct Upload).

- `site/` es exactamente lo que se sube: es la raíz del sitio.
- El primer commit es una copia del sitio publicado (descargado el 2026-11-25), porque el script generador original no existe.
- No hay paso de build: el HTML, el CSS y el JS se editan directamente.

## Datos repetidos

Cada proyecto aparece en varios archivos y hay que cambiarlos todos juntos:

- `site/<proyecto>/index.html` — página propia del proyecto
- tarjetas en `site/index.html` y en las páginas de filtro (`fotografia/`, `camara/`, `iluminacion/`, `edicion/`)
- `site/project-details.js` — ficha de la ventana sobre la portada
- `site/films.js` — textos
- `site/next-projects.js` — orden de "siguiente proyecto" y listas por filtro
- `site/sitemap.xml`

Al cambiar un CSS o JS, sube su `?v=` en todos los HTML que lo cargan.

## Publicar

Cloudflare › Workers & Pages › `sebastian-pinzon` › Create deployment › arrastrar la carpeta `site/`.
