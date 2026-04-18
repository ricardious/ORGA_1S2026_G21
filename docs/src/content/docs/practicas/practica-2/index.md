---
title: "Práctica 2: Lógica Binaria y Combinacional (LogicCalc)"
description: Diseño e implementación de una ALU combinacional de 4 bits con operaciones aritméticas, lógicas y comparativas, documentada con evidencias de simulación y montaje.
---

## Resumen

La práctica 2 consistió en diseñar e implementar **LogicCalc**, una calculadora binaria basada en lógica combinacional que modela una **Unidad Aritmética Lógica (ALU)** elemental.  
El sistema trabaja con dos operandos de 4 bits (`A` y `B`) y ejecuta operaciones aritméticas, lógicas y comparativas, mostrando resultados en displays de 7 segmentos y en LEDs según el bloque activo.

El desarrollo se validó en **Proteus** y posteriormente se trasladó a **protoboard**, conservando una arquitectura modular por bloques:

- **Unidad aritmética**: suma, resta, multiplicación y potencia.
- **Unidad lógica**: AND, OR, NAND y XNOR.
- **Unidad comparativa**: determina mayor y menor entre operandos.
- **Conversión binario a BCD**: adapta los resultados para su visualización decimal.

## Fechas clave

- Asignación del proyecto: **07/03/2026**
- Fecha fin de elaboración / entrega: **21/03/2026**
- Fecha de calificación: **21/03/2026**

## Marco formativo

### Valor de la práctica

Esta práctica fortalece la comprensión de la **lógica digital combinacional** al obligar a construir una ALU sin microcontroladores ni lógica secuencial.  
Su valor principal radica en conectar el análisis booleano con una implementación real, donde cada bloque debe justificarse desde la tabla de verdad hasta el cableado final.

### Competencias desarrolladas

- Análisis y síntesis de circuitos digitales combinacionales.
- Interpretación de hojas de datos de circuitos TTL.
- Diseño modular de sistemas digitales por subbloques funcionales.
- Integración entre simulación, validación visual y montaje físico.
- Documentación técnica de arquitectura, materiales, presupuesto y resultados.

### Objetivo SMART

Diseñar, simular e implementar antes del **21 de marzo de 2026** una ALU combinacional de 4 bits capaz de ejecutar ocho operaciones seleccionables, presentar resultados aritméticos en displays, resultados lógicos en LEDs y evidenciar su funcionamiento tanto en Proteus como en montaje físico.

## Objetivo

### Objetivo general

Diseñar y construir una ALU combinacional funcional (**LogicCalc**) capaz de ejecutar operaciones aritméticas y lógicas con visualización correcta y validación tanto en simulación como en montaje físico.

### Objetivos específicos

- Implementar operaciones aritméticas: suma, resta, multiplicación y potencia.
- Implementar operaciones lógicas: AND, OR, NAND y XNOR.
- Integrar una unidad comparativa que muestre el valor mayor y el menor entre operandos.
- Mostrar resultados aritméticos y comparativos en displays de 7 segmentos.
- Mostrar resultados lógicos en un banco de 4 LEDs.
- Integrar el circuito completo en un solo proyecto de Proteus y verificar una versión física funcional.

## Requisitos del enunciado

- Implementar una ALU combinacional con operaciones aritméticas y lógicas.
- Integrar un bloque comparador para identificar número mayor y menor.
- Utilizar únicamente componentes permitidos del enunciado.
- Presentar el circuito funcional en un solo archivo `.pdsprj`.
- Entregar documentación técnica en PDF dentro del repositorio grupal.
- Construir una versión física funcional.
- Incluir indicadores visuales de unidad activa.

## Alcance

El alcance del trabajo cubrió:

- Diseño lógico de cada submódulo.
- Integración completa en un solo archivo de Proteus.
- Validación de operaciones aritméticas, lógicas y comparativas.
- Adaptación de resultados binarios a visualización decimal.
- Construcción física sobre protoboards.
- Elaboración de documentación técnica y presupuesto.

No se consideró el uso de elementos programables; toda la solución se resolvió con lógica discreta de la serie `74LS`, resistencias, indicadores visuales y cableado manual.

