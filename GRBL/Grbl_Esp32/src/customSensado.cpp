#include "customSensado.h"

TaskHandle_t taskEnviarDatos = NULL; // Handle para poder controlar la tarea
volatile bool continuarTarea = false; // Flag para controlar ejecución

void enviarDatos(void *pvParameters){     
    float datos[100];
    int contador = 0;

    while (1) {
        if (continuarTarea) {
            datos[contador] = contador * 10;
            contador++;
            vTaskDelay(1000 / portTICK_PERIOD_MS); // cada 1s
            
        } else {
            Serial.println("Tarea detenida por comando");
            vTaskDelete(NULL); // mata la tarea
        }
    }
}

void M70() {
    if (taskEnviarDatos == NULL) { // solo crear si no está corriendo
        continuarTarea = true; 
        xTaskCreatePinnedToCore(
            enviarDatos,
            "SendTask",
            4096,
            NULL,
            1,
            &taskEnviarDatos,
            0 // Core 0
        );
    } else {
        continuarTarea = true; // si ya existe, simplemente reanuda
    }
}

void M71() {
    continuarTarea = false; // detener en el próximo ciclo
    taskEnviarDatos = NULL; // liberar handle
}