import tkinter as tk
from tkinter import ttk, PhotoImage, scrolledtext, filedialog, simpledialog
import os 
import sys
from src.generador import generar_gcode_sismico
from src.configuracion import cargar_configuracion, aplicar_configuracion
from src.serialCOM import controlSerial
from serial.tools import list_ports

# Rutas de imagen - Se asume que existen
logoVentana = "assets/Logo_3.png"
logoCuerpo = "assets/Logo.png"

serialCOM = controlSerial()

# Variables globales o de clase para los valores de Ejecución
velocidad_ejecucion_var = None 
aceleracion_ejecucion_var = None

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass

class Ventana:
    
    def __init__(self):
        global velocidad_ejecucion_var, aceleracion_ejecucion_var
        self.ruta_archivo = ""
        self.configuracion = cargar_configuracion()
        self.root = tk.Tk()
        self.root.title("SISMA GCODE CONTROLADOR")
        self.root.geometry("1000x800") 
        self.root.resizable(True, True) 
        self.root.configure(bg="#1b1212")
        
        # Estilo del Notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2a2a2a', foreground='#ff6b35', 
                        font=("Segoe UI", 11, "bold")) 
        style.map('TNotebook.Tab', background=[('selected', "#f0cfc3")], 
                  foreground=[('selected', '#000000')])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5) 
        
        self.logo(logoVentana)
        
        
        # Inicializar variables de control para la pestaña Ejecución
        self.velocidad_ejecucion_var = tk.StringVar(value=str(self.configuracion.get("velocidad", "1000")))
        self.movimiento_ejecucion_var = tk.StringVar(value=str(10))

        # Asignar a las variables globales
        velocidad_ejecucion_var = self.velocidad_ejecucion_var
        # movimiento_ejecucion_var = self.movimiento_ejecucion_var # Esta variable no es global en el código original, se mantiene como estaba

        # Crear las pestañas
        self.crear_pestana_gcode()
        self.crear_pestana_ejecucion() 
        
    def crear_pestana_gcode(self):
        """Crea la pestaña principal para generar G-Code sísmico con todos los parámetros"""
        # Estilo para inputs
        estilo_input = {
            "font": ("Segoe UI", 12), 
            "bg": "#1a1a1a",
            "fg": "#ffffff",
            "insertbackground": "#ff6b35",
            "relief": "solid",
            "bd": 2,
            "highlightthickness": 2,
            "highlightcolor": "#ff6b35",
            "highlightbackground": "#666"
        }
        
        frame_pestana = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(frame_pestana, text="GENERADOR G-CODE") 
        
        # Frame contenedor principal - Se mantiene el place relativo, pero se asegura la expansión interna
        frame_contenido = tk.Frame(frame_pestana, bg="#1a1a1a", relief="solid", bd=3)
        # Se cambia place por pack para que se expanda dentro de frame_pestana si el notebook se expande
        # frame_contenido.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75) 
        frame_contenido.pack(fill="both", expand=True, padx=50, pady=50) # Modificación importante aquí y en la línea de abajo
        
        # Contenedor interno - Debe expandirse dentro del frame_contenido
        frame_interno = tk.Frame(frame_contenido, bg="#2a2a2a", relief="ridge", bd=5)
        frame_interno.pack(fill="both", expand=True, padx=10, pady=10) # Modificación: expand=True
        
        # --- MODIFICACIONES INICIAN AQUÍ ---
        
        # Frame principal de organización, contendrá: [Logo/Título] [Parámetros]
        frame_organizacion = tk.Frame(frame_interno, bg="#2a2a2a")
        frame_organizacion.pack(fill="both", expand=True, padx=20, pady=10) # Modificación: expand=True
        
        # Configurar GRID: 3 columnas, 1 para el logo (fijo) y 2 para los parámetros (expandibles)
        frame_organizacion.grid_columnconfigure(0, weight=0) # Columna del logo (fijo)
        frame_organizacion.grid_columnconfigure(1, weight=1) # Columna de parámetros izquierda (expandible)
        frame_organizacion.grid_columnconfigure(2, weight=1) # Columna de parámetros derecha (expandible)
        frame_organizacion.grid_rowconfigure(0, weight=1)    # Fila 0 (Parámetros) le damos peso
        frame_organizacion.grid_rowconfigure(1, weight=0)    # Fila 1 (Botón Generar) peso fijo

        # ============ COLUMNA LOGO ============
        frame_logo_container = tk.Frame(frame_organizacion, bg="#2a2a2a")
        # El logo va en la primera columna y se pega a la esquina superior (nw)
        frame_logo_container.grid(row=0, column=0, rowspan=2, padx=15, pady=10, sticky="nw")

        # ... (Contenido del logo se mantiene igual)
        try:
            imagen = PhotoImage(file=logoCuerpo).subsample(10,10) 
            label = tk.Label(frame_logo_container, text="SISMA", image=imagen, bg=frame_logo_container['bg'])
            label.image = imagen    
        except:
            label = tk.Label(frame_logo_container, text="SISMA", bg=frame_logo_container['bg'])
            pass
           
                    
        self.Titulo = tk.Label(frame_logo_container, text="SISMA", bg=frame_logo_container['bg'], 
                             fg="#ff6b35", font=("Rajdhani", 25, "bold"))
        label.pack(side="top")
        self.Titulo.pack(side="bottom", padx=(15,0))
        
        # ============ COLUMNA IZQUIERDA DE PARÁMETROS ============
        frame_izquierdo = tk.Frame(frame_organizacion, bg="#2a2a2a")
        # sticky="nwes" para que se expanda en todas direcciones de la celda
        frame_izquierdo.grid(row=0, column=1, padx=15, pady=10, sticky="nwes") 
        # Aseguramos que los inputs se expandan
        for i in range(5): frame_izquierdo.grid_rowconfigure(i, weight=0)
        frame_izquierdo.grid_columnconfigure(0, weight=1)
        
        # Reemplazar pack por grid para mayor control y uso de sticky en los elementos internos si es necesario
        
        # Título izquierda
        tk.Label(frame_izquierdo, text="📊 PARÁMETROS SÍSMICOS", 
                  bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 13, "bold")).pack(pady=(0, 15), fill="x")
        
        # Magnitud Richter
        tk.Label(frame_izquierdo, text="📏 Magnitud Richter:", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_magnitud = tk.Entry(frame_izquierdo, **estilo_input)
        self.entry_magnitud.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_magnitud.insert(0, "5.0")
        
        # Ciclos/Repeticiones
        tk.Label(frame_izquierdo, text="⏱️ Ciclos (repeticiones):", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_repeticiones = tk.Entry(frame_izquierdo, **estilo_input)
        self.entry_repeticiones.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_repeticiones.insert(0, "10")
        
        # Separador visual
        tk.Frame(frame_izquierdo, bg="#ff6b35", height=2).pack(fill="x", padx=5, pady=15) # fill="x"
        
        # Amplitudes
        tk.Label(frame_izquierdo, text="📈 Amplitud Máxima:", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_amp_max = tk.Entry(frame_izquierdo, **estilo_input)
        self.entry_amp_max.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_amp_max.insert(0, self.configuracion["amplitud_maxima"])
        
        tk.Label(frame_izquierdo, text="📉 Amplitud Mínima:", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_amp_min = tk.Entry(frame_izquierdo, **estilo_input)
        self.entry_amp_min.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_amp_min.insert(0, self.configuracion["amplitud_minima"])
        
        # ============ COLUMNA DERECHA DE PARÁMETROS ============
        frame_derecho = tk.Frame(frame_organizacion, bg="#2a2a2a")
        # sticky="nwes" para que se expanda en todas direcciones de la celda
        frame_derecho.grid(row=0, column=2, padx=15, pady=10, sticky="nwes") 
        frame_derecho.grid_columnconfigure(0, weight=1)
        
        # Título derecha
        tk.Label(frame_derecho, text="⚡ VALORES DE MOVIMIENTO", 
                  bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 13, "bold")).pack(pady=(0, 15), fill="x")
        
        # Aceleración
        tk.Label(frame_derecho, text="🚀 Aceleración (mm/s²):", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_aceleracion = tk.Entry(frame_derecho, **estilo_input)
        self.entry_aceleracion.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_aceleracion.insert(0, self.configuracion["aceleracion"])
        
        # Velocidad
        tk.Label(frame_derecho, text="💨 Velocidad (mm/s):", 
                  bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=5)
        self.entry_velocidad = tk.Entry(frame_derecho, **estilo_input)
        self.entry_velocidad.pack(fill="x", padx=5, pady=(2, 15), ipady=6) # fill="x"
        self.entry_velocidad.insert(0, self.configuracion["velocidad"])
        
        
        # Botón Generar (centrado abajo) - Se reubica en la fila 1 (debajo de los parámetros)
        boton_generar = tk.Button(frame_organizacion, text="GENERAR G-CODE", 
                                       bg="#04f023", fg="black", 
                                       font=("Segoe UI", 12, "bold"), 
                                       relief="raised", bd=5, cursor="hand2",
                                       width=22, height=2, 
                                       activebackground="#f14e3f", activeforeground="white")
        # Se coloca en la fila 1, abarcando las dos columnas de parámetros (col 1 y 2)
        boton_generar.grid(row=1, column=1, columnspan=2, pady=(30, 10), sticky="s") # sticky="s"
        
        # Configurar función del botón con los parámetros actualizados
        def generar_con_parametros():
            # ... (Función se mantiene igual)
            aplicar_configuracion(self.entry_amp_max.get(), self.entry_amp_min.get(),self.entry_aceleracion.get(),self.entry_velocidad.get(), self.configuracion)
            ruta = filedialog.asksaveasfilename(
                defaultextension=".gcode",
                filetypes=[
                    ("Archivo G-CODE","*.gcode"),
                    ("Todos los archivos", "*.*")  
                ],
                title="Guardar GCODE"
            )
            
            if ruta:
                generar_gcode_sismico(
                    self.entry_magnitud.get(), 
                    self.entry_repeticiones.get(),                     
                    self.configuracion, 
                    ruta=ruta
                )
        
        boton_generar.config(command=generar_con_parametros)
        
        
    def crear_pestana_ejecucion(self):
        """Crea la pestaña de ejecución y control serial"""
        self.estilo_input_base = {
            'font': ("Consolas", 11), 
            'bg': "#1a1a1a", 
            'fg': "#ffffff", 
            'insertbackground': "#ff6b35", 
            'relief': "solid", 
            'bd': 2, 
            'width': 15
        }
        
        frame_pestana = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(frame_pestana, text="EJECUCIÓN")

        frame_contenido = tk.Frame(frame_pestana, bg="#1a1a1a", relief="solid", bd=3)
        # Importante: expand=True para que tome el espacio del notebook
        frame_contenido.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame_interno = tk.Frame(frame_contenido, bg="#2a2a2a", relief="ridge", bd=2)
        # Importante: expand=True para que tome el espacio del frame_contenido
        frame_interno.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Contenedor Superior (Conexión, Ejecución, Parámetros)
        frame_superior = tk.Frame(frame_interno, bg="#2a2a2a", relief="groove", bd=2)
        # Usamos pack(fill="x") para que se expanda horizontalmente, NO expand=True.
        frame_superior.pack(fill="x", pady=10, padx=40)
        
        # Configuración interna de frame_superior (Grid: 2x2)
        frame_superior.grid_columnconfigure(0, weight=1) # Columna izquierda (expandible)
        frame_superior.grid_columnconfigure(1, weight=1) # Columna derecha (expandible)
        frame_superior.grid_rowconfigure(0, weight=1)
        frame_superior.grid_rowconfigure(1, weight=1)
        
        #BOTONES IZQUIERDA (Conexión Serial)
        frame_controles_izq = tk.Frame(frame_superior, bg="#2a2a2a", padx=10, pady=5)
        # Usamos grid con sticky="nw" y padx/pady pequeños para que ocupe el espacio sin forzar expansión vertical
        frame_controles_izq.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        
        #TITULO IZQUIERDA
        tk.Label(frame_controles_izq, text="🔗 CONEXIÓN SERIAL", 
                 bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 12, "bold")).pack(pady=(0, 10), anchor="w")

        #CONTENEDOR PUERTO Y CONTROLES DE CONEXIÓN
        frame_puerto = tk.Frame(frame_controles_izq, bg="#2a2a2a")
        frame_puerto.pack(fill="x", pady=5)
        
        #ETIQUETA TITULO PUERTOS
        tk.Label(frame_puerto, text="Puerto:", bg="#2a2a2a", fg="white", font=("Segoe UI", 10)).pack(side="left")
        
        #LISTA COMBOX CON LOS PUERTOS DISPONIBLES
        self.puertos_disponibles = [port.device for port in list_ports.comports()]
        if not self.puertos_disponibles:
            self.puertos_disponibles = ["No hay puertos"]
            
        self.puerto_seleccionado_var = tk.StringVar(value=self.puertos_disponibles[0])
        
        self.combobox_puertos = ttk.Combobox(frame_puerto, textvariable=self.puerto_seleccionado_var, 
                                             values=self.puertos_disponibles, 
                                             state="readonly", width=15)
        self.combobox_puertos.pack(side="left", padx=5)
        
        #BOTON DE CONEXIÓN
        self.boton_conectar = ttk.Button(frame_puerto, text="Conectar", 
                                         command=lambda: serialCOM.conectar(self.puerto_seleccionado_var.get()), 
                                         style="Connect.TButton")
        self.boton_conectar.pack(side="left", padx=10)

        #BOTON DE RECARGAR PUERTOS
        self.boton_recargar_puertos = ttk.Button(frame_puerto, text="🔄 Recargar Puertos", 
                                                 command=self.recargar_puertos_com, 
                                                 style="Dark.TButton")
        self.boton_recargar_puertos.pack(side="left", padx=5)
        
        #BOTON DE DESCONECTAER
        self.boton_desconectar = ttk.Button(frame_puerto, text="🔌 Desconectar", command=serialCOM.desconectar
                                             , style="Red.TButton")
        self.boton_desconectar.pack(side="left", padx=10)
        
        
        
        
        #CONTROLES BOTONES DE EJECUCION
        frame_botones_ejecucion = tk.Frame(frame_superior, bg="#2a2a2a")
        # Grid en la segunda fila izquierda
        frame_botones_ejecucion.grid(row=1, column=0,padx=5, pady=5, sticky="nw")
        
        #TITULO BOTONES DE EJECUCION
        tk.Label(frame_botones_ejecucion, text="⚙️ EJECUCIÓN DE ARCHIVO", 
                 bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 12, "bold")).pack(pady=(15, 0), anchor="w")

        
        #ETIQUETA NOMBRE DE ARCHIVO CARGADO
        self.etiqueta_nombre_archivo = tk.Label(frame_botones_ejecucion, 
                                                 text="No se ha cargado un archivo",
                                                 bg="#2a2a2a",
                                                 fg="#575250", 
                                                 font=("Segoe UI", 10, "bold"))
        self.etiqueta_nombre_archivo.pack(pady=(0,10), anchor="w")
        
        #BOTONES DE EJECUCION
        ttk.Button(frame_botones_ejecucion, text="📂 CARGAR", 
                   command=lambda:self.cargar_archivo(),
                   style="Dark.TButton").pack(side="left", padx=5)
        
        ttk.Button(frame_botones_ejecucion, text="▶️ EJECUTAR", 
                   command=lambda: serialCOM.ejecutar_comando(self.ruta_archivo), 
                   style="Green.TButton").pack(side="left", padx=5)
        
        ttk.Button(frame_botones_ejecucion, text="⏸️ PAUSA", 
                   command=lambda: serialCOM.pausar_comando(), 
                   style="Yellow.TButton").pack(side="left", padx=5)
        
        ttk.Button(frame_botones_ejecucion, text="⏹️ STOP", 
                   command=lambda: serialCOM.detener_comando(), 
                   style="Red.TButton").pack(side="left", padx=5)
        
        ttk.Button(frame_botones_ejecucion, text="🔄 RESET", 
                   command=lambda: serialCOM.reset_comando(), 
                   style="Dark.TButton").pack(side="left", padx=5)
        
        
        
        
        #CONTENEDOR ESTADO
        frame_estado = tk.Frame(frame_superior, bg="#2a2a2a", padx=15, pady=10)
        # Grid en la primera fila derecha
        frame_estado.grid(row=0, column=1, padx=5, pady=5, sticky="ne")
        
        self.etiqueta_estado = tk.Label(frame_estado, text= "🔌 DESCONECTADO", bg="#2a2a2a", fg="#726c6c", font=("Rajdhani", 15, "bold"))
        self.etiqueta_estado.pack(side="left",pady=(0, 10))
        
        tk.Button(frame_estado, text="🔓", bg="#000000", fg="#dce926",command=serialCOM.desbloquear,
                  font=("Rajdhani", 20, "bold")).pack(side="right", padx=(20,5), pady=(0,10))
        
        
        #CONTENEDOR PARAMETROS DE MOVIMIENTO
        frame_movimiento_params = tk.Frame(frame_superior, bg="#2a2a2a", padx=15, pady=10)
        # Grid en la segunda fila derecha
        frame_movimiento_params.grid(row=1, column=1, padx=5, pady=5, sticky="nwes")
        frame_movimiento_params.grid_columnconfigure(0, weight=1)
        frame_movimiento_params.grid_columnconfigure(1, weight=1)
        
        #TITULO PARAMETROS DE MOVIMIENTO
        tk.Label(frame_movimiento_params, text="📈 VALORES DE MOVIMIENTO GRBL", 
                 bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 12, "bold")).grid(
                         row=0, column=0, columnspan=2, pady=(0, 10), sticky="n")

        #INPUT VELOCIDAD
        frame_vel = tk.Frame(frame_movimiento_params, bg="#2a2a2a")
        frame_vel.grid(row=1, column=0, padx=5, sticky="ew")
        tk.Label(frame_vel, text="💨 Velocidad (F):", 
                 bg="#2a2a2a", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Entry(frame_vel, textvariable=self.velocidad_ejecucion_var, 
                 **self.estilo_input_base).pack(fill="x", pady=(2, 5), ipady=5) # fill="x"

        frame_mov = tk.Frame(frame_movimiento_params, bg="#2a2a2a")
        frame_mov.grid(row=1, column=1, padx=5, sticky="ew")
        tk.Label(frame_mov, text="⚡️ Movimiento (mm):", 
                 bg="#2a2a2a", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Entry(frame_mov, textvariable=self.movimiento_ejecucion_var, 
                 **self.estilo_input_base).pack(fill="x", pady=(2, 5), ipady=5) # fill="x"
        
        # 2. Contenedor Movimiento Manual
        frame_movimiento_manual = tk.Frame(frame_interno, bg="#2a2a2a", bd=2, relief="groove", padx=15, pady=10)
        # Usamos pack(fill="x") para que se expanda horizontalmente, NO expand=True.
        frame_movimiento_manual.pack(fill="x", padx=20, pady=15)
        
        tk.Label(frame_movimiento_manual, text="🛠️ MOVIMIENTO MANUAL (Eje X)", 
                 bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 12, "bold")).pack(pady=(0, 10))

        frame_botones_x = tk.Frame(frame_movimiento_manual, bg="#2a2a2a")
        frame_botones_x.pack(pady=10)
        
        ttk.Button(frame_botones_x, text="◀️ X-", 
                   command=lambda: serialCOM.mover_eje_x(
                       str(-int(self.movimiento_ejecucion_var.get())),
                       self.velocidad_ejecucion_var.get()), 
                   style="Directional.TButton", width=12).pack(side="left", padx=15)
        
        ttk.Button(frame_botones_x, text="🏠 HOME", 
                   command=lambda:serialCOM.home_comando(), 
                   style="Home.TButton", width=12).pack(side="left", padx=15)
        
        ttk.Button(frame_botones_x, text="X+ ▶️", 
                   command=lambda: serialCOM.mover_eje_x(
                       self.movimiento_ejecucion_var.get(),
                       self.velocidad_ejecucion_var.get()), 
                   style="Directional.TButton", width=12).pack(side="left", padx=15)

        # 3. Consola
        tk.Label(frame_interno, text="💻 CONSOLA", 
                 bg="#2a2a2a", fg="#ff6b35", font=("Rajdhani", 14, "bold")).pack(pady=(20, 5))
        
        self.consola = scrolledtext.ScrolledText(frame_interno, wrap=tk.WORD, 
                                                 bg="#0a0a0a", fg="#1fff17", 
                                                 font=("Consolas", 10), 
                                                 relief="sunken", bd=3, padx=5, pady=5, height=15) 
        self.consola.insert(tk.END, "Consola lista. Seleccione puerto COM y presione Conectar.\n")
        # Importante: fill="both" y expand=True para que tome el espacio restante
        self.consola.pack(fill="both", expand=True, padx=20, pady=0) 

        sys.stdout = ConsoleRedirector(self.consola)
        sys.stderr = ConsoleRedirector(self.consola)
        
        # 4. Input manual de comandos
        frame_input_manual = tk.Frame(frame_interno, bg="#2a2a2a")
        # Usamos pack(fill="x") para que se expanda horizontalmente, NO expand=True.
        frame_input_manual.pack(fill="x", padx=20, pady=(5, 10)) 
        
        self.comando_manual_var = tk.StringVar()
        self.input_comando = tk.Entry(frame_input_manual, textvariable=self.comando_manual_var, 
                 **self.estilo_input_base,)
        self.input_comando.bind("<Return>", lambda event: enviar_y_guardar())
        # Importante: fill="x" y expand=True para que ocupe todo el espacio a la izquierda
        self.input_comando.pack(side="left",pady= (5,10), fill="x", expand=True)
        
        
        def enviar_y_guardar():
            comando = self.comando_manual_var.get()
            if comando.lower() == "clear":
                self.limpiar_consola()
            resultado = serialCOM.enviar_comando_manual(comando)
            self.ultimo_resultado_manual = resultado
            
        # El botón solo usa pack(side="left")
        ttk.Button(frame_input_manual, text="Enviar", 
                   command=enviar_y_guardar, 
                   style="Send.TButton").pack(side="left", padx=(5, 0))

        # Estilos de botones (se mantienen al final)
        style = ttk.Style()
        
        style.configure("Dark.TButton", background="#444444", foreground="white", relief="raised")
        style.map("Dark.TButton", background=[('active', '#666666')])
        
        style.configure("Green.TButton", background="#1fff17", foreground="black", relief="raised")
        style.map("Green.TButton", background=[('active', '#00cc00')])
        
        style.configure("Yellow.TButton", background="#ffcc00", foreground="black", relief="raised")
        style.map("Yellow.TButton", background=[('active', '#e6b800')])
        
        style.configure("Red.TButton", background="#f14e3f", foreground="white", relief="raised")
        style.map("Red.TButton", background=[('active', '#cc0000')])
        
        style.configure("Directional.TButton", background="#007bff", foreground="white", 
                        font=("Segoe UI", 12, "bold"), padding=10)
        style.map("Directional.TButton", background=[('active', '#0056b3')])
        
        style.configure("Home.TButton", background="#343a40", foreground="white", 
                        font=("Segoe UI", 12, "bold"), padding=10)
        style.map("Home.TButton", background=[('active', '#495057')])

        style.configure("Connect.TButton", background="#007bff", foreground="white", 
                        font=("Segoe UI", 10, "bold"), padding=5)
        style.map("Connect.TButton", background=[('active', '#0056b3')])
        
        style.configure("Send.TButton", background="#1fff17", foreground="black", 
                        font=("Segoe UI", 10, "bold"), padding=5)
        style.map("Send.TButton", background=[('active', '#00cc00')])

        self.iniciar_actualizacion_estado()

    # ... (El resto de las funciones de la clase Ventana se mantienen igual)
    def logo(self, ruta_imagen):
        """Carga el icono de la ventana"""
        if os.path.exists(ruta_imagen):
            try:
                imagen = PhotoImage(file=ruta_imagen)
                self.root.iconphoto(False, imagen)
            except Exception as e:
                print(f"Advertencia: No se pudo cargar el ícono. Error: {e}")
        else:
            print(f"Advertencia: El archivo de ícono '{ruta_imagen}' no existe.")
            
    def cargar_archivo(self):
        """Abre un diálogo para seleccionar un archivo G-Code"""
        self.ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar Archivo G-Code para Ejecutar",
            initialdir=os.getcwd(), 
            filetypes=(
                ("Archivos G-Code", "*.gcode"),
                ("Archivos de Texto", "*.txt"),
                ("Todos los archivos", "*.*")
            )
        )
        if self.ruta_archivo:
            nombre_archivo = os.path.basename(self.ruta_archivo)
            self.etiqueta_nombre_archivo.config(
                text=nombre_archivo,
                fg="#ff6b35"
            )
    
    def recargar_puertos_com(self):
        """Recarga la lista de puertos COM disponibles"""
        nuevos_puertos = [port.device for port in list_ports.comports()]
        if not nuevos_puertos:
            nuevos_puertos = ["No hay puertos"]
        self.combobox_puertos['values'] = nuevos_puertos
        self.puerto_seleccionado_var.set(nuevos_puertos[0])
    
    def limpiar_consola(self):
        """Limpia el contenido de la consola"""
        self.consola.configure(state="normal")
        self.consola.delete("1.0", tk.END)
        self.consola.configure(state="disabled")

    def actualizar_estado(self):
        
        
        # Obtener el valor numérico del estado actual
        estadoNum = serialCOM.retornar_estado() 
        
        # Inicialización de variables para el mapeo
        estado = ""
        color = ""
        
        # Mapeo de estados del Enum
        if estadoNum == 0:
            estado = "🟢 REPOSO"         
            color = "#1fff17"         
        elif estadoNum == 1:
            estado = "⏸️ PAUSA"       
            color = "#fbff17"         
        elif estadoNum == 2:
            estado = "🚨 ALARMA"         
            color = "#ff1717"       
        elif estadoNum == 3:
            estado = "🛑 DETENIDO"       
            color = "#ff1717"           
        elif estadoNum == 4:
            estado = "🔨 EJECUCIÓN"     
            color = "#1755ff"           
        elif estadoNum == 5:
            estado = "🔌 DESCONECTADO" 
            color = "#726c6c"         
        else:
            estado = "❓ DESCONOCIDO" 
            color = "#ffa500"           
            
        # Actualiza la etiqueta de estado
        if hasattr(self, "etiqueta_estado") and isinstance(self.etiqueta_estado, tk.Label):
            self.etiqueta_estado.config(text=estado, fg=color)
        
        # Llama de nuevo
        self.root.after(1000, self.actualizar_estado)
        
    def iniciar_actualizacion_estado(self):
        """Inicia la actualización periódica del estado."""
        self.actualizar_estado()
    def ejecutar(self):
        """Inicia el loop principal de la aplicación"""
        self.root.mainloop()