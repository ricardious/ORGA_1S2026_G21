---
title: "Práctica 3: Carrusel Automatizado con Control de Acceso Seguro"
description: Diseño e implementación de un sistema secuencial con autenticación de 4 bits, contador de errores, alarma, temporización y control bidireccional de motor DC.
---

## Resumen

La práctica 3 consistió en diseñar e implementar un **carrusel automatizado con control de acceso seguro**, integrando lógica combinacional, lógica secuencial y una etapa de potencia para el manejo del motor.  
El sistema restringe la activación del carrusel mediante una **contraseña digital de 4 bits**, contabiliza intentos fallidos, activa una alarma al llegar a tres errores y, cuando el acceso es válido, ejecuta una secuencia de giro controlada por tiempo.

La solución se validó en **Proteus** y luego se trasladó a **montaje físico sobre protoboard**, manteniendo una arquitectura modular por bloques:

- **Autenticación**: memoria de contraseña, comparación y validación.
- **Seguridad**: contador de errores y alarma persistente.
- **Temporización**: conteo ascendente de `0` a `15` y descendente de `10` a `0`.
- **Visualización**: displays de 7 segmentos para tiempo y errores.
- **Potencia**: puente H para invertir el giro del motor del carrusel.

## Fechas clave

- Asignación del proyecto: **21/03/2026**
- Fecha fin de elaboración / entrega: **18/04/2026**
- Fecha de calificación: **18/04/2026**

## Marco formativo

### Valor de la práctica

Esta práctica fortalece la comprensión de la **lógica digital secuencial y combinacional** al integrar registro, comparación, conteo, bloqueo por errores y accionamiento de una carga física real.  
Su valor principal radica en conectar el análisis de estados y señales de control con una implementación tangible que combina simulación, cableado y estructura mecánica.

### Competencias desarrolladas

- Diseño de sistemas secuenciales con flip-flops tipo D.
- Integración entre lógica de validación, contadores y visualización.
- Uso de comparadores, decodificadores y compuertas TTL en un sistema mayor.
- Separación funcional entre lógica digital, temporización y etapa de potencia.
- Documentación técnica basada en evidencias de simulación y montaje.

### Objetivo SMART

Diseñar, simular e implementar antes del **18 de abril de 2026** un carrusel automatizado con contraseña de 4 bits, contador de errores, alarma de seguridad, control bidireccional de motor DC y visualización de tiempo en displays, validando su funcionamiento tanto en Proteus como en montaje físico.

## Objetivo

### Objetivo general

Diseñar y construir un sistema de acceso seguro para un carrusel automatizado, capaz de autenticar usuarios, bloquear intentos inválidos y ejecutar una secuencia controlada de movimiento y visualización.

### Objetivos específicos

- Almacenar una contraseña de 4 bits con flip-flops tipo D.
- Comparar el ingreso del usuario contra la contraseña memorizada.
- Detectar y contar intentos fallidos hasta activar una alarma en el tercer error.
- Implementar un contador ascendente para la fase verde y un contador descendente para la fase roja.
- Mostrar tiempo y errores en displays de 7 segmentos.
- Controlar el sentido de giro del motor mediante un puente H discreto.

## Requisitos del enunciado

- Implementar una contraseña de 4 bits almacenada en flip-flops.
- Comparar la contraseña con un comparador de 4 bits.
- Mostrar intentos fallidos en un display de 7 segmentos.
- Activar una alarma al llegar a tres errores consecutivos.
- Usar un Arduino únicamente para generar pulsos de reloj y control auxiliar del motor.
- Ejecutar una secuencia de **15 s** en una dirección y **10 s** en la dirección contraria.
- Integrar LEDs indicadores de estado y una maqueta física funcional.
- Entregar archivo `.pdsprj`, documentación y evidencias en el repositorio.

## Alcance

El alcance del trabajo cubrió:

