import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess
import platform

# ========== CONFIGURACIÓN DE SISTEMA ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_OS = platform.system()

def get_system_font():
    return "Arial" if SYSTEM_OS == "Windows" else "DejaVu Sans"

SYSTEM_FONT = get_system_font()

# --- CONFIGURACIÓN VISUAL ---
class GameConfig:
    MAIN_COLOR = "#00C853"       
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    DIVIDER_COLOR = "#E0E0E0"    
    
    # Nombres de las imágenes
    # [0]=Mil (Fútbol), [1]=Centena (Basquet), [2]=Decena (Tenis), [3]=Unidad (Voley)
    BALL_TYPES = ["futbol.png", "basquet.png", "tenis.png", "voley.jpg"]

# --- FUNCIONES AUXILIARES ---
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
              x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class MathDragGameLevel3:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 3")
        
        if SYSTEM_OS == "Windows":
            master.attributes("-fullscreen", True)
        else:
            master.attributes("-fullscreen", True)
            
        master.configure(bg=GameConfig.MAIN_COLOR)
        master.bind("<Escape>", self.volver_al_menu)

        # Escala
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        self.scale = min(screen_width / 1280, screen_height / 800)

        # Fuentes
        self.font_title = (SYSTEM_FONT, int(24 * self.scale), "bold")
        self.font_header = (SYSTEM_FONT, int(16 * self.scale), "bold") 
        self.font_number = (SYSTEM_FONT, int(50 * self.scale), "bold") 
        self.font_btn = (SYSTEM_FONT, int(14 * self.scale), "bold")
        
        self.ball_size = int(70 * self.scale) 
        
        # Variables de arrastre
        self.drag_data = {"item": None, "type_index": None, "offset_x": 0, "offset_y": 0}
        self.columns_content = [[], [], [], []] 

        self._create_gui()
        self._start_new_round()

    def _create_gui(self):
        self.main_canvas = tk.Canvas(self.master, bg=GameConfig.MAIN_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        cw = int(sw * 0.90)
        ch = int(sh * 0.90)
        cx = sw // 2
        cy = sh // 2
        
        create_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR)

        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=cw-40, height=ch-40)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="⬅ Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", lambda e: self.volver_al_menu())

        # Título
        tk.Label(self.content_frame, text="Representa el número arrastrando las pelotas", font=self.font_title, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).pack(pady=(10, 10))

        # NÚMERO OBJETIVO
        self.frame_top = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_top.pack(pady=10)

        self.lbl_number_display = tk.Label(self.frame_top, text="0000", font=self.font_number, 
                                           fg=GameConfig.MAIN_COLOR, bg="white",
                                           bd=2, relief="solid", padx=30, pady=5)
        self.lbl_number_display.pack()

        # COLUMNAS
        self.frame_columns = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_columns.pack(expand=True, fill="both", padx=20, pady=10)
        
        for i in range(7):
            w_val = 1 if i % 2 == 0 else 0
            self.frame_columns.columnconfigure(i, weight=w_val)
        self.frame_columns.rowconfigure(1, weight=1)

        headers = ["Unidad de Mil", "Centena", "Decena", "Unidad"]
        bg_cols = ["#E8F5E9", "#E3F2FD", "#FFF3E0", "#FCE4EC"] 
        self.column_frames = [] 

        for i, title in enumerate(headers):
            grid_col = i * 2
            tk.Label(self.frame_columns, text=title, font=self.font_header, 
                     bg=GameConfig.CARD_COLOR, fg="#555").grid(row=0, column=grid_col, pady=(0,5))
            
            drop_area = tk.Frame(self.frame_columns, bg=bg_cols[i], bd=1, relief="solid") 
            drop_area.grid(row=1, column=grid_col, sticky="nsew", padx=2)
            self.column_frames.append(drop_area)

            if i < 3:
                sep = tk.Frame(self.frame_columns, bg=GameConfig.DIVIDER_COLOR, width=2)
                sep.grid(row=0, column=grid_col+1, rowspan=2, sticky="ns", padx=2)

        # FUENTE DE PELOTAS
        self.frame_source = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_source.pack(pady=20, fill="x")

        self.source_images = []
        labels_pelotas = ["1000", "100", "10", "1"]
        
        for i, btype in enumerate(GameConfig.BALL_TYPES):
            img = self.crear_imagen_pelota(btype, labels_pelotas[i])
            self.source_images.append(img)
            
            container = tk.Frame(self.frame_source, bg=GameConfig.CARD_COLOR)
            container.pack(side="left", expand=True)
            
            lbl = tk.Label(container, image=img, bg=GameConfig.CARD_COLOR, cursor="hand2")
            lbl.pack()
            tk.Label(container, text=labels_pelotas[i], font=self.font_btn, bg=GameConfig.CARD_COLOR).pack()
            
            # VINCULAR CLIC A LA PELOTA ORIGINAL
            lbl.bind("<Button-1>", lambda e, idx=i: self.start_spawn_drag(e, idx))
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def _start_new_round(self):
        for col_list in self.columns_content:
            for widget in col_list:
                widget.destroy()
            col_list.clear()

        d1 = random.randint(1, 3) 
        d2 = random.randint(1, 4) 
        d3 = random.randint(1, 5) 
        d4 = random.randint(1, 5) 
        
        self.target_number_str = f"{d1}{d2}{d3}{d4}"
        self.lbl_number_display.config(text=self.target_number_str)
        self.targets = [d1, d2, d3, d4]

    # --- ARRASTRE ---
    def start_spawn_drag(self, event, type_index):
        img = self.source_images[type_index]
        drag_lbl = tk.Label(self.content_frame, image=img, bg=GameConfig.CARD_COLOR, bd=0)
        drag_lbl.image = img 
        
        # Usamos coordenadas globales para calcular la posición inicial
        root_x = event.x_root
        root_y = event.y_root
        
        frame_x = self.content_frame.winfo_rootx()
        frame_y = self.content_frame.winfo_rooty()
        
        # Centramos la nueva pelota en el mouse
        start_x = root_x - frame_x - (self.ball_size // 2)
        start_y = root_y - frame_y - (self.ball_size // 2)
        
        drag_lbl.place(x=start_x, y=start_y)
        drag_lbl.lift()
        
        self.drag_data["item"] = drag_lbl
        self.drag_data["type_index"] = type_index

    def do_drag(self, event):
        # Se llama al mover el mouse sobre la pelota original, pero mueve la copia
        widget = self.drag_data["item"]
        if not widget: return
        
        x_root = event.x_root
        y_root = event.y_root
        
        frame_x = self.content_frame.winfo_rootx()
        frame_y = self.content_frame.winfo_rooty()
        
        new_x = x_root - frame_x - (self.ball_size // 2)
        new_y = y_root - frame_y - (self.ball_size // 2)
        
        widget.place(x=new_x, y=new_y)

    def end_drag(self, event):
        widget = self.drag_data["item"]
        idx = self.drag_data["type_index"]
        self.drag_data["item"] = None
        
        if not widget: return

        drop_x = event.x_root
        drop_y = event.y_root
        
        col_found = -1
        
        for i, frame in enumerate(self.column_frames):
            fx = frame.winfo_rootx()
            fy = frame.winfo_rooty()
            fw = frame.winfo_width()
            fh = frame.winfo_height()
            
            if fx < drop_x < fx + fw and fy < drop_y < fy + fh:
                col_found = i
                break
        
        if col_found != -1 and col_found == idx:
            self.add_ball_to_column(col_found, idx)
            widget.destroy() 
        else:
            widget.destroy()

    def add_ball_to_column(self, col_idx, ball_type_idx):
        frame = self.column_frames[col_idx]
        img = self.source_images[ball_type_idx]
        
        lbl = tk.Label(frame, image=img, bg=frame.cget("bg")) 
        lbl.image = img
        lbl.bind("<Button-1>", lambda e, c=col_idx, w=lbl: self.remove_ball(c, w))
        
        self.columns_content[col_idx].append(lbl)
        self.reorganize_column(col_idx)
        self.check_win()

    def remove_ball(self, col_idx, widget):
        if widget in self.columns_content[col_idx]:
            self.columns_content[col_idx].remove(widget)
            widget.destroy()
            self.reorganize_column(col_idx)

    def reorganize_column(self, col_idx):
        items = self.columns_content[col_idx]
        frame = self.column_frames[col_idx]
        for w in items: w.place_forget()
            
        cols_visual = 2
        w_ball = self.ball_size
        
        frame_w = frame.winfo_width()
        start_x = (frame_w - (cols_visual * w_ball)) // 2
        if start_x < 0: start_x = 0
        
        for i, widget in enumerate(items):
            row = i // cols_visual
            col = i % cols_visual
            px = start_x + (col * w_ball)
            py = (row * w_ball) + 5
            widget.place(x=px, y=py)

    def check_win(self):
        current_counts = [len(col) for col in self.columns_content]
        if current_counts == self.targets:
            self.master.after(300, self.game_win)

    def game_win(self):
        win = tk.Toplevel(self.master)
        win.title("¡Ganaste!")
        w, h = 400, 280
        cx = self.master.winfo_screenwidth() // 2
        cy = self.master.winfo_screenheight() // 2
        win.geometry(f"{w}x{h}+{cx-w//2}+{cy-h//2}")
        win.configure(bg="white")
        win.overrideredirect(True)
        win.attributes("-topmost", True)

        tk.Frame(win, bg=GameConfig.MAIN_COLOR, height=15).pack(fill="x")
        tk.Label(win, text="¡Muy Bien!", font=("Arial", 26, "bold"), bg="white", fg=GameConfig.MAIN_COLOR).pack(pady=(30, 10))
        tk.Label(win, text="¡Número completado!", font=("Arial", 14), bg="white", fg="#555").pack(pady=10)
        
        btn = tk.Label(win, text="Siguiente Ejercicio", font=("Arial", 14, "bold"),
                       bg=GameConfig.MAIN_COLOR, fg="white", padx=20, pady=10, cursor="hand2")
        btn.pack(pady=20)
        btn.bind("<Button-1>", lambda e: (win.destroy(), self._start_new_round()))

    # --- DIBUJO DE PELOTAS ---
    def crear_imagen_pelota(self, nombre_archivo, texto_numero):
        s = self.ball_size
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        item_img = None
        rutas = [
            nombre_archivo,
            os.path.join("imagenes", nombre_archivo),
            os.path.join("assets", nombre_archivo),
            os.path.join("..", "nivel1", nombre_archivo),
            os.path.join("..", "nivel2", nombre_archivo)
        ]
        
        for r in rutas:
            if os.path.exists(os.path.join(SCRIPT_DIR, r)):
                try:
                    item_img = Image.open(os.path.join(SCRIPT_DIR, r)).convert("RGBA")
                    break
                except: pass

        if item_img:
            img_res = item_img.resize((s, s), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_res)
        else:
            # DIBUJOS AUTOMÁTICOS
            if "futbol" in nombre_archivo:
                # Blanco y negro
                draw.ellipse([2, 2, s-2, s-2], fill="white", outline="black", width=2)
                draw.ellipse([s*0.2, s*0.2, s*0.4, s*0.4], fill="black")
                draw.ellipse([s*0.6, s*0.5, s*0.8, s*0.7], fill="black")
                
            elif "basquet" in nombre_archivo:
                # Naranja con lineas
                draw.ellipse([2, 2, s-2, s-2], fill="#FF9800", outline="black", width=2)
                draw.line([s/2, 2, s/2, s-2], fill="black", width=2) 
                draw.line([2, s/2, s-2, s/2], fill="black", width=2)
                
            elif "tenis" in nombre_archivo:
                # Verde limón
                draw.ellipse([2, 2, s-2, s-2], fill="#CCFF00", outline="black", width=2)
                draw.arc([s*0.1, s*0.1, s*0.9, s*0.9], 0, 360, fill="white", width=2)

            elif "voley" in nombre_archivo:
                # --- NUEVO DISEÑO VOLEY (Amarillo y Azul) ---
                # Base Amarilla
                draw.ellipse([2, 2, s-2, s-2], fill="#FFEB3B", outline="black", width=2)
                # Franjas Azules a los lados
                draw.chord([2, 2, s-2, s-2], 120, 240, fill="#0055A4", outline="black", width=2)
                draw.chord([2, 2, s-2, s-2], 300, 60, fill="#0055A4", outline="black", width=2)
            else:
                # Genérico
                draw.ellipse([2, 2, s-2, s-2], fill="red", outline="black", width=2)
            
            # Texto del valor (1, 10, 100, 1000)
            try:
                font = ImageFont.truetype("arial.ttf", int(s*0.3))
            except:
                font = ImageFont.load_default()
            
            # Sombra blanca para que se lea bien sobre cualquier color
            draw.text((s/2+1, s/2+1), texto_numero, fill="white", anchor="mm", font=font)
            draw.text((s/2, s/2), texto_numero, fill="black", anchor="mm", font=font)

            return ImageTk.PhotoImage(img)

    def volver_al_menu(self, event=None):
        path = os.path.join(SCRIPT_DIR, "..", "menu", "menumatematicas.py")
        path = os.path.normpath(path)
        
        if os.path.exists(path):
            self.master.destroy()
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, path], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, path])
        else:
            messagebox.showerror("Error", f"Menú no encontrado en:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathDragGameLevel3(root)
    root.mainloop()