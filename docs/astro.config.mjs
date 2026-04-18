// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { ion } from "starlight-ion-theme";

const githubPagesSite = "https://ricardious.github.io";
const githubPagesBase = "/ORGA_1S2026_G21";

function prefixBaseForRootRelativeUrls(base) {
  /**
   * @param {import('hast').Root | import('hast').Element} node
   */
  function visit(node) {
    if ("children" in node && Array.isArray(node.children)) {
      for (const child of node.children) {
        if (child && typeof child === "object") {
          visit(child);
        }
      }
    }

    if (node.type !== "element" || !node.properties) return;

    for (const attribute of ["href", "src"]) {
      const value = node.properties[attribute];
      if (typeof value !== "string") continue;
      if (!value.startsWith("/") || value.startsWith("//")) continue;
      if (value === base || value.startsWith(`${base}/`)) continue;
      node.properties[attribute] = value === "/" ? `${base}/` : `${base}${value}`;
    }
  }

  return function rehypePrefixBase() {
    return function transform(tree) {
      visit(tree);
    };
  };
}

// https://astro.build/config
export default defineConfig({
  site: githubPagesSite,
  base: githubPagesBase,
  markdown: {
    rehypePlugins: [prefixBaseForRootRelativeUrls(githubPagesBase)],
  },
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
