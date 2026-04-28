#include <EEPROM.h>
#include <Wire.h>
#include <DFRobot_RGBLCD1602.h>
#include <Servo.h>

const int rx_bluetooth = 0;
const int tx_bluetooth = 1;
const int led_azul = 2;
const int led_verde = 3;
const int led_rojo = 4;
const int luces_sala = 5;
const int luces_comedor = 6;
const int luces_cocina = 7;
const int luces_bano = 8;
const int servo_puerta = 9;
const int motor_ventilador = 10;
const int boton_puerta = 11;
const int luces_habitacion = 12;

const unsigned long BAUDRATE = 9600;
const byte EEPROM_MAGIC = 0x42;
const byte LCD_COLUMNS = 16;
const byte LCD_ROWS = 2;
const byte MESSAGE_SIZE = 33;

const byte FAN_OFF = 0;
const byte FAN_ON = 1;

const byte LEDS_OFF = 0;
const byte LEDS_ON = 1;
const byte LEDS_ALTERNATING = 2;

const byte MODE_FIESTA = 0;
const byte MODE_RELAJADO = 1;
const byte MODE_NOCHE = 2;
const byte MODE_ENCENDER_TODO = 3;
const byte MODE_APAGAR_TODO = 4;
const byte MODE_COUNT = 5;
const byte NO_MODE = 255;

const int EEPROM_ADDR_FIESTA = 0;
const int EEPROM_ADDR_RELAJADO = 36;
const int EEPROM_ADDR_NOCHE = 72;
const int EEPROM_ADDR_ENCENDER_TODO = 108;
const int EEPROM_ADDR_APAGAR_TODO = 144;
const int MODE_EEPROM_ADDRESS[MODE_COUNT] = {
  EEPROM_ADDR_FIESTA,
  EEPROM_ADDR_RELAJADO,
  EEPROM_ADDR_NOCHE,
  EEPROM_ADDR_ENCENDER_TODO,
  EEPROM_ADDR_APAGAR_TODO
};

const int DOOR_CLOSED_ANGLE = 0;
const int DOOR_OPEN_ANGLE = 90;

struct SceneConfig {
  byte magic;
  byte fan;
  byte ledPattern;
  char message[MESSAGE_SIZE];
};

struct PendingScene {
  bool touched;
  bool fanSet;
  bool ledsSet;
  byte fan;
  byte ledPattern;
  char message[MESSAGE_SIZE];
};

DFRobot_RGBLCD1602 lcd(LCD_COLUMNS, LCD_ROWS);
Servo doorServo;

PendingScene pendingScenes[MODE_COUNT];
String inputLine = "";
bool uploadActive = false;
bool systemError = false;
byte currentUploadMode = NO_MODE;
byte activeMode = NO_MODE;
bool doorOpen = false;
bool stableDoorButtonState = HIGH;
bool lastDoorButtonReading = HIGH;
unsigned long lastDoorDebounce = 0;
unsigned long lastAlternateTick = 0;
bool alternatePhase = false;

void setup() {
  pinMode(rx_bluetooth, INPUT);
  pinMode(tx_bluetooth, OUTPUT);
  pinMode(led_azul, OUTPUT);
  pinMode(led_verde, OUTPUT);
  pinMode(led_rojo, OUTPUT);
  pinMode(luces_sala, OUTPUT);
  pinMode(luces_comedor, OUTPUT);
  pinMode(luces_cocina, OUTPUT);
  pinMode(luces_bano, OUTPUT);
  pinMode(motor_ventilador, OUTPUT);
  pinMode(boton_puerta, INPUT_PULLUP);
  pinMode(luces_habitacion, OUTPUT);

  Serial.begin(BAUDRATE);
  doorServo.attach(servo_puerta);
  closeDoor();

  lcd.init();
  lcd.setRGB(255, 255, 255);
  setReadyState();

  seedDefaultScenesIfNeeded();
  applyMode(MODE_APAGAR_TODO);
}

void loop() {
  readSerialLines();
  handleDoorButton();
  updateAlternatingLights();
}

void readSerialLines() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();
    if (incoming == '\r') {
      continue;
    }
    if (incoming == '\n') {
      processLine(inputLine);
      inputLine = "";
      continue;
    }
    inputLine += incoming;
  }
}

