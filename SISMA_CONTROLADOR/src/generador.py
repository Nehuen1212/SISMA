import datetime
from random import randint

# VARIABLES DE SIMULADOR
maximaDistancia = 110  # Distancia total de viaje en el eje X en mm
nivelacion_comando = "$H"  # Comando para homing

def generar_gcode_sismico(magnitud, repeticiones,configuracion,ruta):
            magnitud_float = float(magnitud)
            repeticiones_float = float(repeticiones)       
                      
            
            
            nivelacion_comando = "$H"
            max_amplitud = (configuracion["amplitud_maxima"] / 9.0) * magnitud_float
            min_amplitud = (max_amplitud * 0.7) 
            if(min_amplitud < configuracion["amplitud_minima"]): min_amplitud = configuracion["amplitud_minima"]
            aceleracion = configuracion["aceleracion"]
            velocidad = configuracion["velocidad"] 
            
            with open(f"{ruta}", "w") as file:
                
                    file.write("; Generado por Generador G-CODES SISMOS de SISMA\n")
                    file.write(f"; Fecha y hora: {datetime.datetime.now()}\n")
                    

                    # Iniciar nivelacion
                    file.write(f"{nivelacion_comando}\n")

                    # Mover al punto 0
                    centroPos = maximaDistancia / 2
                    
                    file.write(f"$120 = 500\n")
                    file.write(f"G0 X{centroPos} F5000\n")
                    file.write("G91\n")  # Modo relativo
                    file.write("G4 P1\n") #Espera un segundo
                    file.write(f"$120 = {aceleracion}\n")
                    
                    # Generar movimientos aleatorios 
                    for i in range(int(repeticiones_float/2)):                    
                        # Velocidad aleatoria
                        
                        # Amplitud aleatoria
                        amplitud = randint(int(min_amplitud), int(max_amplitud))
                        
                        
                        #Elige direccion dependiendo de la anterior
                        if i%2 == 0 or i == 0 :
                            direccion = -1
                        else :
                            direccion = 1
                        
                        
                                
                        file.write(f"G1 X{amplitud * direccion} F{velocidad}\n")
                        file.write(f"G1 X{amplitud/2 * (-direccion)} F{velocidad/2}\n")
                        

                    # Volver a modo absoluto y al origen
                    file.write("G4 P1\n") #Espera un segundo 
                    file.write("G90\n") 
                            
                    file.write(";\n")
                    file.write("; Fin de la simulación\n")

            print(f"Archivo G-code guardado.") 
                 
                        
            
            
        