## Enunciado interpretado

De acuerdo con la consigna, el sistema debía comportarse como una calculadora binaria elemental con control por selector, capaz de operar sobre dos números de 4 bits y cambiar de función sin reconfigurar físicamente el circuito.  
Esto implicó resolver dos problemas al mismo tiempo:

1. construir los bloques funcionales que producen cada resultado, y
2. diseñar la ruta de selección y visualización para que solo la operación activa llegue a la salida final.

Ese segundo punto fue especialmente importante, porque una ALU discreta no solo requiere “calcular”, sino también **elegir correctamente qué resultado mostrar** entre varios módulos trabajando sobre las mismas entradas.

## Entradas y salidas

### Entradas

- Operando `A` de 4 bits.
- Operando `B` de 4 bits.
- Selector de operación de 3 bits.

### Salidas

- Resultado aritmético/comparativo en displays de 7 segmentos.
- Resultado lógico en 4 LEDs.
- Indicadores de unidad activa.

### Configuración de operandos

Los operandos se ingresan con bancos de DIP switches de 4 posiciones. Cada combinación representa un valor de `0` a `15`.

| Binario | Decimal |
|---:|---:|
| 0000 | 0 |
| 0001 | 1 |
| 0010 | 2 |
| 0011 | 3 |
| 0100 | 4 |
| 0101 | 5 |
| 0110 | 6 |
| 0111 | 7 |
| 1000 | 8 |
| 1001 | 9 |
| 1010 | 10 |
| 1011 | 11 |
| 1100 | 12 |
| 1101 | 13 |
| 1110 | 14 |
| 1111 | 15 |

<img src="/media/practicas/practica-2/bloques/numeros_A_B.png" alt="Configuración de operandos A y B con DIP switches en Proteus" />

La elección de DIP switches permitió:

- variar operandos rápidamente durante pruebas,
- repetir combinaciones sin modificar cableado,
- validar tanto casos simples como casos límite,
- y observar directamente la relación entre entrada binaria y salida visual.

### Combinaciones de prueba recomendadas

| A bin | A dec | B bin | B dec | Caso representativo |
|---:|---:|---:|---:|---|
| 0011 | 3 | 0010 | 2 | Suma, resta positiva y comparación |
| 0010 | 2 | 0011 | 3 | Resta negativa y bandera de signo |
| 0101 | 5 | 0101 | 5 | Igualdad en comparador |
| 0011 | 3 | 0001 | 1 | Operaciones lógicas simples |
| 0011 | 3 | 0010 | 2 | Potencia cuadrática |
| 0010 | 2 | 0011 | 3 | Potencia cúbica |

## Diseño lógico y electrónico

### Arquitectura general

La solución se organizó en módulos independientes conectados a un **controlador principal**. El selector de 3 bits habilita una sola operación a la vez y enruta la salida al bloque correspondiente.

| Módulo | Integrados principales | Función |
|---|---|---|
| Controlador principal | `74LS138`, `74LS04` | Decodifica la selección de operación |
| Entradas binarias | DIP switches, resistencias | Define `A[3:0]` y `B[3:0]` |
| Suma y resta | `74LS86`, `74LS08`, `74LS32` | Calcula `A+B` y `A-B` |
| Multiplicación | `74LS08`, `74LS283` | Genera productos parciales y resultado |
| Potencia | `74LS08`, `74LS283`, `74LS157` | Calcula `A²` y `A³` |
| Unidad lógica | `74LS08`, `74LS32`, `74LS00`, `74LS266` | Evalúa AND, OR, NAND, XNOR |
| Unidad comparativa | `74LS85`, `74LS157`, `74LS48` | Muestra mayor y menor |
| Binario a BCD | `74LS86`, `74LS08`, `74LS32`, `74LS283`, `74LS48` | Convierte resultados para displays |

El diseño modular permitió:

- aislar errores por etapa,
- reutilizar señales entre bloques,
- simplificar la validación por casos de prueba,
- y separar claramente las salidas lógicas de las aritméticas.

### Flujo general de señales