- Diseño de los bloques de autenticación, seguridad, temporización, visualización y potencia.
- Integración completa en un solo proyecto de Proteus.
- Validación funcional de la secuencia de acceso y movimiento.
- Construcción de una maqueta física del carrusel con motor y cableado real.
- Elaboración de documentación técnica y presupuesto reportado.

No se delegó la lógica principal al Arduino; su papel se restringió a generar pulsos de reloj y a conmutar las señales de dirección del motor.

## Enunciado interpretado

De acuerdo con la consigna, el sistema debía comportarse como una atracción automatizada con **acceso condicionado por contraseña**, capaz de impedir activaciones no autorizadas y de ejecutar un ciclo completo de movimiento cuando la validación fuera correcta.  
Esto implicó resolver tres problemas al mismo tiempo:

1. **memorizar y comparar** una contraseña digital,
2. **registrar y bloquear** errores consecutivos,
3. **coordinar** tiempo, giro del motor y señalización visual.

Ese tercer punto fue especialmente importante, porque el sistema no solo debía encender un motor, sino también mostrar claramente en qué fase del ciclo se encontraba y mantener consistencia entre lógica interna y comportamiento físico.

## Entradas y salidas

### Entradas

- Switch de 4 bits para definir la contraseña almacenada.
- Switch de 4 bits para el ingreso del usuario.
- Pulsador de guardado de contraseña.
- Pulsador de validación de ingreso.
- Pulsador de reinicio.
- Señal de reloj generada por el Arduino para los contadores.

### Salidas

- Señal `AUTH_OK` de habilitación general.
- Conteo de errores en display de 7 segmentos.
- Tiempo de fase en displays de 7 segmentos.
- LED verde y LED rojo para indicar sentido de giro.
- Alarma visual/sonora.
- Señales del puente H hacia el motor DC.

## Diseño lógico y electrónico

### Arquitectura general

La solución se organizó en módulos independientes conectados por señales de control bien definidas.

| Módulo | Integrados / elementos principales | Función |
|---|---|---|
| Unidad de control | Arduino Uno | Genera pulsos de reloj y controla la secuencia del motor |
| Registro de contraseña | `74LS174` | Guarda la contraseña de 4 bits |
| Comparación y validación | `74LS85`, `74LS74` | Compara entrada y memoriza `AUTH_OK` |
| Contador de errores | `74LS74`, `74LS20`, `74LS04`, `74LS48` | Cuenta errores y activa la alarma |
| Temporización | `74LS74`, `74LS08`, `74LS32` | Implementa conteo ascendente y descendente |
| Visualización de tiempo | `74LS157`, `74LS283`, `74LS48` | Selecciona fase activa y adapta a displays |
| Puente H | `2N2222A`, `1N4007`, motor DC | Invierte el giro del motor |

### Flujo general de señales

El recorrido principal de la información puede resumirse así:

1. Se define una contraseña en el bloque de memoria.
2. El usuario ingresa otra combinación de 4 bits.
3. El comparador valida coincidencia.
4. Si la validación falla, se incrementa el contador de errores.
5. Si la validación es correcta, se activa `AUTH_OK`.
6. El Arduino inicia la secuencia temporal del carrusel.
7. El sistema conmuta entre fase verde ascendente y fase roja descendente.
8. El puente H traduce las señales digitales en giro físico del motor.

### Unidad de control con Arduino

El Arduino no reemplaza la lógica digital del sistema. Su función se limita a:

- leer la señal de habilitación `AUTH_OK`,
- generar pulsos de reloj para los contadores,
- mantener la fase de avance durante 15 segundos,
- cambiar de dirección y activar la fase de retorno durante 10 segundos,
- detener el sistema cuando la habilitación desaparece.

<img src="/media/practicas/practica-3/bloques/unidad_control_arduino.png" alt="Unidad de control con Arduino en Proteus" />

### Módulo de autenticación

La autenticación se compone de tres etapas:

