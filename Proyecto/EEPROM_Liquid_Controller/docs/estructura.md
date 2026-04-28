# Estructura de la app de PC

Esta app se separa por responsabilidades para evitar que la interfaz, la validacion
del archivo `.org` y la comunicacion serial queden mezcladas.

```text
EEPROM_Liquid_Controller/
├── assets/                         # Imagenes usadas por la interfaz Tkinter
├── docs/                           # Notas tecnicas de la app de PC
├── examples/                       # Archivos .org de prueba
├── main.py                         # Entry point corto
└── src/
    └── eeprom_liquid_controller/
        ├── app.py                  # Arranque de la aplicacion
        ├── config.py               # Constantes globales y rutas
        ├── domain/                 # Modelos: escenas, comandos, estados
        ├── org/                    # Parser y validacion de archivos .org
        ├── serial/                 # Comunicacion USB/serial con Arduino
        └── ui/                     # Ventanas, widgets y carga de assets
```

# Como ejecutar

Requisitos:
- Python 3.11 o superior

Desde la carpeta `Proyecto/EEPROM_Liquid_Controller`, instala dependencias con:

```bash
pip install -e .
```

Luego puedes ejecutar la app de cualquiera de estas formas:

```bash
python main.py
```

```bash
python -m eeprom_liquid_controller
```

```bash
eeprom-liquid-controller
```
