// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { ion } from "starlight-ion-theme";

const site = "https://ricardious.github.io";
const base = "/ORGA_1S2026_G21";
const repo = "https://github.com/ricardious/ORGA_1S2026_G21";

// https://astro.build/config
export default defineConfig({
  site,
  base,
  integrations: [
    starlight({
      title: "ORGA 1S2026 — Grupo 21",
      description:
        "Documentación final del curso de Organización Computacional: prácticas y proyecto del Grupo 21, Semestre 1 de 2026.",
      locales: {
        root: {
          label: "Español",
          lang: "es",
        },
      },
      favicon: "/favicon.svg",
      lastUpdated: true,
      editLink: {
        baseUrl: `${repo}/edit/main/docs/`,
      },
      head: [
        {
          tag: "meta",
          attrs: {
            property: "og:image",
            content: `${site}${base}/og-image.webp`,
          },
        },
        {
          tag: "meta",
          attrs: { property: "og:image:width", content: "800" },
        },
        {
          tag: "meta",
          attrs: { property: "og:image:height", content: "800" },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:image",
            content: `${site}${base}/og-image.webp`,
          },
        },
      ],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: repo,
        },
      ],
      sidebar: [
        {
          label: "Inicio",
          link: "/",
        },
        {
          label: "Fundamentos",
          autogenerate: { directory: "fundamentos" },
        },
        {
          label: "Calculadoras",
          autogenerate: { directory: "calculadoras" },
        },
        {
          label: "Prácticas",
          items: [
            { label: "Vista general", link: "/practicas/" },
            { label: "Práctica 1", link: "/practicas/practica-1/" },
            { label: "Práctica 2", link: "/practicas/practica-2/" },
            { label: "Práctica 3", link: "/practicas/practica-3/" },
          ],
        },
        {
          label: "Proyecto",
          autogenerate: { directory: "proyectos" },
        },
      ],
      plugins: [ion()],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
