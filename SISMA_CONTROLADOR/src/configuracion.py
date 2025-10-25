import json
import os

def aplicar_configuracion(amp_max, amp_min, aceleracion, velocidad, configuracion):
       
        
        configuracion["amplitud_maxima"] = float(amp_max)
        configuracion["amplitud_minima"] = float(amp_min)
        configuracion["aceleracion"] = float(aceleracion)
        configuracion["velocidad"] = float(velocidad)
            
        with open("data/configuracion.json", "w") as f:
                json.dump(configuracion, f)
            
        print(f"Configuración Aplicada:")
        print(f"Amplitud Máxima: {configuracion["amplitud_maxima"]}")
        print(f"Amplitud Mínima: {configuracion["amplitud_minima"]}")
        print(f"Aceleración: {configuracion["aceleracion"]}")
        print(f"Velocidad: {configuracion["velocidad"]}")
            
           
        
            
        
def cargar_configuracion():
    configuracion = {
            "amplitud_maxima": 300,
            "amplitud_minima": 3,
            "aceleracion": 1200,
            "velocidad": 1500
        }
    try:
        with open("data/configuracion.json", "r") as f:
            configuracion = json.load(f)
    except:
        pass
            
    return configuracion
