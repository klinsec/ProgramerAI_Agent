import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import subprocess
import configparser
import google.generativeai as genai
import sys  # Para usar sys.executable en la instalación

# Intentamos cargar PIL para la imagen de fondo (opcional)
try:
    from PIL import Image, ImageTk
    from PIL.Image import Resampling
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# --------------------- FUNCIONES AUXILIARES PARA IMPORTACIONES ---------------------
def extract_imports(code_text):
    """
    Extrae los nombres de módulos importados a partir del código fuente.
    Busca líneas que comiencen con "import" o "from" y extrae el primer identificador.
    """
    pattern = r'^\s*(?:import|from)\s+([\w\.]+)'
    matches = re.findall(pattern, code_text, flags=re.MULTILINE)
    modules = set()
    for m in matches:
        # Solo tomamos el primer nivel, en caso de importaciones con puntos.
        top_module = m.split('.')[0]
        modules.add(top_module)
    return list(modules)

# --------------------- FUNCIONES DE CARGA DE ARCHIVOS ---------------------
def load_api_key(file_path="GoogleAPI.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo API Key: {e}")
        exit(1)

def load_custom_prompt(file_path="prompt_gemini.txt"):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Extrae de este texto el tema y los subtemas (separados por comas) de forma resumida.\n")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo prompt: {e}")
        exit(1)

def load_guion_prompt(file_path="prompt_gemini_guion.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo prompt guion: {e}")
        exit(1)

def load_exper_prompt(file_path="prompt_gemini_exper.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo prompt experimental: {e}")
        exit(1)

def load_install_prompt(file_path="prompt_gemini_instalaciones.txt"):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
"""Genera una serie de comandos CMD para instalar únicamente las dependencias necesarias para que el siguiente programa funcione.
El código utiliza las siguientes dependencias: google-generativeai, ttkthemes y Pillow.
No incluyas comandos para paquetes que no se usen.
El formato de salida debe ser un archivo .bat ejecutable, con cada comando en una línea, por ejemplo:

@echo off
echo Creando entorno virtual...
python -m venv venv
call venv\\Scripts\\activate
echo Instalando dependencias...
pip install google-generativeai ttkthemes Pillow
echo Instalación completada.
""")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo prompt de instalaciones: {e}")
        exit(1)

# --------------------- CONFIGURACIÓN DE LA API Y PROMPTS ---------------------
API_KEY = load_api_key()
genai.configure(api_key=API_KEY)
custom_prompt = load_custom_prompt()
guion_prompt = load_guion_prompt()
exper_prompt = load_exper_prompt()
install_prompt = load_install_prompt()

# Carpeta raíz para perfiles (pestaña Experimental)
DEFAULT_ROOT_EXPER = r".\Perfiles"
if not os.path.exists(DEFAULT_ROOT_EXPER):
    os.makedirs(DEFAULT_ROOT_EXPER)

# Carpeta temporal para almacenar conversación experimental
TEMP_FOLDER = "Temp"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
TEMP_CONVERSATION_FILE = os.path.join(TEMP_FOLDER, "exper_conversation.txt")

# --------------------- FUNCIÓN AUXILIAR PARA LIMPIAR BLOQUES DE CÓDIGO ---------------------
def clean_code_block(text):
    """Elimina delimitadores de bloques de código y líneas innecesarias."""
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    filtered_lines = [line for line in text.splitlines() if not (line.strip().startswith("User:") or line.strip().startswith("Generated Code:"))]
    return "\n".join(filtered_lines).strip()

# --------------------- INTERFAZ CON TTKTHEMES ---------------------
try:
    from ttkthemes import ThemedTk
    BaseTk = ThemedTk
except ImportError:
    BaseTk = tk.Tk

