# Sitio de documentación

Sitio estático construido con [Astro](https://astro.build) y [Starlight](https://starlight.astro.build) que publica la documentación final del curso.

🌐 <https://ricardious.github.io/ORGA_1S2026_G21/>

## Desarrollo

```bash
pnpm install
pnpm dev      # servidor local en http://localhost:4321/ORGA_1S2026_G21/
pnpm build    # genera dist/
pnpm preview  # sirve dist/ localmente
```

## Estructura

```text
src/content/docs/   Páginas del sitio (Markdown / MDX)
src/components/     Componentes Astro reutilizables
src/assets/media/   Imágenes de las páginas, optimizadas por Astro en el build
src/styles/         CSS propio
public/svg/         Esquemas vectoriales y GIF/WebP animados, servidos sin procesar
```

## Imágenes

Las imágenes de contenido se referencian con el componente `Figure`, que las resuelve
contra `src/assets/media/` y las optimiza en el build:

```mdx
import Figure from '../../../components/Figure.astro';

<Figure src="practicas/practica-3/montaje/carrusel_maqueta_completa.jpeg"
        alt="Maqueta completa del carrusel"
        caption="Maqueta completa durante las pruebas." />
```

Una ruta inexistente rompe el build con la lista de rutas válidas, en lugar de publicar
una imagen rota. Los SVG y las imágenes animadas viven en `public/svg/` porque no deben
pasar por el optimizador; se referencian con `` `${import.meta.env.BASE_URL}/svg/...` ``.

Para reoptimizar los SVG tras editarlos:

```bash
pnpm optimize:svg
```

## Despliegue

Cada push a `main` que toque `docs/` dispara el workflow
[`deploy.yml`](../.github/workflows/deploy.yml), que construye el sitio y lo publica en
GitHub Pages.
