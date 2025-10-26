#include "ComunicacionWiFi.h" 

String archivoUrl;

void crearArchivoCSV() {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    WiFiClientSecure client;
    HTTPClient http;

    client.setInsecure(); 
    
    http.setTimeout(15000); 
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    String url = APP_SCRIPT_URL;
    url += "?action=createFile";
    
    http.begin(client, url); 

    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
        archivoUrl = http.getString();  
        archivoUrl.trim();      
        Serial.println("URL: " + archivoUrl);
    } else {
        Serial.print("Error en la solicitud HTTP. Código: ");
        Serial.println(httpResponseCode);
        Serial.print("Mensaje de error: ");
        Serial.println(http.errorToString(httpResponseCode)); 
    }
    
    http.end();

}

String urlEncode(const String& str) {
    String encodedString = "";
    char c;
    
    for (unsigned int i = 0; i < str.length(); i++) {
        c = str.charAt(i);
        if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encodedString += c;
        } else if (c == ' ') {
            encodedString += '+'; 
        } else {
            encodedString += '%';
            char buff[3];
            sprintf(buff, "%02X", (byte)c);
            encodedString += buff;
        }
    }
    return encodedString;
}


void escribirArchivoCSV(int buffer_size, MpuData datos[]){

    if(WiFi.status() != WL_CONNECTED){
        return;
    }
    
    Serial.printf("Memoria libre antes de datosString: %u bytes\n", ESP.getFreeHeap());

    String datosString = "";
    
    for (int i = 0; i < buffer_size; i++) {
        datosString += String(datos[i].instante, 2); 
        datosString += ","; 
        datosString += String(datos[i].angleX, 3);
        datosString += ","; 
        datosString += String(datos[i].angleY, 3);
        datosString += ","; 
        datosString += String(datos[i].angleZ, 3);
        
        if (i < buffer_size - 1) {
            datosString += ","; 
        }
    }
    
    Serial.printf("Memoria libre despues de datosString (%d chars): %u bytes\n", datosString.length(), ESP.getFreeHeap());

    if (archivoUrl.length() == 0) {
        return;
    }

    WiFiClientSecure client;
    HTTPClient http;
    client.setInsecure();
    http.setTimeout(15000);
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    
    String url = APP_SCRIPT_URL;
    url += "?action=write";
    url += "&url=" + urlEncode(archivoUrl); 
    
    Serial.println("Inicia Peticion...");
    Serial.printf("Memoria antes de http.begin: %u bytes\n", ESP.getFreeHeap());
    
    http.begin(client, url); 

    http.addHeader("Content-Type", "text/plain");

    int httpResponseCode = http.POST(datosString);
    
    Serial.printf("Memoria despues de http.POST: %u bytes\n", ESP.getFreeHeap());

    if (httpResponseCode > 0) {
        String payload = http.getString();
        Serial.println("Respuesta del servidor: " + payload);
    } 
    else if(httpResponseCode == 0){
        Serial.println("Tiempo de respuesta agotado (Timeout).");
    }
    else {
        Serial.print("Error de Conexión/Protocolo. Código: ");
        Serial.println(httpResponseCode);
        Serial.print("Mensaje: ");
        Serial.println(http.errorToString(httpResponseCode));
    }
    
    http.end();
    delay(5000); 
}
