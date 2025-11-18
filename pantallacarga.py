import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk 
import time
import threading
import subprocess
import os
import sys
import queue

class LoadingScreen(tk.Toplevel):
    def __init__(self, parent, on_load_complete=None):
        super().__init__(parent)
        self.parent = parent
        self.on_load_complete = on_load_complete
        
        # VENTANA
        self.title("Cargando...")
        self.attributes('-fullscreen', True)
        self.overrideredirect(True)
        
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # COLA PARA COMUNICACIÓN SEGURA
        self.queue = queue.Queue()
        
        self.create_widgets()
        self.progress_value = 0
        self.after_id = None

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#FFFFFF")
        main_frame.pack(expand=True, fill="both")

        logo_path = "logo.png"
        
        if os.path.exists(logo_path):
            try:
                original_image = Image.open(logo_path)
                new_height = int(self.screen_height * 0.7)
                aspect_ratio = original_image.width / original_image.height
                new_width = int(new_height * aspect_ratio)

                resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
                self.logo_image_tk = ImageTk.PhotoImage(resized_image)
                logo_label = tk.Label(main_frame, image=self.logo_image_tk, bg="#FFFFFF")
                logo_label.pack(pady=(self.screen_height // 10, self.screen_height // 20))
            except Exception as e:
                print(f"Error al cargar 'logo.png': {e}. Usando placeholder de texto.")
                self.create_text_logo_placeholder(main_frame)
        else:
            print("Advertencia: 'logo.png' no encontrado. Usando placeholder de texto.")
            self.create_text_logo_placeholder(main_frame)

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", 
                                           length=self.screen_width // 2, mode="determinate")
        self.progress_bar.place(relx=0.5, rely=0.85, anchor="center")

        s = ttk.Style()
        s.theme_use('default')
        s.configure("TProgressbar", thickness=30, troughcolor='lightgray', 
                   background='#4CAF50', bordercolor='gray', lightcolor='white', darkcolor='darkgray')
        self.progress_bar.config(style="TProgressbar")

    def create_text_logo_placeholder(self, parent_frame):
        logo_container = tk.Frame(parent_frame, bg="#FFFFFF")
        logo_container.pack(pady=(self.screen_height // 10, self.screen_height // 20))

        canvas_width = int(self.screen_width * 0.45)
        canvas_height = int(self.screen_height * 0.45) 
        canvas = tk.Canvas(logo_container, width=canvas_width, height=canvas_height, 
                          bg="#FFFFFF", highlightthickness=0)
        canvas.pack()

        center_x, center_y = canvas_width // 2, canvas_height // 2
        radius = int(canvas_width / 5)
        
        offset = int(radius / 2)
        canvas.create_oval(center_x - radius - offset, center_y - radius - offset, 
                          center_x - offset, center_y - offset, fill="red", outline="red")
        canvas.create_oval(center_x + offset, center_y - radius - offset, 
                          center_x + radius + offset, center_y - offset, fill="yellow", outline="yellow")
        canvas.create_oval(center_x - radius - offset, center_y + offset, 
                          center_x - offset, center_y + radius + offset, fill="blue", outline="blue")
        canvas.create_oval(center_x + offset, center_y + offset, 
                          center_x + radius + offset, center_y + radius + offset, fill="green", outline="green")

        text_frame = tk.Frame(parent_frame, bg="#FFFFFF")
        text_frame.pack(pady=(self.screen_height // 40, 0))

        colors = {"M": "red", "I": "blue", "N": "green", "D": "orange"}
        for char in "MIND":
            label = tk.Label(text_frame, text=char, font=("Comic Sans MS", 120, "bold"), 
                           bg="#FFFFFF", fg=colors.get(char, "black"))
            label.pack(side=tk.LEFT, padx=5)

    def process_queue(self):
        """PROCESA MENSAJES DEL HILO SECUNDARIO"""
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg == "update":
                    self.progress_bar["value"] = self.progress_value
                elif msg == "done":
                    self.finish_loading()
                    return
        except queue.Empty:
            pass
        
        self.after_id = self.after(50, self.process_queue)

    def finish_loading(self):
        """CIERRA VENTANA Y EJECUTA CALLBACK"""
        if self.after_id:
            self.after_cancel(self.after_id)
        self.destroy()
        if self.on_load_complete:
            self.on_load_complete()

def simulate_heavy_task(loading_screen):
    """CORRE EN HILO SECUNDARIO - SOLO CALCULA"""
    print("Iniciando tarea pesada (simulada)...")
    total_steps = 50
    
    for i in range(total_steps):
        time.sleep(0.1)
        loading_screen.progress_value = int(((i + 1) / total_steps) * 100)
        loading_screen.queue.put("update")
        
    loading_screen.queue.put("done")
    print("Tarea pesada completada.")

def open_game_menu():
    """Abre el menú de juegos"""
    game_menu_folder = "menu de juegos"
    game_menu_file = "menu_de_juegos.py"
    full_path = os.path.abspath(os.path.join(game_menu_folder, game_menu_file))

    if not os.path.exists(full_path):
        print(f"Error: El archivo '{game_menu_file}' no se encontró en '{game_menu_folder}'.")
        return

    try:
        # ❗ CORREGIDO: Usar full_path en lugar de script_path
        cmd = [sys.executable, "-u", full_path]
        
        # ❗ CORREGIDO: Añadir flag para Windows
        if sys.platform == "win32":
            subprocess.Popen(cmd, cwd=os.path.abspath(game_menu_folder), 
                           creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen(cmd, cwd=os.path.abspath(game_menu_folder))
            
        print(f"✅ Abriendo {game_menu_file}")
    except Exception as e:
        print(f"❌ Error al abrir el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    def on_loading_finished():
        root.destroy()
        open_game_menu()
        print("Carga completa y menú de juegos iniciado.")

    loading_screen = LoadingScreen(root, on_load_complete=on_loading_finished)
    loading_screen.process_queue()
    
    task_thread = threading.Thread(target=simulate_heavy_task, args=(loading_screen,))
    task_thread.start()

    root.mainloop()