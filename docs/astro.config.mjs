// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { ion } from "starlight-ion-theme";

// https://astro.build/config
export default defineConfig({
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
          href: "https://github.com/withastro/starlight",
        },
      ],
      sidebar: [
        {
          label: "Inicio",
          link: "/",
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
          label: "Proyectos",
          autogenerate: { directory: "proyectos" },
        },
        // {
        //   label: "Apuntes",
        //   autogenerate: { directory: "apuntes" },
        // },
      ],
      plugins: [ion()],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