El recorrido de la información dentro de LogicCalc puede resumirse así:

1. Se definen `A` y `B` en los bancos de entrada.
2. El selector habilita una sola combinación de control.
3. El controlador principal activa el submódulo correspondiente.
4. El resultado se envía a LEDs o a conversión BCD según el tipo de operación.
5. Los displays o LEDs presentan la salida final al usuario.

Este flujo fue útil para estructurar tanto la simulación como la documentación web, porque permite explicar el sistema desde lo más general hasta cada implementación específica.

### Controlador principal

El controlador principal se implementó con un `74LS138` y lógica inversora para habilitar una ruta de operación por vez.

| A | B | C | Operación habilitada |
|---:|---:|---:|---|
| 0 | 0 | 0 | Suma |
| 1 | 0 | 0 | Resta |
| 0 | 1 | 0 | Multiplicación |
| 1 | 1 | 0 | Potencia |
| 0 | 0 | 1 | AND |
| 1 | 0 | 1 | OR |
| 0 | 1 | 1 | NAND |
| 1 | 1 | 1 | XNOR |

La salida del controlador no solo determina qué operación está activa, sino también qué bloque visual debe responder. Esto evita conflictos entre módulos y permite que la operación seleccionada se identifique visualmente con LEDs de estado.

#### Rol del controlador dentro del sistema

- Recibe el selector general de 3 bits.
- Decodifica la combinación activa.
- Habilita la ruta correspondiente.
- Bloquea la propagación de resultados de módulos no seleccionados.
- Coordina la visualización final del sistema.

#### Observación de diseño

Aunque el controlador parece un bloque pequeño respecto al resto del sistema, en la práctica es uno de los más importantes. Un error en la decodificación del selector afecta simultáneamente a todos los módulos, por lo que se tomó como referencia central para revisar el mapeo correcto de operaciones durante la documentación.

<img src="/media/practicas/practica-2/bloques/controlador_principal.png" alt="Controlador principal de LogicCalc implementado en Proteus" />

### Unidad aritmética

La unidad aritmética concentra suma, resta, multiplicación y potencia. Los resultados binarios se envían luego al bloque de conversión BCD para representación decimal.

#### Suma y resta

La suma y la resta se resolvieron con una estructura de sumadores completos. Para la resta se utilizó complemento a dos parcial, invirtiendo `B` mediante XOR y ajustando el acarreo de entrada.

| `op_res` | Comportamiento |
|---:|---|
| 0 | El bloque trabaja como sumador binario de 4 bits (`A+B`) |
| 1 | El bloque implementa la resta binaria de 4 bits (`A-B`) |

| A | B | `C_in` | S | `C_out` |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 | 0 |
| 0 | 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 | 0 |
| 1 | 0 | 1 | 0 | 1 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 | 1 |

| A | B | Resultado | Interpretación |
|---:|---:|---:|---|
| 0011 | 0010 | 0101 | `3 + 2 = 5` |
| 0101 | 0011 | 1000 | `5 + 3 = 8` |
| 0011 | 0010 | 0001 | `3 - 2 = 1` |
| 0010 | 0011 | 1111 | `2 - 3 = -1` en complemento a dos |

#### Interpretación del bloque suma/resta

- Cuando `op_res = 0`, el módulo actúa como sumador binario estándar.
- Cuando `op_res = 1`, el operando `B` se invierte y el acarreo inicial implementa el ajuste necesario para la resta.
- El bloque genera tanto el resultado parcial como la información necesaria para detectar signo y propagación de acarreo.

#### Casos analizados en suma

- Suma sin acarreo final.
- Suma con acarreo de salida.
- Suma de operandos intermedios.
- Comportamiento visual del resultado en displays.

#### Casos analizados en resta

- Resta con resultado positivo.
- Resta con resultado nulo.
- Resta con resultado negativo.
- Propagación de la bandera de signo hacia la visualización.

#### Etapas del bloque

##### Etapa 0
Corresponde al bit menos significativo y establece la base para el acarreo inicial del sistema.

<img src="/media/practicas/practica-2/bloques/suma_resta_p1.png" alt="Etapa 0 del bloque de suma y resta" />

