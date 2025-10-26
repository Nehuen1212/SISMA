#ifndef COMUNICACIONWIFI_H
#define COMUNICACIONWIFI_H


#include <ESP8266WiFi.h>      
#include <ESP8266HTTPClient.h>  
#include <WiFiClientSecure.h>   
#include <Arduino.h> 
#include "Sensado/DatosMPU.h"


#define APP_SCRIPT_URL "https://script.google.com/macros/s/AKfycbxvvAmjkD8IVuUeofIpvtQtWTRXj4dWccl7VyP4f3BTTjGPPuz-B1-BamyCxwUMAo5U/exec"
extern String archivoUrl;


void crearArchivoCSV();
void escribirArchivoCSV(int buffer_size, MpuData datos[]);
String urlEncode(const String& str);
#endif 