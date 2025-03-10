import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

# Este código define un widget (Generalimport) que se integrará en el frame llamado parent_frame.
# DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

class Generalimport(ttk.Frame):
    """
    Widget para exportar la estructura de directorios, diseñado para integrarse en parent_frame.
    """
    def __init__(self, parent):
        super().__init__(parent) # Inicializa ttk.Frame con el parent_frame proporcionado.
        self.parent_frame = parent # Guarda una referencia al parent_frame.
        self._build_interface() # Llama al método para construir la interfaz gráfica.
        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

    def _build_interface(self):
        # Métodos internos con guión bajo "_" como convención para indicar que son para uso interno de la clase.
        self.label_instrucciones = ttk.Label(self, text="Selecciona una carpeta para exportar su estructura:", font=("Helvetica", 12))
        self.label_instrucciones.pack(pady=10) # Se empaqueta en 'self', que es el frame Generalimport, integrado en parent_frame.
        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

        self.boton_seleccionar_carpeta = ttk.Button(self, text="Seleccionar Carpeta y Exportar", command=self._exportar_estructura_directorios)
        self.boton_seleccionar_carpeta.pack(pady=10) # Se empaqueta en 'self', integrado en parent_frame.
        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

        self.mensaje_label = ttk.Label(self, text="", wraplength=300) # Para mensajes al usuario.
        self.mensaje_label.pack(pady=10) # Se empaqueta en 'self', integrado en parent_frame.
        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

    def _exportar_estructura_directorios(self):
        # Función interna para exportar la estructura de directorios.
        # Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.
        carpeta_seleccionada = filedialog.askdirectory(parent=self.parent_frame, title="Seleccionar carpeta") # Usa self.parent_frame como parent para el diálogo.
        if carpeta_seleccionada:
            ruta_archivo_salida = os.path.join(carpeta_seleccionada, "estructura_directorios.txt")
            try:
                with open(ruta_archivo_salida, "w", encoding="utf-8") as archivo_salida:
                    for ruta_directorio, directorios, archivos in os.walk(carpeta_seleccionada):
                        nivel = ruta_directorio.replace(carpeta_seleccionada, '').count(os.sep)
                        indentacion = ' ' * 4 * nivel
                        archivo_salida.write('{}- {}\n'.format(indentacion, os.path.basename(ruta_directorio)))
                        subindentacion = ' ' * 4 * (nivel + 1)
                        for archivo in archivos:
                            archivo_salida.write('{}-- {}\n'.format(subindentacion, archivo))
                self.mensaje_label.config(text=f"Estructura exportada a:\n{ruta_archivo_salida}") # Mensaje de éxito en la GUI embebida.
            except Exception as e:
                self.mensaje_label.config(text=f"Error al exportar: {e}") # Mensaje de error en la GUI embebida.
        else:
            self.mensaje_label.config(text="No se seleccionó ninguna carpeta.") # Mensaje si no se selecciona carpeta.

# Para usar este código en el programa principal, instancia Generalimport pasando parent_frame como argumento.
# Ejemplo de uso DENTRO del programa principal (donde parent_frame ya está definido):
#
# interfaz_exportar = Generalimport(parent_frame)
# interfaz_exportar.pack(expand=True, fill='both') # Empaquetar la interfaz dentro de parent_frame para que se visualice.
#
# Recuerda: DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame. DEBE GENERAR UNA INTERFAZ GRÁFICA INTEGRADA EN parent_frame.