##### Etapa 1
Propaga el acarreo desde la primera etapa y conserva el mismo patrón estructural del sumador completo.

<img src="/media/practicas/practica-2/bloques/suma_resta_p2.png" alt="Etapa 1 del bloque de suma y resta" />

##### Etapa 2
Mantiene la acumulación de acarreo y consolida la lógica de los bits intermedios.

<img src="/media/practicas/practica-2/bloques/suma_resta_p3.png" alt="Etapa 2 del bloque de suma y resta" />

##### Etapa final
Resuelve el bit más significativo y genera la señal asociada al signo en operaciones de resta.

<img src="/media/practicas/practica-2/bloques/suma_resta_p4.png" alt="Etapa final del bloque de suma y resta con manejo de signo" />

#### Multiplicación

La multiplicación binaria se implementó con **productos parciales** generados por compuertas AND y sumados progresivamente con `74LS283`.

| Producto parcial | Descripción |
|---|---|
| `A · B0` | AND entre cada bit de `A` y `B0` |
| `A · B1` | AND entre `A` y `B1`, desplazado 1 posición |
| `A · B2` | AND entre `A` y `B2`, desplazado 2 posiciones |
| `A · B3` | AND entre `A` y `B3`, desplazado 3 posiciones |

Ejemplo:

- `A = 0011₂ = 3`
- `B = 0010₂ = 2`
- Resultado: `00000110₂ = 6`

La multiplicación fue uno de los bloques más costosos en integrados, ya que requiere construir y acumular varios productos parciales. Aun así, su implementación replica directamente el algoritmo binario clásico, por lo que resulta didácticamente clara.

#### Criterio de implementación

En vez de resolver la multiplicación con una caja negra o con un componente dedicado de alto nivel, se optó por construirla a partir de:

- compuertas AND para productos parciales,
- desplazamientos implícitos por posición,
- y sumadores `74LS283` para acumular resultados.

Eso hace que el bloque sea más largo, pero también más transparente desde el punto de vista académico.

<img src="/media/practicas/practica-2/bloques/multiplicacion.png" alt="Bloque de multiplicación binaria implementado en Proteus" />

#### Potencia

El bloque de potencia calcula `A²` o `A³` dependiendo del valor cargado en `B`.

| Valor de `B` | Operación |
|---:|---|
| 0010 | `A²` |
| 0011 | `A³` |

| A bin | B bin | Operación | Resultado bin | Decimal |
|---:|---:|---|---:|---:|
| 0010 | 0010 | `2²` | 000100 | 4 |
| 0011 | 0010 | `3²` | 001001 | 9 |
| 0010 | 0011 | `2³` | 001000 | 8 |
| 0011 | 0011 | `3³` | 011011 | 27 |

Este bloque reutiliza estructuras semejantes a las de multiplicación, pero su selección depende del valor de `B`, por lo que también implica una capa de control adicional. En la práctica, esto permitió diferenciar entre cálculo cuadrático y cúbico sin recurrir a circuitos programables.

#### Criterio funcional del bloque de potencia

- Si `B = 2`, el sistema prioriza el cálculo del cuadrado.
- Si `B = 3`, el sistema prioriza el cálculo del cubo.
- Otros valores no forman parte del caso principal definido por la práctica, por lo que el bloque queda condicionado por la lógica de control.

Esto convierte al bloque de potencia en una operación especial dentro de LogicCalc, porque depende no solo de la selección general sino también del valor explícito del operando `B`.

<img src="/media/practicas/practica-2/bloques/potencia.png" alt="Bloque de potencia para cuadrado y cubo" />
<img src="/media/practicas/practica-2/bloques/potencia_salidas.png" alt="Selección de salidas del bloque de potencia" />

### Unidad lógica

La unidad lógica produce operaciones bit a bit y muestra el resultado con LEDs.

| A | B | AND | OR | NAND | XNOR |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | 0 |
| 1 | 0 | 0 | 1 | 1 | 0 |
| 1 | 1 | 1 | 1 | 0 | 1 |

