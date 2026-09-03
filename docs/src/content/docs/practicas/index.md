---
title: Prácticas
description: Índice de las tres prácticas del curso, con su tema y fecha de entrega.
---

Tres prácticas de dificultad creciente, cada una documentada desde el planteamiento hasta el montaje funcionando. Si vienes a resolver una parecida, salta directo a la que te toque; si vienes a entender el curso completo, [empieza por lo que nos costó tiempo](#si-vas-a-hacer-estas-prácticas).

## Índice

| Práctica | Tema | Entrega |
|---|---|:---:|
| [Práctica 1](practica-1/) | Visualización bidireccional en display de 7 segmentos (normal y espejo) | 28/02/2026 |
| [Práctica 2](practica-2/) | LogicCalc: ALU combinacional de 4 bits | 21/03/2026 |
| [Práctica 3](practica-3/) | Carrusel automatizado con control de acceso seguro | 18/04/2026 |

## Progresión del curso

Las prácticas avanzan de lógica puramente combinacional hacia sistemas secuenciales con memoria de estado:

- **Práctica 1** parte de tablas de verdad y mapas de Karnaugh para decodificar caracteres en un display de 7 segmentos, resolviendo por separado las variantes de cátodo y ánodo común, y construyendo las compuertas con transistores discretos.
- **Práctica 2** integra varios bloques combinacionales —sumador/restador, multiplicador, potencia, unidad lógica, comparador y conversor binario-BCD— bajo un controlador que selecciona la operación activa.
- **Práctica 3** introduce estado: flip-flops tipo D para memorizar una contraseña, un contador de errores que persiste hasta activar la alarma, y contadores de temporización que gobiernan el giro del motor.

## Si vas a hacer estas prácticas

Lo que sigue es lo que nos costó tiempo a nosotros. Está aquí para que no lo descubras a mitad del montaje.

### Dónde se pierde el tiempo en cada práctica

**Práctica 1 — la trampa está en cátodo vs. ánodo común.** No son el mismo circuito con los LEDs al revés. El cátodo común opera con salidas **activas en alto**, y el ánodo común exige invertir y trabajar en forma **POS, activa en bajo**. Si asumes que basta con negar la salida, vas a rehacer los mapas de Karnaugh. Conviene resolver las dos variantes en paralelo desde el diseño, no una después de la otra.

**Práctica 2 — la integración pesa más que cada bloque.** Los bloques sueltos salen rápido; lo que consume el tiempo es unirlos. En concreto:

- La **resta** exige atención por el manejo de signo y complemento a dos; es donde más fallan las pruebas.
- La **conversión binario a BCD** concentró buena parte del trabajo de integración.
- **Multiplicación y potencia** disparan la complejidad del cableado y de la visualización, no la de la lógica.
- El **comparador** resultó más estable al resolverlo con un bloque dedicado (`74LS85`) en vez de lógica suelta.

**Práctica 3 — separa la lógica de la potencia desde el principio.** El contador de errores y la alarma funcionan sin depender del Arduino, y eso simplifica la depuración: puedes probar el bloque de seguridad sin firmware de por medio. Para arrancar el contador descendente siempre desde 10 hizo falta una NAND de 4 entradas que genera una única señal de carga; sin ella el contador hereda el estado residual de la fase anterior.

### Sobre el montaje físico

El salto de Proteus al protoboard es donde aparecen los problemas que la simulación no muestra:

- **Alimentación estable** para varios TTL en simultáneo: es la causa de fallos intermitentes que parecen errores de lógica.
- **Distribución de integrados** entre varios protoboards, y rutas identificables de un módulo a otro.
- **Ordenamiento de buses** y señales de control antes de cablear, no durante.

Dos recomendaciones que salieron de la Práctica 1 y que aplican a todas: **estandarizar el etiquetado de señales desde el inicio** y **preparar una matriz de pruebas por segmento o por bloque** antes de armar. Depurar sin eso obliga a rastrear el error a mano por todo el circuito.

### Orden de trabajo que funcionó

1. Comprar componentes primero: la disponibilidad condiciona el diseño.
2. Diseñar los bloques funcionales por separado en Proteus.
3. Integrarlos y validar contra la tabla de verdad, bloque por bloque.
4. Montar en físico y documentar con evidencias sobre la marcha.

Documentar al final es la forma más rápida de perder la trazabilidad entre la ecuación booleana, la simulación y el montaje. Las evidencias conviene capturarlas mientras el circuito está armado.