void processLine(String rawLine) {
  String line = stripComment(rawLine);
  line.trim();
  if (line.length() == 0) {
    return;
  }

  if (line == "conf_ini") {
    beginUpload();
    return;
  }

  if (uploadActive) {
    processUploadLine(line);
    return;
  }

  processCommand(line);
}

String stripComment(String line) {
  int commentIndex = line.indexOf("//");
  if (commentIndex >= 0) {
    return line.substring(0, commentIndex);
  }
  return line;
}

void beginUpload() {
  uploadActive = true;
  systemError = false;
  currentUploadMode = NO_MODE;
  resetPendingScenes();
  digitalWrite(led_rojo, LOW);
  digitalWrite(led_azul, LOW);
  showLcd("Carga .org", "Recibiendo...");
  Serial.println("UPLOAD_START");
}

void processUploadLine(String line) {
  if (line == "conf:fin") {
    finishUpload();
    return;
  }

  byte mode = modeFromLine(line);
  if (mode != NO_MODE) {
    if (!commitCurrentUploadMode()) {
      failUpload("modo incompleto");
      return;
    }
    currentUploadMode = mode;
    pendingScenes[mode].touched = true;
    defaultMessageForMode(mode, pendingScenes[mode].message);
    return;
  }

  if (currentUploadMode == NO_MODE) {
    failUpload("modo no definido");
    return;
  }

  if (startsWithIgnoreCase(line, "Mensaje en LCD:")) {
    parseMessage(line);
    return;
  }

  if (startsWithIgnoreCase(line, "Ventilador:")) {
    parseFan(line);
    return;
  }

  if (startsWithIgnoreCase(line, "LED'S:") ||
      startsWithIgnoreCase(line, "LEDS:") ||
      startsWithIgnoreCase(line, "LEDs:")) {
    parseLeds(line);
    return;
  }

  failUpload("linea invalida");
}

bool commitCurrentUploadMode() {
  if (currentUploadMode == NO_MODE) {
    return true;
  }
  PendingScene &scene = pendingScenes[currentUploadMode];
  return scene.fanSet && scene.ledsSet;
}

void finishUpload() {
  if (!commitCurrentUploadMode()) {
    failUpload("modo incompleto");
    return;
  }

  bool hasScene = false;
  for (byte i = 0; i < MODE_COUNT; i++) {
    if (pendingScenes[i].touched) {
      hasScene = true;
      writeSceneToEeprom(i, pendingScenes[i]);
    }
  }

  if (!hasScene) {
    failUpload("archivo vacio");
    return;
  }

  uploadActive = false;
  currentUploadMode = NO_MODE;
  Serial.println("UPLOAD_OK");
  blinkGreenSuccess();
  setReadyState();
}

void failUpload(const char *reason) {
  uploadActive = false;
  currentUploadMode = NO_MODE;
  systemError = true;
  digitalWrite(led_azul, LOW);
  digitalWrite(led_verde, LOW);
  digitalWrite(led_rojo, HIGH);
  showLcd("Error archivo", reason);
  Serial.print("UPLOAD_ERROR:");
  Serial.println(reason);
}

void parseMessage(String line) {
  int colon = line.indexOf(':');
  String value = line.substring(colon + 1);
  value.trim();
  if (value.startsWith("\"") && value.endsWith("\"") && value.length() >= 2) {
    value = value.substring(1, value.length() - 1);
  }
  copyMessage(value, pendingScenes[currentUploadMode].message);
}

void parseFan(String line) {
  int colon = line.indexOf(':');
  String value = line.substring(colon + 1);
  value.trim();
  value.toUpperCase();

  if (value == "ON") {
    pendingScenes[currentUploadMode].fan = FAN_ON;
  } else if (value == "OFF") {
    pendingScenes[currentUploadMode].fan = FAN_OFF;
  } else {
    failUpload("ventilador invalido");
    return;
  }
  pendingScenes[currentUploadMode].fanSet = true;
}

void parseLeds(String line) {
  int colon = line.indexOf(':');
  String value = line.substring(colon + 1);
  value.trim();
  value.toUpperCase();

  if (value == "ON") {
    pendingScenes[currentUploadMode].ledPattern = LEDS_ON;
  } else if (value == "OFF") {
    pendingScenes[currentUploadMode].ledPattern = LEDS_OFF;
  } else if (value == "ALTERNANDOSE" || value == "ALTERNANDO") {
    pendingScenes[currentUploadMode].ledPattern = LEDS_ALTERNATING;
  } else {
    failUpload("leds invalidos");
    return;
  }
  pendingScenes[currentUploadMode].ledsSet = true;
}