# --------------------- PROGRAMA PRINCIPAL ---------------------
class App(BaseTk):
    def __init__(self):
        try:
            super().__init__(theme="arc")
        except TypeError:
            super().__init__()
        self.bg_color = "#e6f2ff"  # Color base para mezclar con el fondo
        self.configure(bg=self.bg_color)
        self.title("ProgramerAI Agent")
        self.geometry("950x750")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.set_styles()
        self.bg_image = None
        self.bg_label = None
        self.load_background("background.png")

        # Variables para la pestaña Experimental y perfiles
        self.root_folder_exper = DEFAULT_ROOT_EXPER
        self.latest_experimental_code = ""
        self.profile_tabs = {}     # perfil -> pestaña
        self.profile_vars = {}     # perfil -> tk.BooleanVar
        self.profile_embeds = {}   # perfil -> frame para la interfaz
        self.current_profile_name = ""

        # Cargar configuración y gestor de perfiles
        self.load_configuration()
        self.create_profile_manager()

        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Pestaña Experimental
        self.tab_experimental = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_experimental, text="Experimental")
        self.build_experimental_tab(self.tab_experimental)
        self.refresh_profile_manager()
        self.update_profile_tabs()

        self.lift()
        if self.bg_label:
            self.bg_label.lower()

    def load_background(self, img_path):
        if PIL_AVAILABLE and os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGBA")
                w, h = self.winfo_width(), self.winfo_height()
                if w < 10: w = 950
                if h < 10: h = 750
                img = img.resize((w, h), Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                self.bg_label = tk.Label(self, image=self.bg_image)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error cargando imagen de fondo: {e}")

    def set_styles(self):
        self.transparent_bg = "#ddeeff"   # Fondo claro para simular transparencia
        self.accent_bg = "#aaddff"         # Color de acento para botones y pestañas
        self.selected_bg = "#77ccff"       # Fondo para pestañas seleccionadas

        self.style.configure("TFrame", background=self.transparent_bg, relief="flat")
        self.style.configure("TNotebook", background=self.transparent_bg, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Helvetica", 12, "bold"), padding=[10,5],
                             background=self.accent_bg, foreground="#333")
        self.style.map("TNotebook.Tab", background=[("selected", self.selected_bg)])
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), foreground="#333",
                             padding=6, background=self.accent_bg, relief="flat")
        self.style.configure("TLabel", font=("Helvetica", 12), background=self.transparent_bg)
        
    def create_profile_manager(self):
        top_frame = ttk.Frame(self, style="TFrame")
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.menu_mb = tk.Menubutton(top_frame, text="Menú", relief=tk.RAISED, bg=self.accent_bg)
        self.menu_menu = tk.Menu(self.menu_mb, tearoff=0)
        self.menu_mb.config(menu=self.menu_menu)
        self.menu_mb.pack(side=tk.LEFT, padx=5)
        self.menu_menu.add_command(label="Importar Perfil", command=self.import_profile)
        self.menu_menu.add_command(label="Reiniciar Perfil", command=self.reset_experimental)
        self.menu_menu.add_command(label="Configuración", command=self.open_configuration_window)
        self.profile_mb = tk.Menubutton(top_frame, text="Gestor de Perfiles", relief=tk.RAISED, bg=self.accent_bg)
        self.profile_menu = tk.Menu(self.profile_mb, tearoff=0)
        self.profile_mb.config(menu=self.profile_menu)
        self.profile_mb.pack(side=tk.RIGHT, padx=5)
        self.refresh_btn = ttk.Button(top_frame, text="↻", width=3, command=self.refresh_profile_manager)
        self.refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def open_configuration_window(self):
        config_win = tk.Toplevel(self)
        config_win.title("Configuración")
        config_win.geometry("400x300")
        notebook = ttk.Notebook(config_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tab_general = ttk.Frame(notebook, style="TFrame")
        notebook.add(tab_general, text="General")
        ttk.Label(tab_general, text="Carpeta raíz Experimental:", font=("Helvetica", 10)).pack(pady=5)
        ruta_entry = ttk.Entry(tab_general, width=40)
        ruta_entry.insert(0, self.root_folder_exper)
        ruta_entry.pack(pady=5)
        def seleccionar_carpeta():
            folder = filedialog.askdirectory(initialdir=self.root_folder_exper, title="Selecciona Carpeta Experimental")
            if folder:
                ruta_entry.delete(0, tk.END)
                ruta_entry.insert(0, folder)
        ttk.Button(tab_general, text="Seleccionar carpeta", command=seleccionar_carpeta).pack(pady=5)
        tab_perfiles = ttk.Frame(notebook, style="TFrame")
        notebook.add(tab_perfiles, text="Perfiles por defecto")
        perfiles = [f for f in os.listdir(self.root_folder_exper) if f.lower().endswith(".py")]
        perfiles_py = [os.path.splitext(p)[0] for p in perfiles]
        default_vars = {}
        ttk.Label(tab_perfiles, text="Habilitar perfiles por defecto:", font=("Helvetica", 10)).pack(pady=5)
        for perfil in perfiles_py:
            var = tk.BooleanVar()
            if hasattr(self, 'default_profiles') and perfil in self.default_profiles:
                var.set(True)
            chk = ttk.Checkbutton(tab_perfiles, text=perfil, variable=var)
            chk.pack(anchor="w")
            default_vars[perfil] = var
        def guardar_config():
            config = configparser.ConfigParser()
            config["GENERAL"] = {"ruta_experimental": ruta_entry.get()}
            habilitados = [p for p, var in default_vars.items() if var.get()]
            config["PERFILES"] = {"perfiles_por_defecto": ",".join(habilitados)}
            try:
                with open("config.txt", "w", encoding="utf-8") as cf:
                    config.write(cf)
                messagebox.showinfo("Configuración", "Configuración guardada.")
                self.root_folder_exper = ruta_entry.get()
                self.default_profiles = habilitados
                self.exp_folder_display.config(text=self.root_folder_exper)
                self.refresh_profile_manager()
                self.update_profile_tabs()
                config_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando la configuración: {e}")
        ttk.Button(config_win, text="Guardar configuración", command=guardar_config).pack(pady=5)

    def load_configuration(self):
        self.default_profiles = []
        if os.path.exists("config.txt"):
            config = configparser.ConfigParser()
            try:
                config.read("config.txt", encoding="utf-8")
            except configparser.MissingSectionHeaderError:
                config["GENERAL"] = {"ruta_experimental": self.root_folder_exper}
                config["PERFILES"] = {"perfiles_por_defecto": ""}
            if "GENERAL" in config:
                self.root_folder_exper = config["GENERAL"].get("ruta_experimental", self.root_folder_exper)
            if "PERFILES" in config:
                perfiles = config["PERFILES"].get("perfiles_por_defecto", "")
                self.default_profiles = [p.strip() for p in perfiles.split(",") if p.strip()]
        if hasattr(self, 'exp_folder_display'):
            self.exp_folder_display.config(text=self.root_folder_exper)

    def refresh_profile_manager(self):
        self.profile_menu.delete(0, tk.END)
        files = [f for f in os.listdir(self.root_folder_exper) if f.lower().endswith(".py")]
        for file in files:
            profile_name = os.path.splitext(file)[0]
            if profile_name not in self.profile_vars:
                self.profile_vars[profile_name] = tk.BooleanVar(value=False)
            if hasattr(self, 'default_profiles') and profile_name in self.default_profiles:
                self.profile_vars[profile_name].set(True)
            self.profile_menu.add_checkbutton(label=profile_name, variable=self.profile_vars[profile_name],
                                              command=lambda pn=profile_name: self.update_profile_tabs_for_profile(pn))

    def update_profile_tabs_for_profile(self, profile_name):
        if self.profile_vars.get(profile_name, tk.BooleanVar()).get():
            file_path = os.path.join(self.root_folder_exper, profile_name + ".py")
            if profile_name not in self.profile_tabs:
                self.add_profile_tab(file_path, profile_name)
        else:
            if profile_name in self.profile_tabs:
                self.remove_profile_tab(profile_name)

    def update_profile_tabs(self):
        for profile_name, var in self.profile_vars.items():
            if var.get():
                file_path = os.path.join(self.root_folder_exper, profile_name + ".py")
                if profile_name in self.profile_tabs:
                    embed_frame = self.profile_embeds.get(profile_name)
                    if embed_frame:
                        self.load_profile_in_background(file_path, profile_name, self.profile_tabs[profile_name], embed_frame)
                else:
                    self.add_profile_tab(file_path, profile_name)
            else:
                if profile_name in self.profile_tabs:
                    self.remove_profile_tab(profile_name)

    def add_profile_tab(self, file_path, profile_name):
        new_tab = ttk.Frame(self.notebook, style="TFrame")
        index = self.notebook.index(self.tab_experimental)
        self.notebook.insert(index, new_tab, text=profile_name)
        embed_frame = ttk.Frame(new_tab, relief=tk.SUNKEN, borderwidth=2, style="TFrame")
        embed_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Botón "Recargar" para actualizar la pestaña
        reload_btn = ttk.Button(new_tab, text="Recargar", command=lambda: self.load_profile_in_background(file_path, profile_name, new_tab, embed_frame))
        reload_btn.pack(pady=5)
        self.profile_embeds[profile_name] = embed_frame
        threading.Thread(target=self.load_profile_in_background, args=(file_path, profile_name, new_tab, embed_frame), daemon=True).start()
        self.profile_tabs[profile_name] = new_tab

    # MÉTODO NUEVO: Verificar e instalar dependencias según el código fuente del perfil o experimental.
    def ensure_dependencies(self, source_code, log_function):
        modules = extract_imports(source_code)
        # Determinar módulos de la biblioteca estándar.
        if hasattr(sys, 'stdlib_module_names'):
            stdlib_modules = sys.stdlib_module_names
        else:
            stdlib_modules = {"os", "sys", "tkinter", "subprocess", "threading", "configparser",
                              "re", "time", "math", "random", "string", "json", "csv", "itertools",
                              "functools", "collections", "datetime", "logging"}
        missing = []
        import importlib.util
        for mod in modules:
            if mod in stdlib_modules:
                continue
            spec = importlib.util.find_spec(mod)
            if spec is None:
                missing.append(mod)
        if missing:
            log_function("Faltan dependencias: " + ", ".join(missing) + ". Instalando en segundo plano...")
            command = [sys.executable, "-m", "pip", "install"] + missing
            try:
                subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                log_function("Dependencias instaladas correctamente.")
            except Exception as e:
                log_function(f"Error al instalar dependencias: {e}")

    def load_profile_in_background(self, file_path, profile_name, tab, embed_frame):
        # Leer el contenido del archivo para determinar las dependencias necesarias.
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_code = f.read()
        except Exception as e:
            self.after(0, lambda: self.exp_log(f"Error leyendo el archivo {file_path}: {e}"))
            return
        # Verificar e instalar las dependencias necesarias para el perfil.
        self.ensure_dependencies(file_code, lambda msg: self.after(0, lambda: self.exp_log(msg)))
        # Limpiar el contenedor para evitar acumulación de widgets.
        for widget in embed_frame.winfo_children():
            widget.destroy()
        method1_success = False
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(profile_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            module = None
            method1_error = e
        if module is not None and hasattr(module, "Generalimport"):
            try:
                widget = module.Generalimport(embed_frame)
                widget.pack(fill=tk.BOTH, expand=True)
                if embed_frame.winfo_children():
                    method1_success = True
            except Exception as e:
                method1_error = e
        if not method1_success:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                for widget in embed_frame.winfo_children():
                    widget.destroy()
                local_ns = {"parent_frame": embed_frame, "__builtins__": __builtins__, "tk": tk, "ttk": ttk}
                exec(compile(code, file_path, "exec"), local_ns, local_ns)
                if not embed_frame.winfo_children():
                    raise Exception("El código no creó ninguna interfaz.")
            except Exception as e:
                self.after(0, lambda err=e: tk.Label(embed_frame, text=f"Error al cargar el perfil: {err}", fg="red", bg=self.bg_color).pack())

    def remove_profile_tab(self, profile_name):
        if profile_name in self.profile_tabs:
            self.notebook.forget(self.profile_tabs[profile_name])
            del self.profile_tabs[profile_name]
            if profile_name in self.profile_embeds:
                del self.profile_embeds[profile_name]

    def build_experimental_tab(self, parent):
        exp_top_frame = ttk.Frame(parent, style="TFrame")
        exp_top_frame.pack(fill=tk.X, padx=10, pady=5)
        exp_folder_label = ttk.Label(exp_top_frame, text="Carpeta Raíz Experimental:")
        exp_folder_label.pack(side=tk.LEFT, padx=(0,5))
        self.exp_folder_display = ttk.Label(exp_top_frame, text=self.root_folder_exper, relief=tk.SUNKEN, padding=5)
        self.exp_folder_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        exp_browse_button = ttk.Button(exp_top_frame, text="Seleccionar", command=self.browse_root_folder_exper)
        exp_browse_button.pack(side=tk.LEFT)

        exp_log_frame = ttk.Frame(parent, style="TFrame")
        exp_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.exp_log_area = scrolledtext.ScrolledText(exp_log_frame, wrap=tk.WORD, font=("Helvetica", 12), height=8, state=tk.DISABLED, bg="#ddeeff", fg="#333", insertbackground="#333")
        self.exp_log_area.pack(fill=tk.BOTH, expand=True)

        exp_chat_frame = ttk.Frame(parent, style="TFrame")
        exp_chat_frame.pack(fill=tk.X, padx=10, pady=5)
        self.exp_input_text = tk.Text(exp_chat_frame, wrap=tk.WORD, font=("Helvetica", 12), width=70, height=5, bg="#ddeeff", fg="#333", insertbackground="#333")
        self.exp_input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.exp_send_button = ttk.Button(exp_chat_frame, text="Enviar", command=self.process_experimental)
        self.exp_send_button.pack(side=tk.LEFT)

        action_frame = ttk.Frame(parent, style="TFrame")
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(action_frame, text="Ejecutar código generado", command=self.start_execute_experimental_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Guardar Perfil", command=self.save_profile).pack(side=tk.LEFT, padx=5)

        self.embedded_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=2, style="TFrame")
        self.embedded_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def start_execute_experimental_code(self):
        self.exp_log("Descargando dependencias, instalando y procesando. Por favor espere...")
        threading.Thread(target=self.execute_experimental_code, daemon=True).start()

    def browse_root_folder_exper(self):
        folder = filedialog.askdirectory(initialdir=self.root_folder_exper, title="Selecciona la Carpeta Raíz Experimental")
        if folder:
            self.root_folder_exper = folder
            self.exp_folder_display.config(text=self.root_folder_exper)
            self.exp_log(f"Carpeta raíz Experimental seleccionada: {self.root_folder_exper}")
            self.refresh_profile_manager()

    def exp_log(self, message):
        self.exp_log_area.config(state=tk.NORMAL)
        self.exp_log_area.insert(tk.END, message + "\n")
        self.exp_log_area.config(state=tk.DISABLED)
        self.exp_log_area.see(tk.END)

    def process_experimental(self):
        user_text = self.exp_input_text.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("Advertencia", "Debe ingresar un prompt experimental.")
            return
        self.exp_log("Procesando prompt experimental...")
        conversation_history = self.read_exper_conversation()
        full_prompt = exper_prompt + "\n" + conversation_history + "\n" + user_text
        self.exp_input_text.delete("1.0", tk.END)
        threading.Thread(target=self._process_experimental_thread, args=(full_prompt, user_text), daemon=True).start()

    def _process_experimental_thread(self, prompt, user_text):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
            response = model.generate_content(prompt)
            code_text = clean_code_block(response.text.strip() if hasattr(response, "text") else "")
            self.after(0, lambda: self.exp_log("Código recibido de Gemini."))
            self.latest_experimental_code = code_text
            self.append_exper_conversation("User: " + user_text)
            self.append_exper_conversation("Generated Code: " + code_text)
            self.after(0, lambda: self.exp_log("Presione 'Ejecutar código generado' para integrar la interfaz en este panel."))
        except Exception as e:
            self.after(0, lambda: self.exp_log(f"Error en el proceso experimental: {e}"))

    def read_exper_conversation(self):
        if os.path.exists(TEMP_CONVERSATION_FILE):
            with open(TEMP_CONVERSATION_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def append_exper_conversation(self, text):
        with open(TEMP_CONVERSATION_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def execute_experimental_code(self):
        # Se obtiene el código experimental a ejecutar
        generated_code = ""
        if os.path.exists(TEMP_CONVERSATION_FILE):
            try:
                with open(TEMP_CONVERSATION_FILE, "r", encoding="utf-8") as f:
                    temp_content = f.read()
                if temp_content and "Generated Code:" in temp_content:
                    parts = temp_content.split("Generated Code:")
                    generated_code = parts[-1].strip()
                else:
                    generated_code = self.latest_experimental_code or ""
            except Exception as e:
                self.after(0, lambda: self.exp_log(f"Error leyendo el archivo temporal: {e}"))
                generated_code = self.latest_experimental_code or ""
        else:
            generated_code = self.latest_experimental_code or ""
        if not generated_code:
            self.after(0, lambda: messagebox.showwarning("Advertencia", "No hay código experimental generado."))
            return
        # Verificar e instalar dependencias necesarias para el código experimental.
        self.ensure_dependencies(generated_code, lambda msg: self.after(0, lambda: self.exp_log(msg)))
        self.after(0, lambda: self.exp_log("Ejecutando código experimental desde el archivo de conversación..."))
        def run_generated_code():
            for widget in self.embedded_frame.winfo_children():
                widget.destroy()
            success = False
            try:
                temp_ns = {}
                exec(compile(generated_code, "<experimental>", "exec"), temp_ns)
                if "Generalimport" in temp_ns:
                    widget = temp_ns["Generalimport"](self.embedded_frame)
                    widget.pack(fill=tk.BOTH, expand=True)
                    success = True
            except Exception as e:
                pass
            if not success:
                try:
                    local_ns = {"parent_frame": self.embedded_frame, "__builtins__": __builtins__, "tk": tk, "ttk": ttk}
                    exec(compile(generated_code, "<experimental>", "exec"), local_ns)
                    if not self.embedded_frame.winfo_children():
                        raise Exception("El código no creó ninguna interfaz.")
                    success = True
                except Exception as e:
                    self.exp_log(f"Error al ejecutar el código: {e}")
            if success:
                self.exp_log("Código ejecutado correctamente. La interfaz se ha integrado en el panel inferior.")
        self.after(0, run_generated_code)

    def save_profile(self):
        if not self.latest_experimental_code:
            messagebox.showwarning("Advertencia", "No hay código para guardar.")
            return
        default_name = self.current_profile_name if self.current_profile_name else ""
        profile_name = simpledialog.askstring("Guardar Perfil", "Introduce el nombre para el perfil:", initialvalue=default_name)
        if not profile_name:
            return
        file_name = profile_name + ".py"
        file_path = os.path.join(self.root_folder_exper, file_name)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.latest_experimental_code)
            self.exp_log(f"Perfil guardado en: {file_path}")
            if profile_name in self.profile_tabs:
                embed_frame = self.profile_embeds.get(profile_name)
                if embed_frame:
                    self.load_profile_in_background(file_path, profile_name, self.profile_tabs[profile_name], embed_frame)
            else:
                self.add_profile_tab(file_path, profile_name)
            self.current_profile_name = profile_name
            if profile_name in self.profile_vars:
                self.profile_vars[profile_name].set(True)
            else:
                self.profile_vars[profile_name] = tk.BooleanVar(value=True)
            self.refresh_profile_manager()
            if os.path.exists(TEMP_CONVERSATION_FILE):
                os.remove(TEMP_CONVERSATION_FILE)
        except Exception as e:
            self.exp_log(f"Error al guardar el perfil: {e}")

    def import_profile(self):
        file_path = filedialog.askopenfilename(initialdir=self.root_folder_exper, title="Selecciona el perfil a importar", filetypes=(("Python Files", "*.py"),))
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                with open(TEMP_CONVERSATION_FILE, "w", encoding="utf-8") as tf:
                    tf.write(code)
                self.latest_experimental_code = code
                self.current_profile_name = os.path.splitext(os.path.basename(file_path))[0]
                self.exp_log(f"Perfil importado desde: {file_path}")
                for widget in self.embedded_frame.winfo_children():
                    widget.destroy()
                success = False
                try:
                    temp_ns = {}
                    exec(compile(code, file_path, "exec"), temp_ns)
                    if "Generalimport" in temp_ns:
                        widget = temp_ns["Generalimport"](self.embedded_frame)
                        widget.pack(fill=tk.BOTH, expand=True)
                        success = True
                except Exception as e:
                    pass
                if not success:
                    try:
                        local_ns = {"parent_frame": self.embedded_frame, "__builtins__": __builtins__, "tk": tk, "ttk": ttk}
                        exec(compile(code, file_path, "exec"), local_ns)
                        if not self.embedded_frame.winfo_children():
                            raise Exception("El código no creó ninguna interfaz.")
                        success = True
                    except Exception as e:
                        self.exp_log(f"Error al cargar el perfil importado: {e}")
                if success:
                    self.exp_log("Perfil importado y cargado correctamente en la pestaña experimental.")
            except Exception as e:
                self.exp_log(f"Error al importar el perfil: {e}")

    def reset_experimental(self):
        if os.path.exists(TEMP_CONVERSATION_FILE):
            os.remove(TEMP_CONVERSATION_FILE)
        self.latest_experimental_code = ""
        self.exp_log_area.config(state=tk.NORMAL)
        self.exp_log_area.delete("1.0", tk.END)
        self.exp_log_area.config(state=tk.DISABLED)
        self.exp_log("Conversación y código experimental reiniciados.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
