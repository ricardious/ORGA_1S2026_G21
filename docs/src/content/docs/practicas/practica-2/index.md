---
title: "Práctica 2: Lógica Binaria y Combinacional (LogicCalc)"
description: Diseño e implementación de una ALU combinacional (LogicCalc) con operaciones aritméticas, lógicas y comparativas.
---

## Resumen

La práctica 2 consiste en diseñar e implementar un prototipo de calculadora binaria **LogicCalc** basado en lógica combinacional, modelando una **Unidad Aritmética Lógica (ALU)** básica.  
El sistema debe ejecutar operaciones aritméticas y lógicas, incorporar una unidad comparativa y mostrar resultados en displays de 7 segmentos y LEDs, cumpliendo las restricciones del enunciado.

## Fechas clave

- Asignación del proyecto: **07/03/2026**
- Fecha fin de elaboración / entrega: **21/03/2026**
- Fecha de calificación: **21/03/2026**

## Objetivo

### Objetivo general

Diseñar y construir una ALU combinacional funcional (LogicCalc) capaz de ejecutar operaciones aritméticas y lógicas con visualización correcta y validación en simulación y montaje físico.

### Objetivos específicos

- Implementar operaciones aritméticas: suma, resta, multiplicación y potencia.
- Implementar operaciones lógicas: AND, OR, NAND y XNOR.
- Integrar una unidad comparativa que muestre mayor y menor entre operandos.
- Mostrar resultados en displays de 7 segmentos (aritmética/comparación) y LEDs de 4 bits (lógica).
- Desarrollar circuito funcional en Proteus (`.pdsprj`) y construir versión física en protoboard o PCB.

## Requisitos del enunciado

- Implementar ALU combinacional con operaciones aritméticas y lógicas requeridas.
- Integrar unidad comparativa para identificar número mayor y menor.
- Utilizar únicamente componentes permitidos del enunciado.
- Presentar circuito funcional en un solo archivo de Proteus (`.pdsprj`).
- Entregar documentación técnica en PDF en repositorio grupal.
- Construcción física funcional (protoboard o PCB).
- Incluir indicadores visuales de unidad activa (ejemplo del enunciado: azul/arimética, amarillo/lógica).

## Entradas y salidas

### Entradas

- Operando `A` de 4 bits.
- Operando `B` de 4 bits.
- Señales de control `CBA` para seleccionar operación.

### Salidas

- Resultado aritmético/comparativo en displays de 7 segmentos.
- Resultado lógico en 4 LEDs.
- Indicadores LED de unidad activa.

## Diseño lógico/electrónico

### Arquitectura general

El sistema se divide en tres bloques principales:

- **Unidad Aritmética**: suma, resta, multiplicación y potencia.
- **Unidad Lógica**: AND, OR, NAND y XNOR.
- **Unidad Comparativa**: determina mayor/menor entre `A` y `B`.

La selección de operación se realiza con líneas de control `CBA`, y la visualización depende del tipo de operación seleccionada.

### Codificación y tabla de verdad

| C | B | A | Operación |
|---:|---:|---:|---|
| 0 | 0 | 0 | Suma |
| 0 | 0 | 1 | Resta |
| 0 | 1 | 0 | Multiplicación |
| 0 | 1 | 1 | Potencia |
| 1 | 0 | 0 | AND |
| 1 | 0 | 1 | OR |
| 1 | 1 | 0 | NAND |
| 1 | 1 | 1 | XNOR |

### Simplificación lógica

Documentar en esta sección:

- Mapas de Karnaugh por salida/bloque.
- Ecuaciones finales (SOP/POS según aplique).
- Implementación de selectores y rutas de salida.
- Justificación técnica de simplificaciones.

### Implementación por bloques

#### Unidad aritmética

- Suma y resta binaria con manejo de acarreo.
- Soporte de complemento a dos para casos negativos.
- Restricción del enunciado: máximo resultado visualizable **99**.

#### Unidad lógica

- Operaciones bit a bit: AND, OR, NAND, XNOR.
- Salida por 4 LEDs.
- Exclusión mutua con unidad aritmética (solo una visible a la vez).

#### Unidad comparativa

- Muestra número mayor y menor entre `A` y `B`.
- Si `A = B`, mostrar el mismo valor en ambos displays.
- Evaluación acotada a números de **0 a 9** según enunciado.

## Implementación

### Simulación (Proteus)

- Archivo principal: `Práctica 2/G21_S1_2026_P2.pdsprj`
- Capturas de bloques funcionales.
- Validación de casos representativos.

### Montaje físico

- Estrategia de cableado e integración.
- Distribución de componentes (protoboard/PCB).
- Ajustes realizados durante pruebas.

### PCB (si aplica)

- Diseño de placas utilizadas.
- Estado de fabricación y pruebas.

## Pruebas y validación

- Validar las 8 operaciones definidas en la tabla `CBA`.
- Verificar comportamiento de acarreo en operaciones aritméticas.
- Validar casos límite de visualización en display.
- Verificar selección exclusiva entre unidad aritmética y lógica.
- Validar comparación (`A>B`, `A<B`, `A=B`) en bloque comparador.

## Evidencias

- Capturas de simulación.
- Evidencias del montaje físico.
- Diagramas/esquemáticos finales.
- Recursos de apoyo utilizados durante validación.

## Componentes permitidos

| Nombre del componente | Código / Especificación |
|---|---|
| Compuerta AND | `7408` |
| Compuerta OR | `7432` |
| Compuerta NOT | `7404` |
| Compuerta XOR | `7486` |
| Sumador | `7483` / `74283` |
| Comparador | `7485` / `74285` |
| Multiplexor | `74157` |
| Demultiplexor | `74138` |
| Decoder para display | `7447` / `7448` |
| Transistor NPN | `2N2222` |
| Displays | 7 segmentos (ánodo y cátodo común) |
| LEDs | 4 bits para resultados lógicos |

## Presupuesto

| Cantidad | Descripción del componente | Precio unitario (Q) | Subtotal (Q) |
|---:|---|---:|---:|
| 0 | Pendiente | 0.00 | 0.00 |

**Total estimado:** `Q 0.00`

## Entregables oficiales

| Tipo | Descripción |
|---|---|
| Archivo de simulación | Archivo `.pdsprj` funcional en un solo proyecto de Proteus. |
| Documento técnico | PDF con carátula, objetivos, funciones, K-map, diagramas, materiales, presupuesto, roles y conclusiones. |
| Repositorio GitHub | Repositorio `ORGA_1S2026_G#` con carpeta de Práctica 2 y evidencias completas. |
| Diagrama PCB y montaje | Archivos y fotografías del diseño de PCB y montaje en protoboard. |
| Enlace de entrega | Enlace oficial UEDI apuntando al repositorio con todo consolidado. |

## Conclusiones

Redactar conclusiones técnicas sobre:

- Cumplimiento de objetivos de la práctica.
- Hallazgos principales en diseño y validación.
- Diferencias entre lo esperado y lo observado.
- Mejoras recomendadas para una siguiente iteración.
