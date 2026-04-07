const int PIN_AUTH     = 2;   // botón de arranque
const int PIN_CLK_UP   = 5;   // pulsos adelante
const int PIN_CLK_DOWN = 6;   // pulsos atrás
const int PIN_H1       = 9;   // IN1
const int PIN_H2       = 10;  // IN2

// 1 pulso = 1 segundo
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

  // todo apagado al inicio
  digitalWrite(PIN_CLK_UP,  LOW);
  digitalWrite(PIN_CLK_DOWN, LOW);
  stopMotor();
}

void loop() {
  if (digitalRead(PIN_AUTH) == HIGH) {

    // adelante 15s
    digitalWrite(PIN_H1, HIGH);
    digitalWrite(PIN_H2, LOW);
    for (int i = 0; i < 15; i++) {
      if (digitalRead(PIN_AUTH) == LOW) { // para si sueltan
        stopMotor();
        return;
      }
      pulsePin(PIN_CLK_UP);
    }

    // atrás 10s
    digitalWrite(PIN_H1, LOW);
    digitalWrite(PIN_H2, HIGH);
    for (int i = 0; i < 10; i++) {
      if (digitalRead(PIN_AUTH) == LOW) { // idem
        stopMotor();
        return;
      }
      pulsePin(PIN_CLK_DOWN);
    }

    stopMotor();

    // espera a que suelten antes del siguiente ciclo
    while (digitalRead(PIN_AUTH) == HIGH) {
      delay(10);
    }

  } else {
    stopMotor(); // sin señal, frenado
  }
}