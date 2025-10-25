import re
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import sys
import csv
import os

# --- 1. Función para Seleccionar y Leer el Archivo ---

def select_gcode_file():
    """Abre un diálogo para seleccionar un archivo .gcode o .txt y lee su contenido."""
    # Configuración de Tkinter para el diálogo
    root = tk.Tk()
    root.withdraw() 
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo G-Code",
        filetypes=(("Archivos G-Code", "*.gcode"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    
    if not file_path:
        print("⛔ No se seleccionó ningún archivo. Saliendo del programa.")
        sys.exit()
    
    try:
        with open(file_path, 'r') as f:
            gcode_data = f.read()
        return gcode_data
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        sys.exit()

# ----------------------------------------------------------------------
## Procesamiento y Guardado en CSV
# ----------------------------------------------------------------------

def process_and_save_gcode_data():
    """
    Lee el G-code, procesa los movimientos del eje X y guarda los resultados en un archivo CSV.
    También devuelve los datos para la graficación.
    """
    # 2.1 Leer el G-code
    gcode_data = select_gcode_file()
    
    # Nombre del archivo de salida
    output_filename = "custom/datosGraficos/movimientos_gcode.csv"

    # Expresión regular para encontrar comandos G0/G1 con X o G90/G91
    gcode_pattern = re.compile(r'^(G[01])(?:\s+X([\-\d\.]+))|^(G9[01])', re.MULTILINE | re.IGNORECASE)

    # Estado inicial de la máquina
    current_x = 0.0
    is_absolute_mode = True  
    step = 0

    # Listas para almacenar los datos (para el gráfico)
    step_number = [0]
    x_positions = [current_x]

    # Lista para almacenar los datos del CSV
    csv_data = []

    # Añadir la fila inicial de datos (Paso 0)
    csv_data.append([0, "ABS", "Inicio", 0.0, 0.0]) # Paso, Modo, Movimiento, Valor X, Posición Final

    # Imprimir encabezado para la consola
    print("\n" + "="*70)
    print("RESUMEN DE MOVIMIENTOS G-CODE (EJE X)")
    print("="*70)
    print(f"{'PASO':<6}{'MODO':<8}{'G-CODE MOV.':<12}{'VALOR X':<15}{'POSICIÓN FINAL (X)':<20}")
    print("-" * 70)
    print(f"{0:<6}{'ABS':<8}{'N/A':<12}{0.0:<15.2f}{current_x:<20.2f}")


    # 2.2 Procesar el G-code línea por línea
    for line in gcode_data.splitlines():
        match = gcode_pattern.search(line)

        if match:
            # Capturar comandos G0 o G1
            if match.group(1):
                g_command = match.group(1).upper()
                x_value_str = match.group(2)

                if x_value_str is not None:
                    try:
                        x_move = float(x_value_str)
                        mode_str = "ABS" if is_absolute_mode else "REL"
                        
                        gcode_movement = f"{g_command} X{x_move}"

                        if is_absolute_mode:
                            # G90 (Absoluto)
                            current_x = x_move
                        else:
                            # G91 (Relativo)
                            current_x += x_move

                        # Registrar la nueva posición
                        step += 1
                        x_positions.append(current_x)
                        step_number.append(step)
                        
                        # Añadir a la lista de CSV
                        csv_data.append([step, mode_str, gcode_movement, x_move, current_x])
                        
                        # Imprimir el dato en la consola
                        print(f"{step:<6}{mode_str:<8}{gcode_movement:<12}{x_move:<15.2f}{current_x:<20.2f}")

                    except ValueError:
                        continue # Ignorar líneas mal formadas

            # Capturar comandos G90 o G91
            elif match.group(3):
                coordinate_mode = match.group(3).upper()
                if coordinate_mode == 'G90':
                    is_absolute_mode = True
                elif coordinate_mode == 'G91':
                    is_absolute_mode = False

    # 2.3 Guardar los datos en el archivo CSV
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Escribir el encabezado del CSV
            csv_writer.writerow(["PASO", "MODO", "G-CODE MOVIMIENTO", "VALOR X DE ENTRADA", "POSICION FINAL X"])
            
            # Escribir todas las filas de datos
            csv_writer.writerows(csv_data)
            
        print("-" * 70)
        print(f"✅ Datos guardados con éxito en: {os.path.abspath(output_filename)}")
        print(f"Total de movimientos procesados: {step}")
        print(f"Posición final del eje X: {current_x:.2f}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error al escribir el archivo CSV: {e}")
        
    # Devolver los datos para la graficación
    return step_number, x_positions

# ----------------------------------------------------------------------
## Ejecución y Graficación
# ----------------------------------------------------------------------

def run_gcode_plotter_csv():
    """Función principal que procesa, guarda en CSV y grafica."""
    
    # Procesar los datos y obtener las listas para graficar
    step_number, x_positions = process_and_save_gcode_data()
    
    # 3. Generación del Gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(step_number, x_positions, linestyle='-', color='blue', linewidth=1)
    
    if len(step_number) > 1:
        # Puntos inicial y final
        plt.plot(step_number[0], x_positions[0], 'go', label=f'Inicio (X={x_positions[0]:.2f})')
        plt.plot(step_number[-1], x_positions[-1], 'ro', label=f'Fin (X={x_positions[-1]:.2f})')


    plt.title('Gráfico Estático de Todos los Movimientos del Eje X')
    plt.xlabel('Paso del Movimiento (Comando G0/G1)')
    plt.ylabel('Posición del Eje X')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    plt.legend()
    plt.show()

# --- Ejecutar el Programa ---
if __name__ == '__main__':
    run_gcode_plotter_csv()