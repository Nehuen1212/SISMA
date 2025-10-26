#include <ESP8266WiFi.h>      
#include <ESP8266HTTPClient.h>  
#include <WiFiClientSecure.h>   
#include <Arduino.h> 
#include "modulos/ComunicacionWiFi.h" 
#include "modulos/CustomSensado.h"

const char* ssid = "Extensor - Depto";
const char* password = "nehuen2008";



Sensor sensor1;
bool bufferLleno;


void setup() {
    Serial.begin(115200);
    sensor1.init();
    
    WiFi.begin(ssid, password);
    Serial.print("\nConectando a WiFi");
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("\nWiFi conectado. IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nFalló la conexión WiFi.");
    }

    if (WiFi.status() == WL_CONNECTED) {
        crearArchivoCSV();
    }
    sensor1.reinicio();
}

void loop() {
    if(WiFi.status() == WL_CONNECTED){
        bufferLleno = sensor1.ActulizarBuffer();
        if(bufferLleno){
            escribirArchivoCSV(TAM_BUFFER, sensor1.dataBuffer);
        }  
    }
    
    
}