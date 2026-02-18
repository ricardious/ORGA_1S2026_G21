---
title: Simulaciones
description: Guía general para documentar simulaciones, pruebas y resultados en Proteus.
---

# Simulaciones

Esta sección define cómo registrar simulaciones para asegurar reproducibilidad y revisión técnica.

## Qué documentar en cada simulación

- Objetivo técnico de la simulación.
- Versión de herramientas y librerías.
- Esquema implementado y supuestos.
- Casos de prueba y resultados.
- Limitaciones detectadas.

## Nomenclatura recomendada

- Proyecto: `simulacion_nombre-proyecto_v01.pdsprj`
- Capturas: `sim_<modulo>_<caso>_<fecha>.png`
- Reporte: `simulacion_<tema>_resumen.pdf`

## Flujo de pruebas

1. Definir condiciones iniciales.
2. Ejecutar casos nominales y de borde.
3. Registrar comportamiento esperado vs observado.
4. Guardar evidencias y versión final del archivo.

## Plantilla relacionada

- [Plantilla de simulación Proteus](/simulaciones/proteus/)

## Entregables y evidencias

- Archivo fuente de simulación: `simulaciones/` o `*/simulacion/`
- Capturas y videos: `evidencias/simulaciones/`
- Resumen de resultados: `docs-pdf/`
- Diagramas base: `diagramas/`
