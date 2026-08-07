// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { ion } from "starlight-ion-theme";

const site = "https://ricardious.github.io";
const base = "/ORGA_1S2026_G21";

// https://astro.build/config
export default defineConfig({
  site,
  base,
  integrations: [
    starlight({
      title: "ORGA_1S2026_G21",
      locales: {
        root: {
          label: "Español",
          lang: "es",
        },
      },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/ricardious/ORGA_1S2026_G21",
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
