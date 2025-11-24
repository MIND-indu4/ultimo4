import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import platform
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ========== CONFIGURACIÓN DEL SISTEMA ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_OS = platform.system()

def get_system_font():
    if SYSTEM_OS == "Windows":
        return "Arial"
    else:
        return "DejaVu Sans"

SYSTEM_FONT = get_system_font()

# --- CONFIGURACIÓN VISUAL ---
class Config:
    MAIN_BG_COLOR = "#00C853"    # Verde fondo
    CARD_COLOR = "#FFFFFF"       # Blanco tarjeta
    TEXT_COLOR = "#212121"       # Gris oscuro (Casi negro)
    BUTTON_BORDER = "#64DD17"    # Verde borde botón
    BLACK_TEXT = "#000000"       # Texto negro

class MathMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matemáticas - Menú")
        
        # --- CORRECCIÓN APLICADA AQUÍ ---
        # Actualizamos tareas pendientes para asegurar que lee bien el tamaño de pantalla
        self.root.update_idletasks()
        
        if SYSTEM_OS == "Windows":
            self.root.state("zoomed")
            self.root.attributes("-fullscreen", True)
        else:
            # Para RASPBERRY PI (Linux):
            # 1. Obtenemos ancho y alto
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            
            # 2. Forzamos el tamaño de la ventana inmediatamente para que no sea pequeña
            self.root.geometry(f"{w}x{h}+0+0")
            
            # 3. Usamos .after() para esperar 100ms antes de activar el fullscreen.
            # Esto da tiempo al sistema gráfico de la Raspberry a "despertar".
            self.root.after(100, lambda: self.root.attributes("-fullscreen", True))
        
        self.root.configure(bg=Config.MAIN_BG_COLOR)
        self.root.bind("<Escape>", lambda e: self.go_back())

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.base_width = 1280
        self.base_height = 720
        self.scale = min(self.screen_width / self.base_width, self.screen_height / self.base_height)

        self.icons = {}
        self.load_my_images() 
        self.create_interface()

    def load_my_images(self):
        """Carga las imágenes PNG"""
        # Tamaño reducido para que se vea delicado dentro del cuadro
        icon_size = int(110 * self.scale) 

        image_files = {
            "cuantos_hay": "cuantos_hay.jpg",
            "traduce": "traduce.jpg",
            "lectura": "lectura.jpg",
            "construccion": "construccion.jpg",
            "cual_falta": "cual_falta.jpg"
        }

        for key, filename in image_files.items():
            path = os.path.join(SCRIPT_DIR, filename)
            
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                    self.icons[key] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error al leer {filename}: {e}")
            else:
                print(f"⚠️ FALTA LA IMAGEN: {filename}")

    def create_interface(self):
        self.canvas = tk.Canvas(self.root, bg=Config.MAIN_BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- TARJETA BLANCA ---
        margin_x = int(100 * self.scale)
        margin_y = int(50 * self.scale)
        
        card_x1, card_y1 = margin_x, margin_y
        card_x2, card_y2 = self.screen_width - margin_x, self.screen_height - margin_y
        
        self.create_rounded_rect(card_x1, card_y1, card_x2, card_y2, 
                                 radius=int(40*self.scale), fill=Config.CARD_COLOR, outline="")

        # --- TÍTULO ---
        title_font_size = int(70 * self.scale) 
        
        self.canvas.create_text(self.screen_width // 2, card_y1 + int(100 * self.scale), 
                                text="Matemáticas", 
                                font=(SYSTEM_FONT, title_font_size, "bold"), 
                                fill=Config.TEXT_COLOR)

        # --- BOTONES ---
        btn_size = int(150 * self.scale) 
        spacing = int(80 * self.scale)
        
        start_y_row1 = card_y1 + int(220 * self.scale)
        start_y_row2 = start_y_row1 + btn_size + int(80 * self.scale) 
        center_x = self.screen_width // 2
        
        # FILA 1
        self.create_game_btn(center_x - btn_size - spacing, start_y_row1, btn_size, "cuantos_hay", "¿Cuántos hay?", 1)
        self.create_game_btn(center_x, start_y_row1, btn_size, "cual_falta", "¿Cuál falta?", 5)
        self.create_game_btn(center_x + btn_size + spacing, start_y_row1, btn_size, "lectura", "LECTURA\nNUMÉRICA", 3)

        # FILA 2
        offset_row2 = (btn_size + spacing) // 2
        self.create_game_btn(center_x - offset_row2, start_y_row2, btn_size, "traduce", "TRADUCE LA\nOPERACIÓN", 2)
        self.create_game_btn(center_x + offset_row2, start_y_row2, btn_size, "construccion", "CONSTRUCCIÓN\nNUMÉRICA", 4)

        # --- BOTÓN ATRÁS ---
        self.create_back_button(card_x1, card_y2)

    def create_game_btn(self, x, y, size, icon_key, text, level_num):
        half = size // 2
        
        # Cuadrado blanco con borde verde
        rect_id = self.create_rounded_rect(x - half, y - half, x + half, y + half, 
                                           radius=20, fill="white", outline=Config.BUTTON_BORDER, width=3)
        
        # Imagen
        if icon_key in self.icons:
            self.canvas.create_image(x, y, image=self.icons[icon_key])
        else:
            self.canvas.create_text(x, y, text="[IMG]", fill="gray", font=("Arial", 20))
        
        # Texto inferior
        text_y = y + half + int(25 * self.scale)
        font_size = int(14 * self.scale)
        
        # Usamos Comic Sans si es Windows, o DejaVu si es Linux
        font_family = "Comic Sans MS" if SYSTEM_OS == "Windows" else "DejaVu Sans"

        text_id = self.canvas.create_text(x, text_y, text=text, justify="center",
                                          font=(font_family, font_size, "bold"), fill="black")
        
        # Hitbox
        hitbox = self.canvas.create_rectangle(x - half, y - half, x + half, text_y + 30, fill="", outline="")
        self.canvas.tag_bind(hitbox, "<Button-1>", lambda e: self.launch_level(level_num))
        self.canvas.tag_bind(rect_id, "<Button-1>", lambda e: self.launch_level(level_num))
        self.canvas.tag_bind(text_id, "<Button-1>", lambda e: self.launch_level(level_num))

    def create_back_button(self, card_x1, card_y2):
        back_btn_radius = int(35 * self.scale)
        back_x = card_x1 + int(80 * self.scale)
        back_y = card_y2 - int(80 * self.scale)
        
        self.canvas.create_oval(back_x - back_btn_radius, back_y - back_btn_radius,
                                back_x + back_btn_radius, back_y + back_btn_radius,
                                fill=Config.MAIN_BG_COLOR, outline="")
        
        arrow_w = int(15 * self.scale)
        self.canvas.create_line(back_x + arrow_w, back_y, back_x - arrow_w, back_y, fill="white", width=5, capstyle="round")
        self.canvas.create_line(back_x - arrow_w, back_y, back_x, back_y - arrow_w, fill="white", width=5, capstyle="round")
        self.canvas.create_line(back_x - arrow_w, back_y, back_x, back_y + arrow_w, fill="white", width=5, capstyle="round")
        
        back_hitbox = self.canvas.create_rectangle(back_x - back_btn_radius, back_y - back_btn_radius,
                                                   back_x + back_btn_radius, back_y + back_btn_radius,
                                                   fill="", outline="")
        self.canvas.tag_bind(back_hitbox, "<Button-1>", lambda e: self.go_back())

    def launch_level(self, level):
        script_name = f"nivel{level}.py"
        folder_name = f"nivel{level}"
        path = os.path.join(SCRIPT_DIR, "..", folder_name, script_name)
        path = os.path.normpath(path)
        
        if os.path.exists(path):
            self.root.destroy()
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, path], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, path])
        else:
            messagebox.showerror("Error", f"No se encuentra el nivel {level}:\n{path}")

    def go_back(self):
        path = os.path.join(SCRIPT_DIR, "..", "..", "menu_de_juegos.py")
        path = os.path.normpath(path)
        self.root.destroy()
        if os.path.exists(path):
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, path], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, path])

    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MathMenuApp(root)
    root.mainloop()