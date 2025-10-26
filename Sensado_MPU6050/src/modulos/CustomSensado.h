#ifndef CUSTOM_SENSADO_H
#define CUSTOM_SENSADO_H

#include "DatosMPU.h"
#include <MPU6050_tockn.h>
#include <Wire.h>
#include <Arduino.h>



class Sensor {
private:
    static const int bufferSize = TAM_BUFFER;
    static const long INTERVALO_MS = 10;
    int bufferIndex = 0; 
    unsigned long previousMillis = 0;
    MPU6050 mpu6050;
    

public:
    int tiempo;
    MpuData dataBuffer[bufferSize];
    Sensor();
    void init();
    bool ActulizarBuffer(); 
    MpuData obtenerDataBuffer(int index);
    void reinicio();
};


#endif