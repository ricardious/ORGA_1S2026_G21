const int PIN_AUTH     = 2;   // señal de habilitación del comparador
const int PIN_CLK_UP   = 5;   // reloj contador ascendente
const int PIN_CLK_DOWN = 6;   // reloj contador descendente
const int PIN_H1       = 9;   // dirección 1 del puente H
const int PIN_H2       = 10;  // dirección 2 del puente H

// genera pulsos de reloj con ciclo de trabajo al 50%
void sendClockCycles(int pin, int cycles, int halfPeriodMs) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(pin, HIGH);
    delay(halfPeriodMs);
    digitalWrite(pin, LOW);
    delay(halfPeriodMs);
  }
}

// detiene el sistema, todo al LOW
void haltSystem() {
  digitalWrite(PIN_H1, LOW);
  digitalWrite(PIN_H2, LOW);
}

// lleva el contador a posición cero antes de terminar el ciclo
void resetCounter(int pin, int remaining) {
  sendClockCycles(pin, remaining, 5);
}

void setup() {
  pinMode(PIN_AUTH, INPUT);
  pinMode(PIN_CLK_UP,   OUTPUT);
  pinMode(PIN_CLK_DOWN, OUTPUT);
  pinMode(PIN_H1, OUTPUT);
  pinMode(PIN_H2, OUTPUT);

  // estado inicial limpio
  digitalWrite(PIN_CLK_UP,  LOW);
  digitalWrite(PIN_CLK_DOWN, LOW);
  haltSystem();
}

void loop() {
  if (digitalRead(PIN_AUTH) == HIGH) {
    delay(50); // filtro de rebote

    if (digitalRead(PIN_AUTH) == HIGH) {
      while (digitalRead(PIN_AUTH) == HIGH) {
        bool cycleAborted = false;

        // --- secuencia de avance: 15 segundos ---
        digitalWrite(PIN_H1, HIGH);
        digitalWrite(PIN_H2, LOW);

        for (int t = 0; t < 15 && !cycleAborted; t++) {
          if (digitalRead(PIN_AUTH) == LOW) {
            haltSystem();
            resetCounter(PIN_CLK_UP, 14 - t); // regresa el contador a cero
            cycleAborted = true;
          } else {
            sendClockCycles(PIN_CLK_UP, 1, 500);
          }
        }

        // --- secuencia de retorno: 10 segundos ---
        if (!cycleAborted) {
          digitalWrite(PIN_H1, LOW);
          digitalWrite(PIN_H2, HIGH);

          for (int t = 0; t < 10 && !cycleAborted; t++) {
            if (digitalRead(PIN_AUTH) == LOW) {
              haltSystem();
              resetCounter(PIN_CLK_DOWN, 9 - t); // regresa el contador a cero
              resetCounter(PIN_CLK_DOWN, 1);      // pulso de cierre de ciclo
              cycleAborted = true;
            } else {
              sendClockCycles(PIN_CLK_DOWN, 1, 500);
            }
          }
        }

        if (!cycleAborted) {
          // pulso de cierre de ciclo antes de reiniciar la secuencia
          sendClockCycles(PIN_CLK_DOWN, 1, 5);
          haltSystem();
          delay(1000);  // estabilización después de frenar
        }

        if (cycleAborted) {
          break;
        }
      }

      delay(200); // margen de debounce al soltar
    }
  } else {
    haltSystem(); // sin habilitación el sistema queda frenado
  }
}
