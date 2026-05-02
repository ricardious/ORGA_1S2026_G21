---
title: "Proyecto: Casa Inteligente con Control de Ambientes y Ventilador Automatizado"
description: Sistema domótico a escala con Arduino, EEPROM, LCD I2C, control por Bluetooth y carga de escenas desde archivo .org.
---

## Resumen

Este proyecto integra una maqueta de casa inteligente con cinco zonas de iluminación, ventilador DC, puerta automatizada y persistencia de escenas en EEPROM.  
La arquitectura se apoya en un Arduino Uno como unidad central, una app de escritorio para enviar configuraciones `.org` por USB y una app móvil para activar modos por Bluetooth.

## Estado actual del firmware

- El sketch principal está en `Proyecto/arduino/eeprom_liquid_controller/eeprom_liquid_controller.ino`.
- El sistema arranca en estado listo y publica `READY` por serial.
- La versión actual ya no siembra escenas por defecto al iniciar.
- La EEPROM solo se actualiza cuando finaliza correctamente una carga `.org`.
- Los comandos operativos incluyen `modo_fiesta`, `modo_relajado`, `modo_noche`, `encender_todo`, `apagar_todo`, `estado`, `abrir_puerta` y `cerrar_puerta`.

## Componentes del repositorio

- Firmware Arduino: control de escenas, EEPROM, LCD, ventilador, puerta y LEDs.
- `EEPROM_Liquid_Controller`: app de escritorio en Python para transferencia serial de archivos `.org`.
- `eeprom_liquid_remote`: app móvil en Flutter para control por Bluetooth.
- Documentación técnica en LaTeX y activos visuales del montaje y la simulación.

## Evidencia física reciente

![Maqueta física funcionando con iluminación activa y puerta en prueba](/media/proyectos/casa-inteligente/maqueta_funcionando_con_puerta.jpeg)

![Montaje general con Arduino, protoboard y LCD I2C](/media/proyectos/casa-inteligente/montaje_general_protoboard_lcd.jpeg)

![Vista lateral del cableado entre maqueta, Arduino y LCD](/media/proyectos/casa-inteligente/cableado_lateral_maqueta_arduino.jpeg)

![Acercamiento a la zona de conexiones y pruebas del Arduino Uno R3 durante el montaje](/media/proyectos/casa-inteligente/detalle_arduino_uno_r3.jpeg)

## Entregables relacionados

- Documento técnico: `Proyecto/documentacion_proyecto.tex`
- Simulación Proteus: `Proyecto/G21_S1_2026_Proyecto.pdsprj`
- README de carga del firmware: `Proyecto/arduino/README.md`
