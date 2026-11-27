# CLAUDE.md

Portafolio estático de Sebastián Pinzón Silva (sebastianpinzon.com). Leer `README.md` primero.

- El contenido se edita en `contenido/`. Nunca editar los archivos que genera `build.py` (listados en `.gitignore`).
- Después de cualquier cambio: `python3 build.py`, servir `site/` con `python3 -m http.server` y revisar en el navegador las páginas afectadas (portada, filtros, ficha y ventana de la ficha) en escritorio y móvil.
- Créditos: solo con fuente. La fuente puede ser el usuario o un documento suyo (por ejemplo, créditos finales o lista de personal). No completar créditos desde la web ni desde Jarana Cine: allí hay datos desactualizados.
- `build.py` usa solo la biblioteca estándar de Python. No agregar dependencias ni pasos de build adicionales: Cloudflare Workers corre `python3 build.py` y luego `npx wrangler deploy`, que publica `site/` según `wrangler.jsonc`.
