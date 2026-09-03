# Organización Computacional — 1S2026, Grupo 21

Repositorio del curso de **Organización Computacional** (Universidad de San Carlos de Guatemala, Facultad de Ingeniería, Escuela de Ciencias y Sistemas), Semestre 1 de 2026.

📖 **Documentación publicada: <https://ricardious.github.io/ORGA_1S2026_G21/>**

El curso concluyó. Este repositorio conserva las entregas finales: tres prácticas de lógica digital y un proyecto integrador de sistemas embebidos.

## Entregas

| Entrega | Tema | Fecha |
|---|---|:---:|
| [Práctica 1](Práctica%201/) | Visualización bidireccional en display de 7 segmentos (normal y espejo) | 28/02/2026 |
| [Práctica 2](Práctica%202/) | LogicCalc: ALU combinacional de 4 bits | 21/03/2026 |
| [Práctica 3](Práctica%203/) | Carrusel automatizado con control de acceso seguro | 18/04/2026 |
| [Proyecto](Proyecto/) | Casa inteligente con control de ambientes y ventilador automatizado | 02/05/2026 |

## Estructura

```text
Práctica 1/   Simulación Proteus, esquemas y documento de entrega
Práctica 2/   Simulación Proteus, esquemas y documento de entrega
Práctica 3/   Simulación Proteus, firmware Arduino y documento de entrega
Proyecto/     Firmware Arduino, app de escritorio (Python), app móvil (Flutter),
              simulación Proteus y documentación LaTeX
docs/         Sitio de documentación (Astro + Starlight) publicado en GitHub Pages
```

## Proyecto integrador

El proyecto final es una maqueta domótica controlada por Arduino Uno, con cinco zonas de iluminación, ventilador DC y puerta con servomotor. Las escenas se definen en archivos `.org`, se validan durante la transferencia serial y se persisten en EEPROM en direcciones fijas. Se controla desde una aplicación de escritorio por USB y desde una aplicación móvil por Bluetooth.

Los binarios de la aplicación de escritorio se publican automáticamente en [Releases](https://github.com/ricardious/ORGA_1S2026_G21/releases) al etiquetar una versión.

## Integrantes

| Carné | Integrante |
| --- | --- |
| 202406918 | Claudia Maribel Tigüilá Tecum |
| 202403929 | Emiliana Elizabeth Pú Lara |
| 202300476 | Alex Ricardo Castañeda Rodríguez |
| 201904522 | Byron Manuel Hernández López |