void processCommand(String command) {
  byte mode = modeFromLine(command);
  if (mode != NO_MODE) {
    applyMode(mode);
    return;
  }

  if (command == "estado") {
    printStatus();
    return;
  }

  if (command == "abrir_puerta") {
    openDoor();
    return;
  }

  if (command == "cerrar_puerta") {
    closeDoor();
    return;
  }

  systemError = true;
  digitalWrite(led_rojo, HIGH);
  showLcd("Comando", "No valido");
  Serial.println("CMD_ERROR");
}

void applyMode(byte mode) {
  SceneConfig scene = readSceneFromEeprom(mode);
  if (scene.magic != EEPROM_MAGIC) {
    systemError = true;
    digitalWrite(led_rojo, HIGH);
    showLcd("Modo sin config", modeName(mode));
    Serial.println("MODE_ERROR");
    return;
  }

  activeMode = mode;
  systemError = false;
  digitalWrite(led_rojo, LOW);
  digitalWrite(led_azul, HIGH);
  digitalWrite(motor_ventilador, scene.fan == FAN_ON ? HIGH : LOW);
  applyLedPattern(scene.ledPattern);
  showLcd(scene.message, scene.fan == FAN_ON ? "Ventilador ON" : "Ventilador OFF");
  Serial.print("MODE_OK:");
  Serial.println(modeName(mode));
}

void applyLedPattern(byte pattern) {
  if (pattern == LEDS_ON) {
    setAllRoomLights(HIGH);
  } else if (pattern == LEDS_OFF) {
    setAllRoomLights(LOW);
  } else {
    alternatePhase = false;
    lastAlternateTick = 0;
    updateAlternatingLights();
  }
}

void updateAlternatingLights() {
  if (activeMode == NO_MODE) {
    return;
  }

  SceneConfig scene = readSceneFromEeprom(activeMode);
  if (scene.ledPattern != LEDS_ALTERNATING) {
    return;
  }

  unsigned long now = millis();
  if (now - lastAlternateTick < 450) {
    return;
  }

  lastAlternateTick = now;
  alternatePhase = !alternatePhase;
  digitalWrite(luces_sala, alternatePhase ? HIGH : LOW);
  digitalWrite(luces_comedor, alternatePhase ? LOW : HIGH);
  digitalWrite(luces_cocina, alternatePhase ? HIGH : LOW);
  digitalWrite(luces_bano, alternatePhase ? LOW : HIGH);
  digitalWrite(luces_habitacion, alternatePhase ? HIGH : LOW);
}

void setAllRoomLights(byte state) {
  digitalWrite(luces_sala, state);
  digitalWrite(luces_comedor, state);
  digitalWrite(luces_cocina, state);
  digitalWrite(luces_bano, state);
  digitalWrite(luces_habitacion, state);
}

void handleDoorButton() {
  bool reading = digitalRead(boton_puerta);
  if (reading != lastDoorButtonReading) {
    lastDoorDebounce = millis();
  }

  if ((millis() - lastDoorDebounce) > 40) {
    if (reading != stableDoorButtonState) {
      stableDoorButtonState = reading;
      if (stableDoorButtonState == LOW) {
        if (doorOpen) {
          closeDoor();
        } else {
          openDoor();
        }
      }
    }
  }

  lastDoorButtonReading = reading;
}

void openDoor() {
  doorOpen = true;
  doorServo.write(DOOR_OPEN_ANGLE);
  Serial.println("DOOR_OPEN");
}

void closeDoor() {
  doorOpen = false;
  doorServo.write(DOOR_CLOSED_ANGLE);
  Serial.println("DOOR_CLOSED");
}

void writeSceneToEeprom(byte mode, PendingScene scene) {
  SceneConfig stored;
  stored.magic = EEPROM_MAGIC;
  stored.fan = scene.fan;
  stored.ledPattern = scene.ledPattern;
  copyMessage(String(scene.message), stored.message);
  EEPROM.put(eepromAddress(mode), stored);
}

SceneConfig readSceneFromEeprom(byte mode) {
  SceneConfig scene;
  EEPROM.get(eepromAddress(mode), scene);
  return scene;
}

int eepromAddress(byte mode) {
  if (mode >= MODE_COUNT) {
    return -1;
  }
  return MODE_EEPROM_ADDRESS[mode];
}