1. **Registro de contraseña** con `74LS174`.
2. **Comparación** entre contraseña memorizada y entrada de usuario con `74LS85`.
3. **Latch de habilitación** con `74LS74` para estabilizar `AUTH_OK`.

Esta estructura evita que el sistema dependa directamente del tiempo de presión del botón y permite que la habilitación permanezca estable una vez validada.

<img src="/media/practicas/practica-3/bloques/modulo_autenticacion_general.png" alt="Vista general del módulo de autenticación" />

<img src="/media/practicas/practica-3/bloques/memoria_contrasena_y_comparador.png" alt="Registro de contraseña y comparador de 4 bits" />

<img src="/media/practicas/practica-3/bloques/latch_autorizacion_auth_ok.png" alt="Latch de autorización AUTH_OK" />

### Contador de errores y alarma

Cada validación incorrecta genera un pulso `ERROR`. Ese pulso alimenta un contador binario de 2 bits implementado con flip-flops tipo D, suficiente para representar los estados `0`, `1`, `2` y `3`.

Cuando el contador alcanza `11`, una lógica de detección activa la alarma y deshabilita el movimiento. El display asociado muestra visualmente el número de errores acumulados.

<img src="/media/practicas/practica-3/bloques/modulo_contador_errores_alarma_general.png" alt="Vista general del módulo de contador de errores y alarma" />

<img src="/media/practicas/practica-3/bloques/contador_errores_flip_flops.png" alt="Contador de errores implementado con flip-flops tipo D" />

<img src="/media/practicas/practica-3/bloques/display_contador_errores.png" alt="Display del contador de errores" />

### Temporización y secuencia

Para representar claramente las dos fases del ciclo se implementaron dos contadores distintos:

- **contador ascendente de `0` a `15`** para la fase verde,
- **contador descendente de `10` a `0`** para la fase roja.

#### Contador ascendente

El contador ascendente utiliza cuatro flip-flops tipo D. Cada pulso de reloj incrementa el estado binario en una unidad:

`0000 -> 0001 -> 0010 -> ... -> 1111`

Como `1111 = 15`, este bloque cubre exactamente la primera fase temporal del enunciado.

#### Contador descendente

El contador descendente también usa cuatro flip-flops tipo D, pero su realimentación se diseñó para decrementar una unidad por pulso. Antes de iniciar la fase roja, una lógica de carga fuerza el patrón `1010`, equivalente a `10` decimal.

`1010 -> 1001 -> 1000 -> 0111 -> ... -> 0000`

Para construir esa condición se utilizó una **NAND de 4 entradas**, porque era necesario resumir el estado completo del bloque y generar una sola señal de carga (`LOAD_10`) útil en lógica TTL. Esa señal permite arrancar siempre desde 10 y evita que el contador herede un estado residual de la fase anterior.

<img src="/media/practicas/practica-3/bloques/modulo_temporizacion_secuencia_general.png" alt="Vista general del módulo de temporización y secuencia" />

<img src="/media/practicas/practica-3/bloques/contador_ascendente_0_a_15.png" alt="Contador ascendente de 0 a 15" />

<img src="/media/practicas/practica-3/bloques/contador_descendente_10_a_0.png" alt="Contador descendente de 10 a 0" />

### Multiplexación y visualización

Una vez definidos ambos contadores, se necesitó seleccionar cuál de ellos sería visible en los displays. Para esto se usaron multiplexores `74LS157` y un bloque de ajuste BCD con `74LS283` y `74LS48`.

La lógica de visualización permite:

- mostrar el conteo ascendente durante la fase verde,
- mostrar el conteo descendente durante la fase roja,
- activar la decena cuando el valor llega a `10` o más.

<img src="/media/practicas/practica-3/bloques/logica_multiplexacion_y_displays_tiempo.png" alt="Lógica de multiplexación y adaptación a displays de tiempo" />

### Control del motor DC

