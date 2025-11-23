import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess

# --- CONFIGURACIÓN ---
class GameConfig:
    # COLOR VERDE (Igual a Nivel 1 y 2)
    MAIN_COLOR = "#4CAF50"       
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    DIVIDER_COLOR = "#4CAF50"    # Las líneas serán del mismo verde
    
    # Tipos de pelota (El script buscará archivos que contengan estos nombres)
    # Orden: Unidad de Mil, Centena, Decena, Unidad
    BALL_TYPES = ["futbol", "basquet", "tenis", "voley"]

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
        master.attributes("-fullscreen", True)
        master.configure(bg=GameConfig.MAIN_COLOR)

        # Escala dinámica
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1280
        base_height = 800
        self.scale = min(screen_width / base_width, screen_height / base_height)

        # Fuentes
        self.font_title = ("Arial", int(24 * self.scale), "bold")
        self.font_header = ("Arial", int(18 * self.scale), "bold") # Negrita para encabezados
        self.font_number = ("Arial", int(50 * self.scale), "bold") # Número más grande
        self.font_btn = ("Arial", int(14 * self.scale), "bold")
        
        # Tamaño de las pelotas
        self.ball_size = int(80 * self.scale) 
        
        self.drag_data = {"item": None, "type_index": None}
        self.columns_content = [[], [], [], []] 

        self._create_gui()
        self._start_new_round()

    def _create_gui(self):
        # Canvas Principal
        self.main_canvas = tk.Canvas(self.master, bg=GameConfig.MAIN_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        # Dimensiones tarjeta
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        cw = int(sw * 0.85)
        ch = int(sh * 0.85)
        cx = sw // 2
        cy = sh // 2
        
        create_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR)

        # Frame Principal
        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=cw-40, height=ch-40)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", self.volver_al_menu)

        # --- ÁREA SUPERIOR: NÚMERO OBJETIVO ---
        self.frame_top = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_top.pack(pady=(30, 20))

        # Caja del número con borde verde grueso
        self.lbl_number_display = tk.Label(self.frame_top, text="0000", font=self.font_number, 
                                           fg=GameConfig.MAIN_COLOR, bg="white",
                                           bd=4, relief="solid", padx=40, pady=10)
        self.lbl_number_display.pack()

        # --- ÁREA CENTRAL: COLUMNAS Y DIVISIONES ---
        self.frame_columns = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_columns.pack(expand=True, fill="both", padx=40, pady=10)
        
        # Configuración de la grilla para divisiones claras
        # Columnas: 0(Dato), 1(Linea), 2(Dato), 3(Linea), 4(Dato), 5(Linea), 6(Dato)
        for i in range(7):
            if i % 2 == 0: # Columnas de datos
                self.frame_columns.columnconfigure(i, weight=1)
            else: # Columnas de separadores
                self.frame_columns.columnconfigure(i, weight=0) # Ancho fijo
        
        self.frame_columns.rowconfigure(1, weight=1) # La fila del contenido se estira

        headers = ["Unidad de mil", "Centena", "Decena", "Unidad"]
        self.column_frames = [] 

        for i, title in enumerate(headers):
            grid_col = i * 2 # 0, 2, 4, 6
            
            # 1. Título
            tk.Label(self.frame_columns, text=title, font=self.font_header, 
                     bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=grid_col, pady=(0,10))
            
            # 2. Área de caída (Frame invisible que se estira)
            drop_area = tk.Frame(self.frame_columns, bg=GameConfig.CARD_COLOR) 
            drop_area.grid(row=1, column=grid_col, sticky="nsew", padx=5)
            self.column_frames.append(drop_area)

            # 3. Línea divisoria (si no es el último)
            if i < 3:
                sep_col = grid_col + 1
                separator = tk.Frame(self.frame_columns, bg=GameConfig.DIVIDER_COLOR, width=4)
                separator.grid(row=0, column=sep_col, rowspan=2, sticky="ns", padx=5)

        # --- ÁREA INFERIOR: FUENTE DE PELOTAS ---
        self.frame_source = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_source.pack(pady=30, fill="x")

        # Crear las 4 pelotas de origen
        self.source_images = []
        for i, btype in enumerate(GameConfig.BALL_TYPES):
            img = self.crear_imagen_pelota(btype)
            self.source_images.append(img)
            
            # Contenedor para centrar
            container = tk.Frame(self.frame_source, bg=GameConfig.CARD_COLOR)
            container.pack(side="left", expand=True)
            
            lbl = tk.Label(container, image=img, bg=GameConfig.CARD_COLOR, cursor="hand2")
            lbl.pack()
            
            lbl.bind("<Button-1>", lambda e, idx=i: self.start_spawn_drag(e, idx))
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def _start_new_round(self):
        # Limpiar
        for col_list in self.columns_content:
            for widget in col_list:
                widget.destroy()
            col_list.clear()

        # Generar número (evitamos ceros para que sea jugable)
        d1 = random.randint(1, 4) 
        d2 = random.randint(1, 5) 
        d3 = random.randint(1, 5) 
        d4 = random.randint(1, 5) 
        
        self.target_number_str = f"{d1}{d2}{d3}{d4}"
        self.lbl_number_display.config(text=self.target_number_str)
        self.targets = [d1, d2, d3, d4]

    # --- LÓGICA ARRASTRE ---
    def start_spawn_drag(self, event, type_index):
        img = self.source_images[type_index]
        drag_lbl = tk.Label(self.content_frame, image=img, bg=GameConfig.CARD_COLOR, bd=0)
        drag_lbl.image = img 
        
        start_x = event.widget.winfo_rootx() - self.content_frame.winfo_rootx()
        start_y = event.widget.winfo_rooty() - self.content_frame.winfo_rooty()
        
        drag_lbl.place(x=start_x, y=start_y)
        drag_lbl.lift()
        
        self.drag_data["item"] = drag_lbl
        self.drag_data["type_index"] = type_index

    def do_drag(self, event):
        widget = self.drag_data["item"]
        if not widget: return
        
        mx = self.master.winfo_pointerx() - self.content_frame.winfo_rootx()
        my = self.master.winfo_pointery() - self.content_frame.winfo_rooty()
        
        x = mx - (self.ball_size // 2)
        y = my - (self.ball_size // 2)
        widget.place(x=x, y=y)

    def end_drag(self, event):
        widget = self.drag_data["item"]
        idx = self.drag_data["type_index"]
        self.drag_data["item"] = None
        
        if not widget: return

        drop_x = self.master.winfo_pointerx()
        drop_y = self.master.winfo_pointery()
        
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
        
        lbl = tk.Label(frame, image=img, bg=GameConfig.CARD_COLOR)
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
        w = self.ball_size
        h = self.ball_size
        frame_w = frame.winfo_width()
        start_x = (frame_w - (cols_visual * w)) // 2
        if start_x < 0: start_x = 0
        
        for i, widget in enumerate(items):
            row = i // cols_visual
            col = i % cols_visual
            px = start_x + (col * w) + 5
            py = (row * h) + 5
            widget.place(x=px, y=py)

    def check_win(self):
        current_counts = [len(col) for col in self.columns_content]
        if current_counts == self.targets:
            self.master.after(200, self.game_win)

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
        tk.Label(win, text="¡Formaste el número correcto!", font=("Arial", 14), bg="white", fg="#555").pack(pady=10)
        
        btn = tk.Label(win, text="Siguiente Ejercicio", font=("Arial", 14, "bold"),
                       bg=GameConfig.MAIN_COLOR, fg="white", padx=20, pady=10, cursor="hand2")
        btn.pack(pady=20)
        
        def reiniciar(e):
            win.destroy()
            self._start_new_round()
            
        btn.bind("<Button-1>", reiniciar)

    # --- CARGA INTELIGENTE DE IMÁGENES ---
    def crear_imagen_pelota(self, tipo):
        s = self.ball_size
        # Fondo transparente para que no se vea cuadrado blanco
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Buscar imagen (Buscamos .png, .jpg y en carpetas vecinas)
        item_img = None
        posibles_nombres = [f"{tipo}.png", f"balon_{tipo}.png", f"{tipo}.jpg"]
        
        rutas_a_probar = []
        for nombre in posibles_nombres:
            rutas_a_probar.append(nombre)
            rutas_a_probar.append(os.path.join("imagenes", nombre))
            rutas_a_probar.append(os.path.join("assets", nombre))
            rutas_a_probar.append(os.path.join("..", "nivel1", nombre)) # Busca en Nivel 1
            rutas_a_probar.append(os.path.join("..", "nivel2", nombre)) # Busca en Nivel 2

        for r in rutas_a_probar:
            if os.path.exists(r):
                try:
                    item_img = Image.open(r).convert("RGBA")
                    break
                except: pass

        if item_img:
            # Si hay imagen, la redimensionamos
            img_res = item_img.resize((s, s), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_res)
        else:
            # SI FALLA: Dibujamos la pelota con PIL (Fallback bonito)
            # Contorno Negro
            draw.ellipse([2, 2, s-2, s-2], outline="black", width=2)
            
            if "futbol" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="white", outline="black", width=2)
                cx, cy = s/2, s/2
                r = s/6
                draw.regular_polygon((cx, cy, r), 6, rotation=0, fill="black")
                draw.ellipse([s*0.1, s*0.1, s*0.3, s*0.3], fill="black")
                draw.ellipse([s*0.7, s*0.1, s*0.9, s*0.3], fill="black")
                
            elif "basquet" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FF8C00", outline="black", width=2)
                draw.line([s/2, 2, s/2, s-2], fill="black", width=2) 
                draw.line([2, s/2, s-2, s/2], fill="black", width=2)
                
            elif "tenis" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#CCFF00", outline="black", width=2)
                draw.arc([s*0.2, -s*0.2, s*1.2, s*0.8], 140, 240, fill="white", width=3)
                draw.arc([-s*0.2, s*0.2, s*0.8, s*1.2], -40, 60, fill="white", width=3)

            elif "voley" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FFD700", outline="black", width=2)
                draw.chord([2, 2, s-2, s-2], 30, 150, fill="#0055A4", outline="black")
                draw.chord([2, 2, s-2, s-2], 210, 330, fill="#0055A4", outline="black")

            return ImageTk.PhotoImage(img)

    def volver_al_menu(self, event=None):
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_menu = os.path.join(ruta_actual, "..", "menu", "menumatematicas.py")
        
        if os.path.exists(ruta_menu):
            self.master.destroy()
            subprocess.Popen([sys.executable, ruta_menu])
        else:
            messagebox.showerror("Error", f"No se encontró el archivo del menú en:\n{ruta_menu}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathDragGameLevel3(root)
    root.mainloop()