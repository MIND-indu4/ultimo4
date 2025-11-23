import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess

# --- CONFIGURACIÓN ---
class GameConfig:
    # VOLVEMOS AL VERDE
    MAIN_COLOR = "#4CAF50"       
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    DIVIDER_COLOR = "#4CAF50"
    
    # Tipos de pelota
    BALL_TYPES = ["futbol", "basquet", "tenis", "voley"]

# --- FUNCIONES AUXILIARES ---
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
              x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class MathDragGameLevel4:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 4")
        master.attributes("-fullscreen", True)
        master.configure(bg=GameConfig.MAIN_COLOR)

        # Escala dinámica
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1280
        base_height = 800
        self.scale = min(screen_width / base_width, screen_height / base_height)

        # Fuentes
        self.font_header = ("Arial", int(18 * self.scale), "bold")
        self.font_btn = ("Arial", int(14 * self.scale), "bold")
        
        # Tamaños
        self.ball_size = int(70 * self.scale) 
        self.box_size = int(110 * self.scale) # Tamaño de las fichas de números
        
        self.drag_data = {"item": None}
        
        # Variables de juego
        self.target_values = [] 
        self.slots_filled = [False, False, False, False]

        self._create_gui()
        self._start_new_round()

    def _create_gui(self):
        # Canvas Principal
        self.main_canvas = tk.Canvas(self.master, bg=GameConfig.MAIN_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        cw = int(sw * 0.85)
        ch = int(sh * 0.85)
        cx = sw // 2
        cy = sh // 2
        
        self.ancho_real_frame = cw - 40

        # Tarjeta Blanca
        create_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR)

        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=self.ancho_real_frame, height=ch-40)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", self.volver_al_menu)

        # --- ÁREA SUPERIOR: LOS 4 CASILLEROS PARA RESPONDER ---
        self.frame_top_container = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_top_container.pack(pady=(20, 10))

        # Creamos 4 Labels que serán los "Slots" vacíos
        self.target_widgets = []
        for i in range(4):
            # Inicializamos sin imagen, se carga en start_new_round
            lbl = tk.Label(self.frame_top_container, bg=GameConfig.CARD_COLOR, bd=0)
            lbl.pack(side="left", padx=10)
            self.target_widgets.append(lbl)

        # --- ÁREA CENTRAL: COLUMNAS ---
        self.frame_columns = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_columns.pack(expand=True, fill="both", padx=40, pady=10)
        
        for i in range(7): # 4 datos + 3 separadores
            if i % 2 == 0: self.frame_columns.columnconfigure(i, weight=1)
            else: self.frame_columns.columnconfigure(i, weight=0)
        self.frame_columns.rowconfigure(1, weight=1)

        headers = ["Unidad de mil", "Centena", "Decena", "Unidad"]
        self.column_areas = [] 

        for i, title in enumerate(headers):
            grid_col = i * 2
            
            # Título
            tk.Label(self.frame_columns, text=title, font=self.font_header, 
                     bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=grid_col, pady=(0,10))
            
            # Área de pelotas (Frame donde dibujaremos las bolas estáticas)
            ball_area = tk.Frame(self.frame_columns, bg=GameConfig.CARD_COLOR) 
            ball_area.grid(row=1, column=grid_col, sticky="nsew", padx=5)
            self.column_areas.append(ball_area)

            # Divisor (Línea Verde)
            if i < 3:
                sep_col = grid_col + 1
                separator = tk.Frame(self.frame_columns, bg=GameConfig.DIVIDER_COLOR, width=3)
                separator.grid(row=0, column=sep_col, rowspan=2, sticky="ns", padx=5)

    def _start_new_round(self):
        # 1. Limpiar área de pelotas (centro)
        for area in self.column_areas:
            for widget in area.winfo_children():
                widget.destroy()
        
        # 2. Limpiar fichas de números (abajo)
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, "es_ficha_numero"):
                widget.destroy()

        # 3. Reiniciar Slots de arriba (Ponerlos como cajas vacías)
        self.img_slot_vacio = self.crear_imagen_slot_vacio() # Crear imagen de caja vacía
        self.slots_filled = [False] * 4
        
        for slot in self.target_widgets:
            slot.config(image=self.img_slot_vacio)
            slot.image = self.img_slot_vacio # Referencia para evitar basura
            slot.ocupado_por = None

        # 4. Generar número aleatorio
        d1 = random.randint(1, 4)
        d2 = random.randint(1, 5)
        d3 = random.randint(1, 5)
        d4 = random.randint(1, 5)
        self.target_values = [d1, d2, d3, d4]
        
        # 5. DIBUJAR PELOTAS ESTÁTICAS
        for i, cantidad in enumerate(self.target_values):
            self.dibujar_pelotas_en_columna(i, cantidad)

        # 6. Generar Opciones (Fichas de números abajo)
        opciones = self.target_values.copy()
        while len(opciones) < 6: 
            n = random.randint(0, 9)
            opciones.append(n)
        random.shuffle(opciones)

        # 7. Dibujar fichas abajo
        frame_w = self.ancho_real_frame
        y_pos = self.content_frame.winfo_height() - int(150 * self.scale)
        if y_pos < 0: y_pos = int(self.master.winfo_screenheight() * 0.85) - int(160 * self.scale)
        
        zona_width = int(frame_w / 6)
        
        for i, val in enumerate(opciones):
            img_num = self.crear_imagen_numero(val)
            
            lbl = tk.Label(self.content_frame, image=img_num, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_num 
            lbl.valor = val 
            lbl.es_ficha_numero = True
            
            # Centrar en su zona
            x_pos = (i * zona_width) + (zona_width // 2) - (self.box_size // 2)
            
            lbl.place(x=x_pos, y=y_pos)
            lbl.home_x = x_pos
            lbl.home_y = y_pos
            lbl.bloqueado = False 

            lbl.bind("<Button-1>", self.start_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def dibujar_pelotas_en_columna(self, col_idx, cantidad):
        """Dibuja las pelotas quietas en la columna"""
        area = self.column_areas[col_idx]
        tipo_pelota = GameConfig.BALL_TYPES[col_idx]
        img_pelota = self.crear_imagen_pelota(tipo_pelota)
        
        # Frame interno para centrar el grupo de pelotas
        inner_frame = tk.Frame(area, bg=GameConfig.CARD_COLOR)
        inner_frame.place(relx=0.5, rely=0.1, anchor="n")
        
        cols_visual = 2
        for i in range(cantidad):
            row = i // cols_visual
            col = i % cols_visual
            
            lbl = tk.Label(inner_frame, image=img_pelota, bg=GameConfig.CARD_COLOR)
            lbl.image = img_pelota
            lbl.grid(row=row, column=col, padx=2, pady=2)

    # --- LÓGICA ARRASTRE ---
    def start_drag(self, event):
        widget = event.widget
        if widget.bloqueado: return
        widget.lift()
        self.drag_data["item"] = widget

    def do_drag(self, event):
        widget = self.drag_data["item"]
        if not widget: return
        
        mx = self.content_frame.winfo_pointerx() - self.content_frame.winfo_rootx()
        my = self.content_frame.winfo_pointery() - self.content_frame.winfo_rooty()
        
        # Centrar en el mouse
        widget.place(x=mx - (widget.winfo_width()//2), y=my - (widget.winfo_height()//2))

    def end_drag(self, event):
        widget = self.drag_data["item"]
        self.drag_data["item"] = None
        if not widget: return

        drop_x = widget.winfo_rootx() + (widget.winfo_width() // 2)
        drop_y = widget.winfo_rooty() + (widget.winfo_height() // 2)

        encontrado = False
        # Verificar colisión con los 4 slots de arriba
        for i, target in enumerate(self.target_widgets):
            if self.slots_filled[i]: continue
            
            tx1 = target.winfo_rootx()
            ty1 = target.winfo_rooty()
            tx2 = tx1 + target.winfo_width()
            ty2 = ty1 + target.winfo_height()
            
            if tx1 < drop_x < tx2 and ty1 < drop_y < ty2:
                if widget.valor == self.target_values[i]:
                    # Correcto
                    final_x = tx1 - self.content_frame.winfo_rootx()
                    final_y = ty1 - self.content_frame.winfo_rooty()
                    
                    # Ajuste fino para centrar
                    ox = (target.winfo_width() - widget.winfo_width()) // 2
                    oy = (target.winfo_height() - widget.winfo_height()) // 2
                    
                    widget.place(x=final_x + ox, y=final_y + oy)
                    widget.bloqueado = True
                    self.slots_filled[i] = True
                    encontrado = True
                    
                    if all(self.slots_filled):
                        self.master.after(300, self.game_win)
                    break
        
        if not encontrado:
            widget.place(x=widget.home_x, y=widget.home_y)

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
        tk.Label(win, text="¡Correcto!", font=("Arial", 26, "bold"), bg="white", fg=GameConfig.MAIN_COLOR).pack(pady=(30, 10))
        tk.Label(win, text="¡Contaste muy bien! 🧠", font=("Arial", 14), bg="white", fg="#555").pack(pady=10)
        
        btn = tk.Label(win, text="Siguiente Ejercicio", font=("Arial", 14, "bold"),
                       bg=GameConfig.MAIN_COLOR, fg="white", padx=20, pady=10, cursor="hand2")
        btn.pack(pady=20)
        btn.bind("<Button-1>", lambda e: [win.destroy(), self._start_new_round()])

    # --- GENERADORES DE IMÁGENES ---
    def crear_imagen_numero(self, numero):
        """Crea la ficha cuadrada con el número"""
        s = self.box_size
        img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.MAIN_COLOR, width=3)
        
        try: font = ImageFont.truetype("arial.ttf", int(s*0.6))
        except: font = ImageFont.load_default()

        text = str(numero)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((s-w)/2, (s-h)/2 - 5), text, fill=GameConfig.MAIN_COLOR, font=font)
        except:
            draw.text((s//3, s//4), text, fill=GameConfig.MAIN_COLOR)

        return ImageTk.PhotoImage(img)

    def crear_imagen_slot_vacio(self):
        """Crea el cuadrado vacío de arriba donde se suelta la ficha"""
        s = self.box_size
        img = Image.new("RGB", (s, s), "white") 
        draw = ImageDraw.Draw(img)
        # Borde verde para indicar que ahí va una ficha
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.MAIN_COLOR, width=2)
        return ImageTk.PhotoImage(img)

    def crear_imagen_pelota(self, tipo):
        s = self.ball_size
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Búsqueda de archivos
        item_img = None
        posibles = [f"{tipo}.png", f"balon_{tipo}.png", f"{tipo}.jpg"]
        rutas = []
        for p in posibles:
            rutas.append(p)
            rutas.append(os.path.join("imagenes", p))
            rutas.append(os.path.join("assets", p))
            rutas.append(os.path.join("..", "nivel3", p)) # Buscar en Nivel 3
            rutas.append(os.path.join("..", "nivel2", p))
        
        for r in rutas:
            if os.path.exists(r):
                try:
                    item_img = Image.open(r).convert("RGBA")
                    break
                except: pass

        if item_img:
            img_res = item_img.resize((s, s), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_res)
        else:
            # Fallback Dibujo (Por si no encuentra las imagenes)
            draw.ellipse([2, 2, s-2, s-2], outline="black", width=2)
            if "futbol" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="white", outline="black")
                draw.regular_polygon((s/2, s/2, s/6), 6, rotation=0, fill="black")
            elif "basquet" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FF8C00", outline="black")
                draw.line([s/2, 2, s/2, s-2], fill="black", width=2)
            elif "tenis" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#CCFF00", outline="black")
                draw.arc([s*0.2, -s*0.2, s*1.2, s*0.8], 140, 240, fill="white", width=2)
            elif "voley" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FFD700", outline="black")
                draw.chord([2, 2, s-2, s-2], 30, 150, fill="#0055A4", outline="black")
            
            return ImageTk.PhotoImage(img)

    def volver_al_menu(self, event=None):
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_menu = os.path.join(ruta_actual, "..", "menu", "menumatematicas.py")
        if os.path.exists(ruta_menu):
            self.master.destroy()
            subprocess.Popen([sys.executable, ruta_menu])
        else:
            messagebox.showerror("Error", f"No se encontró el menú: {ruta_menu}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathDragGameLevel4(root)
    root.mainloop()