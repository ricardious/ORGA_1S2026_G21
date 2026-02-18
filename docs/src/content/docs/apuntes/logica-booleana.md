---
title: Lógica booleana
description: Resumen de K-map, SOP/POS, display de cátodo/ánodo común y errores típicos.
---

# Lógica booleana

## K-map

- Usar orden Gray en filas y columnas.
- Agrupar en potencias de 2.
- Priorizar grupos grandes para simplificar.

## SOP y POS

- SOP: suma de productos a partir de minterms.
- POS: producto de sumas a partir de maxterms.
- Verificar equivalencia entre forma canónica y simplificada.

## Cátodo común y ánodo común

- Cátodo común: segmento en alto para encender (según driver).
- Ánodo común: segmento en bajo para encender (según driver).
- Confirmar lógica activa del circuito real antes de cablear.

## Errores típicos

- Confundir numeración de pines del display.
- Omitir resistencias limitadoras de corriente.
- Ignorar niveles lógicos reales de entrada/salida.
- No validar casos de borde en tablas de verdad.

## Entregables y evidencias

- Apunte consolidado: `apuntes/`
- Ejemplos de simplificación: `apuntes/ejercicios/`
- Diagramas de apoyo: `diagramas/`
- Validaciones en simulación: `simulacion/`
