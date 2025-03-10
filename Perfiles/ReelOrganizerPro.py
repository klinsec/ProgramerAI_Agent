import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import google.generativeai as genai

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

# --------------------- CONFIGURACIÓN DE LA API Y PROMPTS ---------------------
API_KEY = load_api_key()
genai.configure(api_key=API_KEY)
custom_prompt = load_custom_prompt()
guion_prompt = load_guion_prompt()

# Carpeta raíz para reels
DEFAULT_ROOT_REELS = r".\Reels"
if not os.path.exists(DEFAULT_ROOT_REELS):
    os.makedirs(DEFAULT_ROOT_REELS)

# --------------------- CLASE GENERAL PARA IMPORTAR LA INTERFAZ ---------------------
class Generalimport(tk.Frame):
    """
    Esta clase implementa el organizador de Reels como un widget (Frame).
    Se puede instanciar directamente en cualquier contenedor del programa principal.
    """
    def __init__(self, parent):
        super().__init__(parent, bg="#e6f2ff")
        self.parent = parent
        self.configure(bg="#e6f2ff")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._set_styles()

        # Variables de funcionamiento
        self.root_folder = DEFAULT_ROOT_REELS
        self.conversation_text = ""
        self.topic = ""
        self.subtopics = []
        self.tree_paths = {}

        # Construir la interfaz
        self._build_interface()

    def _set_styles(self):
        self.style.configure("TFrame", background="#e6f2ff")
        self.style.configure("TLabel", font=("Helvetica", 12), background="#e6f2ff")
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), padding=6)
        self.style.configure("Treeview", font=("Helvetica", 11), rowheight=25, background="#e6f2ff")

    def _build_interface(self):
        # Panel superior para seleccionar la carpeta raíz
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(top_frame, text="Carpeta Raíz Reels:").pack(side=tk.LEFT, padx=(0,5))
        self.folder_label = ttk.Label(top_frame, text=self.root_folder, relief=tk.SUNKEN, padding=5)
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(top_frame, text="Seleccionar", command=self._browse_root).pack(side=tk.LEFT)
        
        # Área de log
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Helvetica", 12), height=10, state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Área de entrada
        chat_frame = ttk.Frame(self)
        chat_frame.pack(fill=tk.X, padx=10, pady=5)
        self.input_text = tk.Text(chat_frame, wrap=tk.WORD, font=("Helvetica", 12), width=70, height=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(chat_frame, text="Enviar", command=self.process_input).pack(side=tk.LEFT)
        
        # Árbol de carpetas
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(tree_frame, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.populate_tree()

    def _browse_root(self):
        folder = filedialog.askdirectory(initialdir=self.root_folder, title="Selecciona la Carpeta Raíz Reels")
        if folder:
            self.root_folder = folder
            self.folder_label.config(text=folder)
            self.log(f"Carpeta raíz actualizada: {folder}")
            self.populate_tree()

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def process_input(self):
        user_text = self.input_text.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("Advertencia", "Ingrese un texto.")
            return
        self.log("Procesando texto...")
        prompt = custom_prompt + "\n" + user_text
        self.input_text.delete("1.0", tk.END)
        threading.Thread(target=self._process_gemini_thread, args=(prompt, user_text), daemon=True).start()

    def _process_gemini_thread(self, prompt, user_text):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
            response = model.generate_content(prompt)
            resp_text = response.text.strip() if hasattr(response, "text") else ""
            self.log(f"Respuesta de Gemini: {resp_text}")
            parts = [p.strip() for p in resp_text.split(",") if p.strip()]
            if not parts:
                self.log("No se extrajo tema y subtemas.")
                return
            self.topic = parts[0]
            self.subtopics = parts[1:]
            self.log(f"Tema: {self.topic}")
            self.log(f"Subtemas: {', '.join(self.subtopics)}")
            topic_folder = os.path.join(self.root_folder, self.topic)
            os.makedirs(topic_folder, exist_ok=True)
            os.makedirs(os.path.join(topic_folder, "exportados"), exist_ok=True)
            for sub in self.subtopics:
                sub_folder = os.path.join(topic_folder, sub)
                os.makedirs(sub_folder, exist_ok=True)
                recursos_folder = os.path.join(sub_folder, "recursos")
                os.makedirs(recursos_folder, exist_ok=True)
                os.makedirs(os.path.join(recursos_folder, "imagenes"), exist_ok=True)
                os.makedirs(os.path.join(recursos_folder, "videos"), exist_ok=True)
                os.makedirs(os.path.join(sub_folder, "exportados"), exist_ok=True)
            conv_file = os.path.join(topic_folder, "conversacion.txt")
            with open(conv_file, "w", encoding="utf-8") as f:
                f.write(user_text)
            self.log(f"Estructura creada en: {topic_folder}")
            self.populate_tree()
            self.generate_scripts(topic_folder, user_text)
        except Exception as e:
            self.log(f"Error en proceso: {e}")

    def generate_scripts(self, topic_folder, conversation_text):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
            counter = 1
            for sub in self.subtopics:
                if sub.lower() == "exportados":
                    continue
                sub_folder = os.path.join(topic_folder, sub)
                script_file = os.path.join(sub_folder, "guion.txt")
                if os.path.exists(script_file):
                    self.log(f"Guion ya existe para '{sub}', se omite.")
                    continue
                prompt_script = f"{conversation_text}\n{guion_prompt}\nSubtema: {sub}"
                self.log(f"Generando guion para '{sub}' (contador {counter})...")
                response = model.generate_content(prompt_script)
                script_text = response.text.strip() if hasattr(response, "text") else "No se obtuvo respuesta."
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(script_text)
                self.log(f"Guion creado en: {script_file}")
                counter += 1
        except Exception as e:
            self.log(f"Error en generate_scripts: {e}")

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_paths = {}
        if not os.path.exists(self.root_folder):
            return
        for topic in os.listdir(self.root_folder):
            topic_path = os.path.join(self.root_folder, topic)
            if os.path.isdir(topic_path):
                node = self.tree.insert("", "end", text=topic, open=True)
                self.tree_paths[node] = topic_path
                for sub in os.listdir(topic_path):
                    sub_path = os.path.join(topic_path, sub)
                    if os.path.isdir(sub_path) and sub.lower() != "exportados":
                        sub_node = self.tree.insert(node, "end", text=sub, open=True)
                        self.tree_paths[sub_node] = sub_path

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            item_text = self.tree.item(sel[0], "text")
            self.log(f"Seleccionado: {item_text}")

# --------------------- EJECUCIÓN INDEPENDIENTE ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Creador de Reels")
    root.geometry("900x750")
    app = Generalimport(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