El motor se accionó mediante un **puente H discreto** construido con transistores `2N2222A` y diodos `1N4007`. Esta etapa permite invertir la polaridad aplicada al motor y, por tanto, cambiar el sentido de giro entre la fase verde y la fase roja.

En las evidencias físicas puede observarse el cableado asociado al motor y la integración del carrusel con los protoboards del sistema.

## Implementación física

La maqueta integra la estructura mecánica del carrusel con las placas de protoboard y el cableado de control. Las fotografías muestran tanto el montaje general como pruebas más cercanas del motor y del sistema completo.

<img src="/media/practicas/practica-3/montaje/carrusel_maqueta_completa.jpeg" alt="Maqueta completa del carrusel con circuitos de control" />

<img src="/media/practicas/practica-3/montaje/carrusel_con_breadboards.jpeg" alt="Carrusel integrado con protoboards y circuitos digitales" />

<img src="/media/practicas/practica-3/montaje/carrusel_vista_superior.jpeg" alt="Vista superior del montaje físico del carrusel" />

<img src="/media/practicas/practica-3/montaje/prueba_motor_y_cableado.jpeg" alt="Prueba física del motor y verificación de cableado" />

## Pruebas y funcionamiento observado

### Casos de validación principales

- Ingreso correcto de contraseña: habilita el sistema y reinicia errores.
- Ingreso incorrecto de contraseña: incrementa el contador de errores.
- Tercer error consecutivo: activa la alarma y bloquea el movimiento.
- Fase verde: conteo ascendente con LED verde activo.
- Fase roja: conteo descendente con LED rojo activo.
- Pérdida de habilitación: detiene el motor y aborta la secuencia.

### Observaciones de funcionamiento

- El uso de un latch para `AUTH_OK` evita arranques inestables por rebotes.
- La separación entre lógica de seguridad y etapa de potencia mejora la estabilidad del sistema.
- Los contadores no son solo visuales: también participan en la detección de estados relevantes para el control temporal.
- El puente H traduce correctamente el estado digital en movimiento físico observable.

## Evidencias

### Evidencias de simulación

- Unidad de control con Arduino.
- Módulo de autenticación y memoria de contraseña.
- Contador de errores y alarma.
- Temporización y secuencia.
- Multiplexación y displays de tiempo.

### Evidencias de montaje

- Maqueta completa del carrusel.
- Integración con protoboards.
- Vista superior durante pruebas.
- Verificación del motor y del cableado de accionamiento.

## Presupuesto

El presupuesto se construyó a partir de costos reportados por los integrantes. En los casos donde no hubo factura individual, se consigna como gasto reportado.

| Componente | Cantidad | Unitario (Q) | Subtotal (Q) |
|---|---:|---:|---:|
| Arduino Uno | 1 | 150.00 | 150.00 |
| Motor DC | 1 | 19.00 | 19.00 |
| 74LS174 | 1 | 10.00 | 10.00 |
| 74LS74 | 2 | 8.00 | 16.00 |
| Buzzer activo 5V | 1 | 5.00 | 5.00 |
| Resistencias de 10 kΩ | 10 | 0.75 | 7.50 |
| 4 transistores y 4 diodos | 1 lote | 16.00 | 16.00 |
| Gasto reportado por otros integrantes | 1 lote | 68.00 | 68.00 |
| **Total reportado** |  |  | **291.50** |

## Conclusiones

- Se implementó un sistema secuencial funcional donde la autenticación y la temporización trabajan de forma integrada.
- El contador de errores y la alarma cumplen el objetivo de bloquear accesos inválidos sin depender del Arduino.
- La solución separa correctamente la lógica digital de la etapa de potencia del motor.
- El uso de dos contadores distintos mejora la claridad visual del ciclo del carrusel.
- La maqueta física demuestra que el proyecto no se quedó en simulación y requirió integración real entre electrónica y estructura mecánica.
