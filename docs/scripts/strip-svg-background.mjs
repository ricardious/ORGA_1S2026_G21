/**
 * Quita el fondo opaco de los SVG de `public/`.
 *
 * Tanto schemdraw (vía matplotlib) como los generadores escritos a mano pintan
 * un rectángulo blanco que cubre todo el lienzo. En la página eso se nota:
 * en modo oscuro el CSS invierte los SVG, el blanco se vuelve negro y el
 * diagrama queda dentro de una caja que no coincide con el fondo.
 *
 * Los diagramas deben verse directamente sobre el fondo de la página, así que
 * ese rectángulo se elimina aquí. Se hace en el proyecto y no en cada script de
 * dibujo porque los scripts viven fuera del repositorio: si mañana se regenera
 * cualquier figura, este paso vuelve a limpiarla sin que haya que acordarse.
 *
 * Se ejecuta antes de svgo, así que tiene que reconocer las dos formas: la que
 * sale del generador y la que queda después de optimizar.
 */

import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("../public", import.meta.url).pathname;

const PATTERNS = [
  // Rectángulo a lienzo completo de los generadores propios, antes y después
  // de que svgo abrevie el color.
  /<rect(?=[^>]*\bwidth="100%")(?=[^>]*\bheight="100%")(?=[^>]*\bfill="(?:white|#fff{1,2}(?:fff)?)")[^>]*\/>/gi,
  // Figura de matplotlib recién generada: un grupo con el parche de fondo.
  /<g id="patch_1">\s*<path d="[^"]*"\s*style="fill:\s*#f{3,6}"\s*\/>\s*<\/g>/gi,
  // El mismo parche después de pasar por svgo.
  /<path id="patch_1" d="M0[^"]*"\s*style="fill:#f{3,6}"\s*\/>/gi,
];

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

let changed = 0;
const touched = [];

for (const file of walk(ROOT).filter((f) => f.endsWith(".svg"))) {
  const original = readFileSync(file, "utf8");
  let output = original;
  for (const pattern of PATTERNS) output = output.replace(pattern, "");
  if (output !== original) {
    writeFileSync(file, output);
    changed++;
    touched.push(file.slice(ROOT.length + 1));
  }
}

if (changed === 0) {
  console.log("Fondos SVG: nada que quitar.");
} else {
  console.log(`Fondos SVG quitados en ${changed} archivo(s):`);
  for (const name of touched) console.log(`  ${name}`);
}
