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
          ],
        },
        {
          label: "Proyectos",
          autogenerate: { directory: "proyectos" },
        },
        {
          label: "Simulaciones",
          autogenerate: { directory: "simulaciones" },
        },
        {
          label: "PCB y esquemáticos",
          autogenerate: { directory: "pcb" },
        },
        {
          label: "Evidencias",
          autogenerate: { directory: "evidencias" },
        },
        {
          label: "Presupuestos",
          autogenerate: { directory: "presupuestos" },
        },
        {
          label: "Plantillas",
          autogenerate: { directory: "plantillas" },
        },
        {
          label: "Apuntes",
          autogenerate: { directory: "apuntes" },
        },
      ],
      plugins: [ion()],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