| Operación | Comportamiento visual |
|---|---|
| AND | El LED enciende solo cuando ambos bits son `1` |
| OR | El LED enciende cuando al menos un bit es `1` |
| NAND | El LED se apaga solo cuando ambos bits son `1` |
| XNOR | El LED enciende cuando los bits son iguales |

El uso de LEDs como salida directa de la unidad lógica permitió validar rápidamente cada operación bit a bit sin pasar por el bloque de visualización decimal. Esto simplificó mucho las pruebas del módulo lógico frente a las aritméticas.

#### Ventaja de este bloque en pruebas

La unidad lógica fue la más inmediata de validar, porque cada bit puede interpretarse visualmente sin necesidad de decodificación adicional.  
Esto permitió comprobar la correspondencia exacta entre la tabla de verdad y la salida observada en LEDs.

<img src="/media/practicas/practica-2/bloques/unidad_logica.png" alt="Unidad lógica con operaciones AND, OR, NAND y XNOR" />

### Unidad comparativa

La unidad comparativa usa un `74LS85` para determinar si `A>B`, `A<B` o `A=B`, y con multiplexores enruta el valor mayor a un display y el menor al otro.

| Condición | Display superior | Display inferior |
|---|---|---|
| `A > B` | Muestra `A` | Muestra `B` |
| `A < B` | Muestra `B` | Muestra `A` |
| `A = B` | Muestra `A` | Muestra `A` |

La unidad comparativa es importante porque desacopla la comparación del resto de operaciones aritméticas. En lugar de calcular diferencias para deducir la relación, el bloque usa un comparador dedicado y multiplexores para enrutar los operandos a los displays correctos.

#### Casos esperados del comparador

- Si `A > B`, el display superior debe reflejar el valor mayor.
- Si `A < B`, el display superior debe cambiar al valor de `B`.
- Si `A = B`, ambos displays deben coincidir.

Esta lógica permitió probar el comparador de forma independiente del bloque suma/resta.

<img src="/media/practicas/practica-2/bloques/unidad_comparativa.png" alt="Unidad comparativa para mostrar el mayor y el menor" />

### Conversión binario a BCD

Para mostrar resultados aritméticos en displays se construyó un bloque de conversión binario a BCD, que recibe las salidas intermedias de suma, resta, multiplicación y potencia.

| Ruta de entrada | Uso |
|---|---|
| `RES[3:0]` | Resultado de suma o resta |
| `RES_COUT` | Bit de acarreo adicional |
| `P[7:0]` | Resultado de multiplicación |
| `POW[5:0]` | Resultado de potencia |
| `sign_bit` | Señal de signo para la resta |

Este bloque fue uno de los más complejos de documentar y de integrar, porque concentra:

- filtrado de rutas según la operación activa,
- combinación de resultados de distinto ancho,
- acondicionamiento de señales intermedias,
- y adaptación final a los drivers de display.

#### Razón de su complejidad

Los módulos aritméticos no entregan todos sus resultados con el mismo ancho ni con el mismo contexto.  
Por eso el bloque de conversión tuvo que resolver:

- selección entre varias rutas,
- adaptación de señales de distinto tamaño,
- manejo de bits de acarreo,
- y preparación del valor final para ser interpretado por decodificadores de display.

<img src="/media/practicas/practica-2/bloques/binario_bcd_vista_general.png" alt="Vista general del conversor binario a BCD" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p1.png" alt="Primera etapa del conversor binario a BCD" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p2.png" alt="Filtrado y enrutamiento de líneas por operación activa" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p3.png" alt="Acondicionamiento de líneas para la resta" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p4.png" alt="Combinación entre resultados de suma y resta" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p5.png" alt="Combinación entre multiplicación y suma resta" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p6.png" alt="Banco de LEDs de prueba para salidas intermedias" />
<img src="/media/practicas/practica-2/bloques/binario_bcd_p7.png" alt="Etapa final del conversor binario a BCD" />

### Resumen funcional por bloque

