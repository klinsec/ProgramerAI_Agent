import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import whisper
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np

class Generalimport(tk.Frame):
    """
    Widget general que se integrará en el programa principal.
    Interfaz gráfica para grabar audio, detener grabación, transcribir y cargar audio.
    INTEGRADA EN parent_frame.
    INTEGRADA EN parent_frame.
    INTEGRADA EN parent_frame.
    """
    def __init__(self, parent):
        super().__init__(parent, bg="#e6f2ff") # Inicializa tk.Frame, usando parent para integrarse y establece el color de fondo
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.
        self.parent = parent # Guarda la referencia al parent_frame
        self.recording_active = False
        self.audio_data = []
        self.stream = None
        self.filename = "output.wav"
        self.fs = 44100
        self.channels = 1
        self.model = whisper.load_model("small") # Carga el modelo whisper al inicio
        self._set_styles() # Aplica estilos
        self._build_interface() # Llama a la función para construir la interfaz
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

    def _set_styles(self):
        """Establece los estilos para los widgets."""
        style = ttk.Style(self)
        style.theme_use("clam") # Usa el tema 'clam'
        style.configure("TFrame", background="#e6f2ff") # Color de fondo para TFrame
        style.configure("TLabel", font=("Helvetica", 16), background="#e6f2ff") # Estilo para TLabel
        style.configure("TButton", font=("Helvetica", 11, "bold")) # Estilo para TButton


    def _build_interface(self):
        """Construye la interfaz gráfica dentro de parent_frame.
        INTERFAZ GRÁFICA INTEGRADA EN parent_frame.
        """

        # Frame para organizar los botones en horizontal
        botones_frame = ttk.Frame(self) # Usa self como parent, integrándose en Generalimport
        botones_frame.pack(pady=10)

        self.record_button = ttk.Button(botones_frame, text="Grabar Voz", command=self.grabar_audio_inicio)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(botones_frame, text="Detener Grabación", command=self.detener_grabacion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.load_audio_button = ttk.Button(botones_frame, text="Cargar Audio", command=self.cargar_audio) # Nuevo botón
        self.load_audio_button.pack(side=tk.LEFT, padx=5)

        self.texto_transcripcion = tk.Text(self, height=10, state=tk.DISABLED) # self como parent
        self.texto_transcripcion.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        scrollbar_texto = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.texto_transcripcion.yview) # self como parent
        self.texto_transcripcion.config(yscrollcommand=scrollbar_texto.set)
        scrollbar_texto.pack(side=tk.RIGHT, fill=tk.Y)
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

    def transcribe_audio(self, audio_path):
        """Transcribe el audio y muestra el texto, gestionando botones."""
        self.texto_transcripcion.config(state=tk.NORMAL)
        self.texto_transcripcion.delete("1.0", tk.END)
        self.texto_transcripcion.insert(tk.END, "Transcribiendo...\n")
        self.texto_transcripcion.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED) # Deshabilitar grabar durante transcripción
        self.stop_button.config(state=tk.DISABLED)  # Deshabilitar detener durante transcripción
        self.load_audio_button.config(state=tk.DISABLED) # Deshabilitar cargar audio durante transcripción

        try:
            result = self.model.transcribe(audio_path)
            transcribed_text = result["text"]
            self.texto_transcripcion.config(state=tk.NORMAL)
            self.texto_transcripcion.delete("1.0", tk.END)
            self.texto_transcripcion.insert(tk.END, transcribed_text)
            self.texto_transcripcion.config(state=tk.DISABLED)
        except Exception as e:
            self.texto_transcripcion.config(state=tk.NORMAL)
            self.texto_transcripcion.delete("1.0", tk.END)
            self.texto_transcripcion.insert(tk.END, f"Error en la transcripción: {e}")
            self.texto_transcripcion.config(state=tk.DISABLED)
        finally:
            self.record_button.config(state=tk.NORMAL) # Re-habilitar grabar tras transcripción (o error)
            self.stop_button.config(state=tk.DISABLED)  # Deshabilitar detener tras transcripción (o error)
            self.load_audio_button.config(state=tk.NORMAL) # Re-habilitar cargar audio tras transcripción (o error)
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.


    def grabar_callback(self, indata, frames, time, status):
        """Callback function para grabación continua."""
        if self.recording_active:
            self.audio_data.append(indata.copy())

    def grabar_audio_inicio(self):
        """Inicia la grabación continua de audio."""
        if not self.recording_active:
            self.texto_transcripcion.config(state=tk.NORMAL)
            self.texto_transcripcion.delete("1.0", tk.END)
            self.texto_transcripcion.insert(tk.END, "Grabando...\n")
            self.texto_transcripcion.config(state=tk.DISABLED)
            self.record_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.load_audio_button.config(state=tk.DISABLED) # Deshabilitar cargar audio mientras graba
            self.recording_active = True
            self.audio_data = [] # Limpiar datos de grabaciones anteriores
            try:
                self.stream = sd.InputStream(callback=self.grabar_callback, samplerate=self.fs, channels=self.channels)
                self.stream.start()
            except Exception as e:
                self.texto_transcripcion.config(state=tk.NORMAL)
                self.texto_transcripcion.delete("1.0", tk.END)
                self.texto_transcripcion.insert(tk.END, f"Error al iniciar grabación: {e}")
                self.texto_transcripcion.config(state=tk.DISABLED)
                self.record_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.load_audio_button.config(state=tk.NORMAL) # Re-habilitar cargar audio en caso de error
                self.recording_active = False
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.


    def detener_grabacion(self):
        """Detiene la grabación, guarda el audio y transcribe."""
        if self.recording_active:
            self.texto_transcripcion.config(state=tk.NORMAL)
            self.texto_transcripcion.delete("1.0", tk.END)
            self.texto_transcripcion.insert(tk.END, "Grabación finalizada. Transcribiendo...\n")
            self.texto_transcripcion.config(state=tk.DISABLED)
            self.record_button.config(state=tk.DISABLED) # Deshabilitar grabar durante transcripción
            self.stop_button.config(state=tk.DISABLED) # Deshabilitar detener durante transcripción
            self.load_audio_button.config(state=tk.DISABLED) # Deshabilitar cargar audio durante transcripción
            self.recording_active = False
            try:
                self.stream.stop()
                self.stream.close()
                if self.audio_data:
                    recorded_audio = np.concatenate(self.audio_data, axis=0)
                    sf.write(self.filename, recorded_audio, self.fs)
                    threading.Thread(target=self.transcribe_audio, args=(self.filename,)).start() # Pasa self.filename y self para acceder a métodos y atributos
                else:
                    self.texto_transcripcion.config(state=tk.NORMAL)
                    self.texto_transcripcion.delete("1.0", tk.END)
                    self.texto_transcripcion.insert(tk.END, "No se grabó audio.")
                    self.texto_transcripcion.config(state=tk.DISABLED)
                    self.record_button.config(state=tk.NORMAL) # Re-habilitar grabar
                    self.stop_button.config(state=tk.DISABLED)  # Deshabilitar detener
                    self.load_audio_button.config(state=tk.NORMAL) # Re-habilitar cargar audio

            except Exception as e:
                self.texto_transcripcion.config(state=tk.NORMAL)
                self.texto_transcripcion.delete("1.0", tk.END)
                self.texto_transcripcion.insert(tk.END, f"Error al detener grabación: {e}")
                self.texto_transcripcion.config(state=tk.DISABLED)
                self.record_button.config(state=tk.NORMAL) # Re-habilitar grabar en caso de error
                self.stop_button.config(state=tk.DISABLED) # Deshabilitar detener en caso de error
                self.load_audio_button.config(state=tk.NORMAL) # Re-habilitar cargar audio en caso de error
                self.recording_active = False
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.

    def cargar_audio(self):
        """Abre un diálogo para cargar un archivo de audio y transcribirlo."""
        file_path = filedialog.askopenfilename(
            defaultextension=".wav",
            filetypes=[("Archivos de audio", "*.wav;*.mp3;*.flac;*.ogg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.texto_transcripcion.config(state=tk.NORMAL)
            self.texto_transcripcion.delete("1.0", tk.END)
            self.texto_transcripcion.insert(tk.END, f"Cargando audio desde: {file_path}\n")
            self.texto_transcripcion.config(state=tk.DISABLED)
            self.record_button.config(state=tk.DISABLED) # Deshabilitar grabar durante carga y transcripción
            self.stop_button.config(state=tk.DISABLED) # Deshabilitar detener durante carga y transcripción
            self.load_audio_button.config(state=tk.DISABLED) # Deshabilitar cargar audio durante carga y transcripción
            threading.Thread(target=self.transcribe_audio, args=(file_path,)).start() # Transcribe el audio cargado
        # INTERFAZ GRÁFICA INTEGRADA EN parent_frame.


# Para probar la interfaz gráfica como un programa independiente:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Interfaz de Transcripción de Audio")
    parent_frame = ttk.Frame(root) # Crea un frame para contener Generalimport
    parent_frame.pack(padx=10, pady=10, fill="both", expand=True)
    app = Generalimport(parent_frame) # Pasa parent_frame como 'parent'
    app.pack(fill=tk.BOTH, expand=True) # Empaquetar Generalimport dentro de parent_frame
    root.mainloop()