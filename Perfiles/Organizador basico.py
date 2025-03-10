import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import shutil

# Este código se integrará en el frame llamado parent_frame (la variable parent_frame ya está definida en el namespace local).
# DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

class Generalimport(ttk.Frame): # Crear una clase llamada Generalimport que hereda de ttk.Frame
    """
    Widget general que se integrará en el programa principal.
    """
    def __init__(self, parent): # Recibe parent_frame como argumento, renombrado a parent
        super().__init__(parent) # Inicializa ttk.Frame con parent
        # self.parent_frame = parent # Guarda la referencia a parent, no estrictamente necesario aquí
        self.incluir_subcarpetas_var = tk.BooleanVar() # Variable para el Checkbutton de subcarpetas
        self._build_interface() # Llama a la función para construir la interfaz

    def _build_interface(self):
        # --- Interfaz gráfica INTEGRADA EN parent_frame ---
        # DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.
        # Usa 'self' como parent para todos los widgets, ya que 'self' es el Frame que se integrará en parent_frame.

        instrucciones_label = ttk.Label(self, text="Selecciona la carpeta a organizar:", font=("Helvetica", 12)) # 'self' como parent
        instrucciones_label.pack(pady=10)

        frame_seleccion_carpeta = ttk.Frame(self) # 'self' como parent
        frame_seleccion_carpeta.pack(pady=5, fill=tk.X, padx=20)

        self.carpeta_entry = ttk.Entry(frame_seleccion_carpeta) # 'self' como parent
        self.carpeta_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        seleccionar_button = ttk.Button(frame_seleccion_carpeta, text="Seleccionar Carpeta", command=self.seleccionar_carpeta) # 'self' como parent y self.seleccionar_carpeta
        seleccionar_button.pack(side=tk.RIGHT, padx=5)

        # Checkbutton para incluir subcarpetas
        incluir_subcarpetas_check = ttk.Checkbutton(self, text="Incluir Subcarpetas", variable=self.incluir_subcarpetas_var) # 'self' como parent y self.incluir_subcarpetas_var
        incluir_subcarpetas_check.pack(pady=5)

        organizar_button = ttk.Button(self, text="Organizar Archivos", command=self.organizar_archivos) # 'self' como parent y self.organizar_archivos
        organizar_button.pack(pady=20)

        estado_label = ttk.Label(self, text="Estado:", font=("Helvetica", 10)) # 'self' como parent
        estado_label.pack(pady=5)

        self.estado_text = tk.Text(self, height=5, state=tk.DISABLED) # 'self' como parent
        self.estado_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar_estado = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.estado_text.yview) # 'self' como parent y self.estado_text
        self.estado_text.config(yscrollcommand=scrollbar_estado.set)
        scrollbar_estado.pack(side=tk.RIGHT, fill=tk.Y)

        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.
        # No se abren ventanas nuevas, todo se integra en 'parent_frame'.

    def seleccionar_carpeta(self):
        # Abre el diálogo para seleccionar una carpeta y actualiza el campo de texto.
        carpeta_seleccionada = filedialog.askdirectory()
        if carpeta_seleccionada:
            self.carpeta_entry.delete(0, tk.END)
            self.carpeta_entry.insert(0, carpeta_seleccionada)

    def organizar_archivos(self):
        # Organiza los archivos de la carpeta especificada, incluyendo o no subcarpetas según la opción.
        carpeta_origen = self.carpeta_entry.get()
        incluir_subcarpetas = self.incluir_subcarpetas_var.get() # Obtiene el valor del Checkbutton

        if not carpeta_origen:
            self.mostrar_mensaje("Por favor, selecciona una carpeta.")
            return

        self.mostrar_mensaje("Organizando archivos...")

        tipos_archivos = {
            "Imagenes": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            "Videos": ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'],
            "Audio": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'], # Añadido .opus
            "Documentos": ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.rtf', '.odt', '.ods', '.odp'],
            "Codigos": ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.sh', '.bat'],
            "Comprimidos": ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            "Ejecutables": ['.exe', '.dmg', '.apk'],
            "Otros": [] # Para otros tipos de archivos
        }

        carpetas_creadas = set() # Para rastrear las carpetas de destino creadas
        nombres_carpetas_tipo = set(tipos_archivos.keys()) # Nombres de carpetas de tipo

        if not incluir_subcarpetas:
            carpeta_carpetas = os.path.join(carpeta_origen, "Carpetas") # Carpeta para mover subcarpetas si no se incluyen
            if not os.path.exists(carpeta_carpetas):
                os.makedirs(carpeta_carpetas)
            carpetas_creadas.add(carpeta_carpetas) # Añadir a carpetas creadas

        archivos_organizados = 0
        carpetas_organizadas = 0 # Contador para carpetas movidas
        archivos_no_organizados = 0

        if incluir_subcarpetas:
            # Recorrer la carpeta y subcarpetas
            for ruta_actual, subcarpetas, archivos in os.walk(carpeta_origen):
                for filename in archivos:
                    filepath = os.path.join(ruta_actual, filename)
                    nombre, extension = os.path.splitext(filename)
                    organizado = False
                    for nombre_carpeta, extensiones in tipos_archivos.items():
                        if extension.lower() in extensiones:
                            ruta_carpeta_destino = os.path.join(carpeta_origen, nombre_carpeta)
                            if ruta_carpeta_destino not in carpetas_creadas: # Crear carpeta destino si no existe
                                if not os.path.exists(ruta_carpeta_destino):
                                    os.makedirs(ruta_carpeta_destino)
                                    carpetas_creadas.add(ruta_carpeta_destino)
                            shutil.move(filepath, os.path.join(ruta_carpeta_destino, filename))
                            archivos_organizados += 1
                            organizado = True
                            break
                    if not organizado: # Si no se categorizó en los tipos anteriores, va a 'Otros'
                        ruta_carpeta_destino = os.path.join(carpeta_origen, "Otros")
                        if ruta_carpeta_destino not in carpetas_creadas: # Crear carpeta destino si no existe
                            if not os.path.exists(ruta_carpeta_destino):
                                os.makedirs(ruta_carpeta_destino)
                                carpetas_creadas.add(ruta_carpeta_destino)
                        shutil.move(filepath, os.path.join(ruta_carpeta_destino, filename))
                        archivos_no_organizados += 1 # En este caso, 'Otros' también cuenta como organizado dentro de su categoría.
        else:
            # Solo la carpeta principal, y mover subcarpetas a "Carpetas"
            for item_name in os.listdir(carpeta_origen):
                item_path = os.path.join(carpeta_origen, item_name)
                if os.path.isfile(item_path):
                    filename = item_name
                    filepath = item_path
                    nombre, extension = os.path.splitext(filename)
                    organizado = False
                    for nombre_carpeta, extensiones in tipos_archivos.items():
                        if extension.lower() in extensiones:
                            ruta_carpeta_destino = os.path.join(carpeta_origen, nombre_carpeta)
                            if ruta_carpeta_destino not in carpetas_creadas: # Crear carpeta destino si no existe
                                if not os.path.exists(ruta_carpeta_destino):
                                    os.makedirs(ruta_carpeta_destino)
                                    carpetas_creadas.add(ruta_carpeta_destino)
                            shutil.move(filepath, os.path.join(ruta_carpeta_destino, filename))
                            archivos_organizados += 1
                            organizado = True
                            break
                    if not organizado: # Si no se categorizó en los tipos anteriores, va a 'Otros'
                        ruta_carpeta_destino = os.path.join(carpeta_origen, "Otros")
                        if ruta_carpeta_destino not in carpetas_creadas: # Crear carpeta destino si no existe
                            if not os.path.exists(ruta_carpeta_destino):
                                os.makedirs(ruta_carpeta_destino)
                                carpetas_creadas.add(ruta_carpeta_destino)
                        shutil.move(filepath, os.path.join(ruta_carpeta_destino, filename))
                        archivos_no_organizados += 1 # En este caso, 'Otros' también cuenta como organizado dentro de su categoría.
                elif os.path.isdir(item_path): # Si es una carpeta, mover a "Carpetas"
                    if item_name != "Carpetas" and item_name not in nombres_carpetas_tipo: # Evitar mover la carpeta "Carpetas" dentro de sí misma y carpetas de tipo
                        carpeta_carpetas = os.path.join(carpeta_origen, "Carpetas")
                        shutil.move(item_path, os.path.join(carpeta_carpetas, item_name))
                        carpetas_organizadas += 1

        mensaje = f"Organización completada.\nArchivos organizados: {archivos_organizados}\nCarpetas movidas a 'Carpetas': {carpetas_organizadas}\nArchivos en 'Otros': {archivos_no_organizados}" if not incluir_subcarpetas else f"Organización completada (subcarpetas incluidas).\nArchivos organizados: {archivos_organizados}\nArchivos en 'Otros': {archivos_no_organizados}"
        self.mostrar_mensaje(mensaje)

    def mostrar_mensaje(self, texto):
        # Muestra mensajes en el campo de texto de estado.
        self.estado_text.config(state=tk.NORMAL) # Habilita la edición del widget de texto
        self.estado_text.delete(1.0, tk.END) # Borra el texto anterior
        self.estado_text.insert(tk.END, texto) # Inserta el nuevo texto
        self.estado_text.config(state=tk.DISABLED) # Deshabilita la edición para que sea de solo lectura

# --- FIN DEL CÓDIGO PARA INTEGRAR EN parent_frame ---
# RECUERDA: ESTE CÓDIGO DEBE INTEGRARSE EN parent_frame. NO ABRIRÁ VENTANAS NUEVAS.
# DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.