| Bloque | Entradas principales | Salidas principales | Observación técnica |
|---|---|---|---|
| Controlador | Selector de 3 bits | Líneas `op_*` | Coordina toda la práctica |
| Entradas binarias | DIP switches | `A[3:0]`, `B[3:0]` | Punto de partida de todas las pruebas |
| Suma / resta | `A`, `B`, `op_res` | `RES`, `RES_COUT`, `sign_bit` | Manejo de complemento a dos |
| Multiplicación | `A`, `B` | `P[7:0]` | Basada en productos parciales |
| Potencia | `A`, `B`, `op_pow` | `POW[5:0]` | Usa criterio especial de selección |
| Lógica | `A`, `B` | LEDs lógicos | Respuesta inmediata bit a bit |
| Comparativa | `A`, `B` | Displays mayor / menor | Ruteo dinámico mediante multiplexores |
| Binario a BCD | Resultados intermedios | BCD para displays | Mayor complejidad de integración |

## Implementación

### Simulación en Proteus

La simulación se integró en un único proyecto:

- `Práctica 2/G21_S1_2026_P2.pdsprj`

La validación en Proteus permitió:

- Probar las 8 combinaciones de selección.
- Revisar propagación de resultados por bloque.
- Confirmar la exclusión entre unidad lógica y unidad aritmética.
- Verificar el enrutamiento hacia displays y LEDs.

La simulación fue el paso más importante antes del montaje físico, porque permitió detectar:

- errores de selección de operación,
- inconsistencias en propagación de acarreo,
- problemas de inversión lógica en la resta,
- y detalles de visualización en displays.

### Estrategia de validación en simulación

La revisión del circuito en Proteus se hizo por etapas:

1. validación individual de cada bloque,
2. verificación de selección por el controlador,
3. integración de resultados en rutas de salida,
4. comprobación del montaje completo en un único proyecto.

Esto evitó que un error local en un bloque se confundiera con un problema de integración general.

### Resultado integrado

La captura general muestra el circuito completo con la salida aritmética y bloques auxiliares activos dentro del esquema.

<img src="/media/practicas/practica-2/bloques/resultados.png" alt="Vista general de resultados dentro del esquema de Proteus" />

### Montaje físico

Después de la simulación, el circuito se trasladó a protoboards con múltiples integrados TTL, cableado de colores y distribución modular.

El montaje físico puso en evidencia la complejidad real del proyecto: aunque el circuito funciona por lógica combinacional pura, la cantidad de integrados y puentes manuales incrementa el riesgo de errores de conexión. Por eso la documentación fotográfica se volvió necesaria para rastrear módulos y validar etapas.

### Retos observados en el montaje

- Distribución de integrados en varios protoboards.
- Ordenamiento de buses y señales de control.
- Alimentación estable para múltiples TTL.
- Identificación rápida de rutas entre módulo y módulo.

En otras palabras, la versión física no solo prueba el diseño lógico; también pone a prueba la organización práctica del sistema.

<img src="/media/practicas/practica-2/montaje/frame.jpeg" alt="Montaje físico principal de LogicCalc en protoboards" />

## Pruebas y validación

- Validación de las 8 operaciones definidas por el selector.
- Pruebas representativas de suma y resta con distintos acarreos.
- Pruebas de multiplicación por productos parciales.
- Validación de potencia con `B=2` y `B=3`.
- Comparación de casos `A>B`, `A<B` y `A=B`.
- Revisión visual de LEDs y displays según el bloque activo.

### Casos de prueba representativos

| A bin | A dec | B bin | B dec | Relación | Uso de prueba |
|---:|---:|---:|---:|---|---|
| 0011 | 3 | 0010 | 2 | `A > B` | Comparación y resta positiva |
| 0010 | 2 | 0011 | 3 | `A < B` | Comparación y bandera de signo |
| 0101 | 5 | 0101 | 5 | `A = B` | Igualdad en displays |
| 0011 | 3 | 0001 | 1 | `A > B` | Operaciones lógicas y aritméticas simples |
| 0011 | 3 | 0010 | 2 | `A > B` | Potencia con `B = 2` |
| 0010 | 2 | 0011 | 3 | `A < B` | Potencia con `B = 3` |

### Verificaciones realizadas

#### Operaciones aritméticas

