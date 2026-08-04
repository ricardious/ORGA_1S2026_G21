---
title: Proyecto
description: "Proyecto integrador del curso: casa inteligente con control de ambientes y ventilador automatizado."
---

El proyecto integrador del curso cierra el semestre trasladando el trabajo de lógica discreta de las prácticas hacia un sistema embebido completo, con memoria persistente, comunicación serial y control remoto.

## Proyecto

| Proyecto | Tema | Entrega |
|---|---|:---:|
| [Casa inteligente](casa-inteligente/) | Maqueta domótica con Arduino, escenas en EEPROM, LCD I2C y control por Bluetooth | 02/05/2026 |

## Qué aporta respecto a las prácticas

Mientras las prácticas se resolvieron con compuertas, contadores y flip-flops discretos, el proyecto centra el trabajo en la **organización de la memoria**: cómo se estructura una escena de 36 bytes, en qué dirección fija se almacena, cuándo se valida y cuándo se persiste.

A eso se suman tres capas de software que no aparecían en las prácticas:

- **Firmware Arduino** que concentra la lógica: validación del formato de entrada, escritura en EEPROM y control de actuadores.
- **Aplicación de escritorio** en Python que transfiere archivos `.org` por USB.
- **Aplicación móvil** en Flutter que envía comandos por Bluetooth clásico.
