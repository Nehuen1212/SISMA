#include "CustomSensado.h"

Sensor::Sensor() : mpu6050(Wire) {
}

void Sensor::init() {
        Wire.begin(); 
        mpu6050.begin(); 
        mpu6050.calcGyroOffsets(true); 
}

bool Sensor::ActulizarBuffer(){
    unsigned long currentMillis = millis();
    if(currentMillis - previousMillis >= INTERVALO_MS){
        previousMillis = currentMillis;

        mpu6050.update();
        dataBuffer[bufferIndex].instante = tiempo;
        dataBuffer[bufferIndex].angleX = mpu6050.getAngleX();
        dataBuffer[bufferIndex].angleY = mpu6050.getAngleY();
        dataBuffer[bufferIndex].angleZ = mpu6050.getAngleZ();

        /*
        Serial.print("\n T: ");
        Serial.print(dataBuffer[bufferIndex].instante);
        Serial.print(", X: ");
        Serial.print(dataBuffer[bufferIndex].angleX);
        Serial.print(", Y: ");
        Serial.print(dataBuffer[bufferIndex].angleY);
        Serial.print(", Z: ");
        Serial.println(dataBuffer[bufferIndex].angleZ);
        */

        bufferIndex++;
        tiempo += INTERVALO_MS;
        if(bufferIndex >= bufferSize){
            bufferIndex = 0;
            return true;
        }
    return false;
    }
    return false;
}

MpuData Sensor::obtenerDataBuffer(int index){
    return dataBuffer[index];
}

void Sensor::reinicio(){
    tiempo = 0;
}