- Se verificó la suma de operandos pequeños y medianos.
- Se observó el comportamiento del acarreo de salida.
- Se comprobó la resta con resultado positivo y negativo.
- Se evaluó la propagación de `sign_bit` en la etapa de visualización.

#### Operaciones lógicas

- Se comparó el encendido esperado de LEDs para AND, OR, NAND y XNOR.
- Se validó que la unidad lógica no interfiriera con la unidad aritmética.
- Se confirmaron respuestas bit a bit con combinaciones simples de prueba.

#### Operación comparativa

- Se probaron casos `A > B`, `A < B` y `A = B`.
- Se verificó que el display superior muestre el valor mayor.
- Se verificó que el display inferior muestre el valor menor.

#### Visualización decimal

- Se probó la salida BCD para resultados aritméticos.
- Se revisaron rutas de selección de resultados intermedios.
- Se observó la adaptación final hacia los decodificadores `74LS48`.

### Hallazgos de validación

- La separación entre unidad lógica y unidad aritmética facilitó la lectura de resultados.
- La resta exigió más atención por el tratamiento de signo y complemento a dos.
- Multiplicación y potencia aumentaron la complejidad del cableado y de la visualización.
- El comparador fue más estable al depender de un bloque dedicado.
- El bloque binario a BCD concentró buena parte del trabajo de integración.

## Evidencias

### Capturas adicionales del montaje

Estas imágenes complementan la documentación del ensamble físico y muestran distintas vistas del cableado y la integración.

#### Evidencia 1
<img src="/media/practicas/practica-2/anexos/frame_000001.jpg" alt="Vista adicional 1 del montaje físico de la práctica 2" />

Primera vista del montaje donde se aprecia la distribución general del sistema sobre protoboards.

#### Evidencia 2
<img src="/media/practicas/practica-2/anexos/frame_000048.jpg" alt="Vista adicional 2 del montaje físico de la práctica 2" />

Detalle intermedio del cableado y de la densidad de conexiones entre módulos.

#### Evidencia 3
<img src="/media/practicas/practica-2/anexos/frame_000118.jpg" alt="Vista adicional 3 del montaje físico de la práctica 2" />

Se observa el avance del ensamble físico y la integración progresiva de bloques TTL.

#### Evidencia 4
<img src="/media/practicas/practica-2/anexos/frame_000241.jpg" alt="Vista adicional 4 del montaje físico de la práctica 2" />

Vista útil para identificar la ruta de alimentación y el patrón de interconexión central.

#### Evidencia 5
<img src="/media/practicas/practica-2/anexos/frame_000384.jpg" alt="Vista adicional 5 del montaje físico de la práctica 2" />

Imagen que evidencia el crecimiento del montaje a medida que se agregan bloques funcionales.

#### Evidencia 6
<img src="/media/practicas/practica-2/anexos/frame_000410.jpg" alt="Vista adicional 6 del montaje físico de la práctica 2" />

Captura final del ensamble, útil como referencia del estado consolidado del sistema.

### Factura de referencia

La factura se utilizó como respaldo para consolidar el presupuesto real de componentes.

<img src="/media/practicas/practica-2/presupuesto/factura.jpeg" alt="Factura de referencia utilizada para el presupuesto de la práctica 2" />

## Recursos y herramientas utilizadas

- **Proteus Design Suite** para simulación y depuración del circuito.
- **Integrados TTL de la serie 74LS** como base de la implementación.
- **Displays de 7 segmentos** para visualización decimal.
- **LEDs** para resultados lógicos e indicadores de estado.
- **Protoboards y jumpers** para el montaje físico.
- **Factura de compra** como respaldo para el presupuesto.

## Material de apoyo consultado

- Recursos del enunciado de la práctica.
- Hojas de datos de integrados `74LS`.
- Referencias de diseño combinacional y simplificación booleana.
- Simulación iterativa en Proteus para contrastar comportamiento esperado y observado.

## Cronograma de trabajo

