import serial
import time
import threading
from enum import Enum

class controlSerial:
    class Estado(Enum):
        Reposo = 0
        Pausado = 1
        Bloqueado = 2
        Detenido = 3
        Ejecutando = 4
        Desconectado = 5
    
    def __init__(self, baudrate=115200):
        self.puertoCom = None  
        self.baudrate = baudrate
        self.conectado = False
        self.estado_conexion = self.Estado.Desconectado
        
        self.hilo_monitoreo = None
        self._detener_monitoreo = threading.Event()
        self._lock_estado = threading.Lock()
        
        self.envio_archivo = False
            
    def _iniciar_monitoreo(self):
        self._detener_monitoreo.clear()
        self.hilo_monitoreo = threading.Thread(target=self._hilo_monitoreo_estado, daemon=True)
        self.hilo_monitoreo.start()

    def _hilo_monitoreo_estado(self):
        
        while not self._detener_monitoreo.is_set():
            
            envio_activo = False
            with self._lock_estado:
                envio_activo = self.envio_archivo
                
            if envio_activo:
                time.sleep(0.1)
                continue
            
            if self.conectado and self.puertoCom and self.puertoCom.is_open:
                try:
                    self.puertoCom.write(b'?')
                    respuesta = self.puertoCom.readline().decode(errors="ignore").strip()
                    if respuesta:
                        self._procesar_respuesta_estado(respuesta)
                except Exception as e:
                    with self._lock_estado:
                         self.estado_conexion = self.Estado.Desconectado
                    self._detener_monitoreo.set()
                    break
            time.sleep(0.2) 
        

    def _procesar_respuesta_estado(self, respuesta):
        nuevo_estado = None
        if "alarm" in respuesta.lower():
            nuevo_estado = self.Estado.Bloqueado
        elif "idle" in respuesta.lower():
            nuevo_estado = self.Estado.Reposo
        elif "hold" in respuesta.lower():
            nuevo_estado = self.Estado.Pausado
        elif "run" in respuesta.lower():
            nuevo_estado = self.Estado.Ejecutando
        
        if nuevo_estado:
            with self._lock_estado:
                self.estado_conexion = nuevo_estado
        
    def conectar(self, puerto):
        if self.conectado:
            print(f"La conexión ya está activa en {self.puertoCom.port}.")
            return True

        try:
            self.puertoCom = serial.Serial(puerto, self.baudrate, timeout=1)
            time.sleep(1) 
            self.puertoCom.write(b"?\n")
            
            conectado = False
            linea = ""
            for _ in range(20):
                linea = self.puertoCom.readline().decode('utf-8', errors='ignore').strip()
                if linea:
                    print(f"Recibido: {linea}")
                    if "Grbl" in linea or "grbl" in linea or "VER" in linea or "Idle" in linea or "Alarm" in linea:
                        conectado = True
                        break

            if conectado:
                self.conexion_activa = True
                if("Alarm" in linea):
                    self.desbloquear()
                print(f"✅ Conexión exitosa al puerto {puerto} con baudios {self.baudrate}.")
                self.conectado = True
                self.estado_conexion = self.Estado.Reposo
                self._iniciar_monitoreo()
                return True
            else:
                print("❌ No se recibió mensaje de bienvenida de GRBL. Cerrando puerto y abortando conexión.")
                if self.puertoCom and self.puertoCom.is_open:
                    self.puertoCom.close()
                self.puertoCom = None
                return False

        except serial.SerialException as e:
            print(f"❌ ERROR: No se pudo conectar a {puerto}. Detalles: {e}")
            self.puertoCom = None
            return False

    def desconectar(self):
        self._detener_monitoreo.set()
        if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
            self.hilo_monitoreo.join()
            
        if self.puertoCom and self.puertoCom.is_open:
            self.puertoCom.close()
            print("🛑 Conexión serial cerrada.")
            self.conectado = False
        else:
            print("La conexión no estaba activa.")
    
    def _enviar_comando(self, comando):
        if not self.conectado:
            return "ERROR: No conectado."
        if self.estado_conexion == self.Estado.Pausado:
            return "Pausa activa -> Feed Hold"

        linea_a_enviar = (comando.strip() + '\n').encode('utf-8')
        
        try:
            self.puertoCom.flushInput()
            
            self.puertoCom.write(linea_a_enviar)
            
            respuestas = []
            while self.puertoCom.in_waiting > 0:
                linea = self.puertoCom.readline().decode(errors="ignore").strip()
                if linea:
                    respuestas.append(linea)
            
            if not respuestas:
                linea = self.puertoCom.readline().decode(errors="ignore").strip()
                if linea:
                    respuestas.append(linea)
            
            if respuestas:
                return f"RESPUESTA: {comando.strip()} -> {'; '.join(respuestas)}"
            else:
                return f"SIN RESPUESTA: {comando.strip()}"
                
        except Exception as e:
            return f"ERROR de transmisión: {e}"

    def mover_eje_x(self, pasos, velocidad_f=3000):
        self._enviar_comando("G91")
        comando = f"G1 X{pasos} F{velocidad_f}"
        resultado = self._enviar_comando(comando)
        print(f"{resultado}")
        return resultado
        
    def ejecutar_comando(self, gcode_file_path=None):
        def run():
            if not self.conectado:
                print("ERROR: No hay conexión activa")
                return False
            
            # Reanudar si está pausado
            if self.estado_conexion == self.Estado.Pausado:
                self.puertoCom.write(b"~")
                self.estado_conexion = self.Estado.Ejecutando
                print("Se ha despausado -> Feed Hold: False\n")
                return
            
            if gcode_file_path:
                with self._lock_estado:
                    self.envio_archivo = True
                try:
                    with open(gcode_file_path, 'r') as archivo:
                        self.estado_conexion = self.Estado.Ejecutando
                        print(f"Programa: Iniciando ejecución de {gcode_file_path}")
                        for linea in archivo:
                            
                            while self.estado_conexion == self.Estado.Pausado:
                                time.sleep(0.1)
                            
                            if self.estado_conexion == self.Estado.Detenido:
                                self.estado_conexion = self.Estado.Reposo
                                break
                                
                            linea = linea.strip()
                            if linea and not linea.startswith('(') and not linea.startswith(';'):
                                resultado = self._enviar_comando(linea)
                                print(resultado)
                                
                        self.estado_conexion = self.Estado.Reposo
                        print("Programa finalizado.")
                    
                except FileNotFoundError:
                    print(f"ERROR: Archivo {gcode_file_path} no encontrado")
                except Exception as e:
                    print(f"ERROR leyendo archivo: {e}")
                finally:
                    with self._lock_estado:
                        self.envio_archivo = False
                        self.estado_conexion = self.Estado.Reposo
            else:
                print("Selecciona un archivo primero")
                
        hilo = threading.Thread(target=run)
        hilo.daemon = True
        hilo.start()

    def pausar_comando(self):
        if self.conectado:
            
            if self.estado_conexion == self.Estado.Pausado: 
                self.puertoCom.write(b"~")
                print("Se ha despausado -> Feed Hold: False")
                
            else:
                self.puertoCom.write(b'!')
                print("Comando: Pausa (Feed Hold)")
                
        else:
            print("ERROR: No hay conexión activa")

    def detener_comando(self):
        if self.conectado and self.estado_conexion == self.Estado.Ejecutando:
            self.estado_conexion = self.Estado.Detenido
            self.puertoCom.flushInput()
            print("Comando 'STOP'")
        else:
            print("ERROR: No hay conexión activa o no hay ejecución activa")

    def desbloquear(self):
        if not self.conectado:
            print("ERROR: No hay conexión activa")
            return False
            
        if self.estado_conexion != self.Estado.Bloqueado:
            print("El dispositivo no está en estado de Bloqueado (Alarm).")
            return False

        try:
            print("🔓 Desbloqueando GRBL...")
            self.puertoCom.write(b'$X\n')
            time.sleep(0.7)
            
            respuesta = self.puertoCom.readline().decode(errors="ignore").strip()
            print(f"   Respuesta: {respuesta}")
            
            if 'ok' in respuesta.lower():
                print("✅ GRBL desbloqueado exitosamente")
                return True
            else:
                print(f"⚠️ Respuesta inesperada al desbloquear: {respuesta}")
                return False
                
        except Exception as e:
            print(f"❌ Error al desbloquear: {e}")
            return False
    
    def reset_comando(self):
        self.puertoCom.write(bytes([24]))
        while self.puertoCom.in_waiting > 0:
                linea = self.puertoCom.readline().decode(errors="ignore").strip()
                if linea:
                    print(linea)
                    
    def home_comando(self):
        resultado = self._enviar_comando("$H")
        print(f"{resultado}")
        return True
        
    def enviar_comando_manual(self, comando):
        if comando: 
            resultado = self._enviar_comando(comando)
            print(f"{resultado}")
            return resultado
        else:
            print("ERROR: Comando vacío")
            return None
    
      
    
    def retornar_estado(self):
        if not self.conectado:
            return self.Estado.Desconectado.value
        with self._lock_estado:
            return self.estado_conexion.value