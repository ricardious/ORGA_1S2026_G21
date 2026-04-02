const int PIN_AUTH     = 2;   // Señal de habilitación
const int PIN_CLK_UP   = 5;   // Pulsos para el contador subiendo
const int PIN_CLK_DOWN = 6;   // Pulsos para el contador bajando
const int PIN_H1       = 9;   // IN1
const int PIN_H2       = 10;  // IN2

// 1 pulso = 1 segundo (500ms HIGH + 500ms LOW)
void pulsePin(int pin) {
  digitalWrite(pin, HIGH);
  delay(500);
  digitalWrite(pin, LOW);
  delay(500);
}

void stopMotor() {
  digitalWrite(PIN_H1, LOW);
  digitalWrite(PIN_H2, LOW);
}

void setup() {
  pinMode(PIN_AUTH, INPUT);
  pinMode(PIN_CLK_UP,   OUTPUT);
  pinMode(PIN_CLK_DOWN, OUTPUT);
  pinMode(PIN_H1, OUTPUT);
  pinMode(PIN_H2, OUTPUT);

  // Todo apagado al arrancar
  digitalWrite(PIN_CLK_UP,  LOW);
  digitalWrite(PIN_CLK_DOWN, LOW);
  stopMotor();
}

void loop() {

  if (digitalRead(PIN_AUTH) == HIGH) {

    // --- Ida: 15 seg hacia adelante ---
    digitalWrite(PIN_H1, HIGH);
    digitalWrite(PIN_H2, LOW);

    for (int i = 0; i < 15; i++) {
      if (digitalRead(PIN_AUTH) == LOW) { // corte de emergencia
        stopMotor();
        return;
      }
      pulsePin(PIN_CLK_UP);
    }

    // --- Vuelta: 10 seg en reversa ---
    digitalWrite(PIN_H1, LOW);
    digitalWrite(PIN_H2, HIGH);

    for (int i = 0; i < 10; i++) {
      if (digitalRead(PIN_AUTH) == LOW) { // corte de emergencia
        stopMotor();
        return;
      }
      pulsePin(PIN_CLK_DOWN);
    }

    stopMotor();

    // Esperar a que suelten el botón antes del siguiente ciclo
    while (digitalRead(PIN_AUTH) == HIGH) {
      delay(10);
    }

  } else {
    stopMotor(); // sin habilitación, motor frenado
  }
}