| Fecha | Actividad principal |
|---|---|
| 17 de marzo de 2026 | Compra de componentes y material base |
| 18 al 19 de marzo de 2026 | Diseño de bloques funcionales en Proteus |
| 20 al 21 de marzo de 2026 | Integración de multiplicación, potencia y conversión BCD |
| 21 al 22 de marzo de 2026 | Montaje físico, evidencias y documentación |

## Componentes utilizados

| Nombre del componente | Código / Especificación |
|---|---|
| Compuerta AND | `74LS08` |
| Compuerta OR | `74LS32` |
| Compuerta NOT | `74LS04` |
| Compuerta XOR | `74LS86` |
| Compuerta NAND | `74LS00` |
| Compuerta XNOR | `74LS266` |
| Sumador | `74LS283` |
| Comparador | `74LS85` |
| Multiplexor | `74LS157` |
| Demultiplexor / decoder | `74LS138` |
| Decoder para display | `74LS48` |
| Displays | 7 segmentos de cátodo común |
| LEDs | Indicadores de resultados lógicos y estado |

## Presupuesto

| Cantidad | Descripción del componente | Precio unitario (Q) | Subtotal (Q) |
|---:|---|---:|---:|
| 2 | DIP switch de 4 posiciones | 3.75 | 7.50 |
| 1 | Decodificador / demultiplexor `74LS138` | 6.00 | 6.00 |
| 1 | LED azul difuso 5 mm | 1.00 | 1.00 |
| 1 | LED amarillo difuso 5 mm | 1.00 | 1.00 |
| 11 | LED naranja difuso 5 mm | 1.00 | 11.00 |
| 2 | Compuerta lógica NAND `74LS00` | 5.00 | 10.00 |
| 1 | Comparador `74LS85` | 11.00 | 11.00 |
| 4 | Multiplexor `74LS157` | 7.00 | 28.00 |
| 4 | Decoder / driver `74LS48` para display | 9.00 | 36.00 |
| 2 | Display de 7 segmentos, cátodo común rojo | 5.00 | 10.00 |
| 5 | Compuerta lógica XOR `74LS86` | 6.00 | 30.00 |
| 15 | Sumador de 4 bits `74LS283` | 14.00 | 210.00 |
| 4 | Compuerta lógica AND `74LS08` | 5.00 | 20.00 |
| 2 | Compuerta lógica XNOR `74LS266` | 12.00 | 24.00 |

**Subtotal:** `Q 405.50`  
**Total:** `Q 405.50`  
**Efectivo entregado:** `Q 410.50`  
**Cambio:** `Q 5.00`

## Entregables oficiales

| Tipo | Descripción |
|---|---|
| Archivo de simulación | Proyecto `.pdsprj` funcional en Proteus |
| Documento técnico | PDF con carátula, objetivos, funciones, tablas, diagramas, materiales, presupuesto y conclusiones |
| Repositorio GitHub | Repositorio grupal con carpetas, evidencias y documentación consolidada |
| Evidencia física | Fotografías del montaje y archivos asociados |

## Conclusiones

La práctica cumplió el objetivo de construir una ALU combinacional de 4 bits basada exclusivamente en compuertas y circuitos TTL, integrando operaciones aritméticas, lógicas y comparativas en una sola arquitectura.

La división modular del diseño facilitó la validación en Proteus y permitió trasladar el sistema a protoboard con mayor control sobre errores de interconexión, señales activas y rutas de visualización.

El bloque de conversión binario a BCD fue una de las partes más exigentes del proyecto, ya que incrementó la complejidad del enrutamiento y del acondicionamiento de salidas para displays.

La documentación por bloques, con tablas e imágenes del circuito, deja trazabilidad clara entre el diseño lógico, la simulación y la implementación física, siguiendo un formato más cercano al de la práctica 1.

Como resultado general, LogicCalc evidencia que una ALU básica puede construirse completamente con lógica discreta, pero también muestra el costo real en espacio, complejidad de integración y cantidad de componentes cuando no se usan soluciones programables.

Desde el punto de vista formativo, la práctica aporta más que un circuito terminado: obliga a documentar decisiones de diseño, justificar rutas de señal, descomponer problemas complejos en submódulos y sostener la trazabilidad entre teoría, simulación y montaje.
