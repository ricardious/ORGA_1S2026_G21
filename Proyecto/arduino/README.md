# Arduino EEPROM Liquid Controller

Guia rapida para compilar, instalar dependencias y cargar el sketch
`eeprom_liquid_controller` desde otra PC.

## Ubicacion del sketch

Archivo principal:

```text
arduino/eeprom_liquid_controller/eeprom_liquid_controller.ino
```

## Requisitos

- Arduino IDE 2.x o superior, o `arduino-cli`
- Placa objetivo compatible con Arduino Uno
- Cable USB para cargar el sketch
- Librerias necesarias:
  - `LiquidCrystal_I2C`
  - `Servo` (normalmente ya viene con el core de Arduino AVR)
  - `EEPROM` (normalmente ya viene con el core de Arduino AVR)

## Librerias necesarias

Si al compilar aparece este error:

```text
fatal error: LiquidCrystal_I2C.h: No such file or directory
```

instala la libreria del LCD I2C.

### Instalar desde Arduino IDE

1. Abre Arduino IDE.
2. Ve a `Programa` -> `Incluir Libreria` -> `Administrar bibliotecas...`
3. Busca `LiquidCrystal I2C`.
4. Instala una libreria que exponga el archivo `LiquidCrystal_I2C.h`.
5. La opcion mas comun es `LiquidCrystal I2C` de Frank de Brabander.
6. Compila de nuevo.

## Compilar y cargar desde Arduino IDE

1. Abre el archivo:

```text
arduino/eeprom_liquid_controller/eeprom_liquid_controller.ino
```

2. En `Herramientas` selecciona:
   - `Placa`: `Arduino Uno`
   - `Puerto`: el COM donde aparezca tu Arduino

3. Presiona `Verificar` para compilar.
4. Presiona `Subir` para cargar el programa.

## Compilar y cargar desde CLI

Estas instrucciones usan `arduino-cli`. Si no lo tienes instalado, primero instalo desde:

```text
https://arduino.github.io/arduino-cli/
```

### 1. Inicializar el entorno

```powershell
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
```

### 2. Instalar librerias

```powershell
arduino-cli lib install "LiquidCrystal I2C"
```

Si esa libreria no coincide con el header `LiquidCrystal_I2C.h`, busca una alternativa:

```powershell
arduino-cli lib search "LiquidCrystal I2C"
```

### 3. Ver tarjetas y puertos detectados

```powershell
arduino-cli board list
```

Busca el puerto de tu Arduino, por ejemplo `COM3`.

### 4. Compilar

Desde la raiz del proyecto:

```powershell
arduino-cli compile --fqbn arduino:avr:uno arduino/eeprom_liquid_controller
```

### 5. Cargar a la placa

Reemplaza `COM3` por tu puerto real:

```powershell
arduino-cli upload -p COM3 --fqbn arduino:avr:uno arduino/eeprom_liquid_controller
```

## Verificacion basica

Despues de cargar el sketch:

- el LCD debe encender
- el sistema debe iniciar en estado listo
- el monitor serial debe usar `9600` baudios

## Problemas comunes

### Error: `LiquidCrystal_I2C.h: No such file or directory`

Falta instalar la libreria `LiquidCrystal_I2C`.

### Error al subir por puerto

- verifica que el cable USB transfiera datos
- confirma el puerto correcto con `arduino-cli board list`
- cierra el monitor serial si el puerto esta ocupado

### La placa no compila como Uno

Este proyecto ya tiene artefactos de build bajo `arduino.avr.uno`, asi que la configuracion esperada es:

```text
FQBN: arduino:avr:uno
```

Si usas otra placa, ajusta el `--fqbn` y revisa compatibilidad de pines.

## Nota sobre EEPROM

El sketch usa direcciones fijas por modo. Si se modifica la distribucion de EEPROM en el codigo, debe actualizarse tambien la documentacion del proyecto.