void seedDefaultScenesIfNeeded() {
  SceneConfig first = readSceneFromEeprom(MODE_APAGAR_TODO);
  if (first.magic == EEPROM_MAGIC) {
    return;
  }

  writeDefaultScene(MODE_FIESTA, FAN_ON, LEDS_ALTERNATING, "Modo: FIESTA.");
  writeDefaultScene(MODE_RELAJADO, FAN_OFF, LEDS_ON, "Modo: RELAJADO.");
  writeDefaultScene(MODE_NOCHE, FAN_OFF, LEDS_OFF, "Modo: NOCHE.");
  writeDefaultScene(MODE_ENCENDER_TODO, FAN_ON, LEDS_ON, "Modo: TODO ON.");
  writeDefaultScene(MODE_APAGAR_TODO, FAN_OFF, LEDS_OFF, "Modo: TODO OFF.");
}

void writeDefaultScene(byte mode, byte fan, byte ledPattern, const char *message) {
  PendingScene scene;
  scene.touched = true;
  scene.fanSet = true;
  scene.ledsSet = true;
  scene.fan = fan;
  scene.ledPattern = ledPattern;
  copyMessage(String(message), scene.message);
  writeSceneToEeprom(mode, scene);
}

void resetPendingScenes() {
  for (byte i = 0; i < MODE_COUNT; i++) {
    pendingScenes[i].touched = false;
    pendingScenes[i].fanSet = false;
    pendingScenes[i].ledsSet = false;
    pendingScenes[i].fan = FAN_OFF;
    pendingScenes[i].ledPattern = LEDS_OFF;
    defaultMessageForMode(i, pendingScenes[i].message);
  }
}

byte modeFromLine(String line) {
  line.trim();
  if (line == "modo_fiesta") return MODE_FIESTA;
  if (line == "modo_relajado") return MODE_RELAJADO;
  if (line == "modo_noche") return MODE_NOCHE;
  if (line == "encender_todo") return MODE_ENCENDER_TODO;
  if (line == "apagar_todo") return MODE_APAGAR_TODO;
  return NO_MODE;
}

const char *modeName(byte mode) {
  if (mode == MODE_FIESTA) return "modo_fiesta";
  if (mode == MODE_RELAJADO) return "modo_relajado";
  if (mode == MODE_NOCHE) return "modo_noche";
  if (mode == MODE_ENCENDER_TODO) return "encender_todo";
  if (mode == MODE_APAGAR_TODO) return "apagar_todo";
  return "desconocido";
}

void defaultMessageForMode(byte mode, char *buffer) {
  if (mode == MODE_FIESTA) copyMessage("Modo: FIESTA.", buffer);
  else if (mode == MODE_RELAJADO) copyMessage("Modo: RELAJADO.", buffer);
  else if (mode == MODE_NOCHE) copyMessage("Modo: NOCHE.", buffer);
  else if (mode == MODE_ENCENDER_TODO) copyMessage("Modo: TODO ON.", buffer);
  else if (mode == MODE_APAGAR_TODO) copyMessage("Modo: TODO OFF.", buffer);
  else copyMessage("Modo activo", buffer);
}

bool startsWithIgnoreCase(String line, const char *prefix) {
  String normalizedLine = line;
  String normalizedPrefix = String(prefix);
  normalizedLine.toUpperCase();
  normalizedPrefix.toUpperCase();
  return normalizedLine.startsWith(normalizedPrefix);
}

void copyMessage(String value, char *destination) {
  value.trim();
  value.toCharArray(destination, MESSAGE_SIZE);
  destination[MESSAGE_SIZE - 1] = '\0';
}

void showLcd(const char *line1, const char *line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void setReadyState() {
  digitalWrite(led_azul, HIGH);
  digitalWrite(led_rojo, LOW);
  digitalWrite(led_verde, LOW);
  showLcd("Sistema listo", "Esperando...");
  Serial.println("READY");
}

void blinkGreenSuccess() {
  digitalWrite(led_rojo, LOW);
  for (byte i = 0; i < 3; i++) {
    digitalWrite(led_verde, HIGH);
    delay(180);
    digitalWrite(led_verde, LOW);
    delay(180);
  }
  showLcd("Configuracion", "guardada");
}

void printStatus() {
  Serial.print("STATUS:");
  Serial.print(modeName(activeMode));
  Serial.print(":");
  Serial.println(systemError ? "ERROR" : "OK");
}
