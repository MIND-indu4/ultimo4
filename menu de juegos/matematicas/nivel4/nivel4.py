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

# --- CONFIGURACIÓN VISUAL (NIVEL 4) ---
class GameConfig:
    # Colores
    MAIN_COLOR = "#4CAF50"       # Verde Material Design
    HOVER_COLOR = "#66BB6A"
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    DIVIDER_COLOR = "#A5D6A7"    # Verde claro para líneas divisorias
    
    # Colores Ventana Victoria
    BTN_MENU_COLOR = "#5B84B1"
    BTN_NEXT_COLOR = "#4CAF50"

    # Orden: Mil, Centena, Decena, Unidad
    BALL_TYPES = ["futbol.png", "basquet.png", "tenis.png", "voley.jpg"]

# --- FUNCIONES AUXILIARES ---
class MathDragGameLevel4:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 4")
        
        # --- CONFIGURACIÓN PANTALLA (FIX RASPBERRY) ---
        master.update_idletasks() 
        
        if SYSTEM_OS == "Windows":
            master.attributes("-fullscreen", True)
        else:
            w = master.winfo_screenwidth()
            h = master.winfo_screenheight()
            master.geometry(f"{w}x{h}+0+0")
            master.after(100, lambda: master.attributes("-fullscreen", True))
        
        master.configure(bg=GameConfig.MAIN_COLOR)
        master.bind("<Escape>", self.volver_al_menu)

        # Escala dinámica
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1280
        base_height = 800
        self.scale = min(screen_width / base_width, screen_height / base_height)

        # Fuentes
        self.font_title = (SYSTEM_FONT, int(24 * self.scale), "bold")
        self.font_header = (SYSTEM_FONT, int(16 * self.scale), "bold")
        self.font_btn = (SYSTEM_FONT, int(14 * self.scale), "bold")
        self.font_win_title = (SYSTEM_FONT, int(40 * self.scale), "bold")
        
        # Tamaños
        self.ball_size = int(50 * self.scale) 
        self.box_size = int(90 * self.scale)  
        
        self.drag_data = {"item": None, "offset_x": 0, "offset_y": 0}
        
        # Variables de juego
        self.target_values = [] 
        self.slots_filled = [False, False, False, False]

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
        
        self.ancho_real_frame = cw - 40
        self.alto_real_frame = ch - 40

        # Fondo blanco redondeado simétrico
        self._draw_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR, outline="")

        # Frame contenido
        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=self.ancho_real_frame, height=self.alto_real_frame)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="⬅ Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", lambda e: self.volver_al_menu())

        # Título
        tk.Label(self.content_frame, text="Cuenta las pelotas y arrastra el número correcto", font=self.font_title, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).pack(pady=(10, 10))

        # --- ÁREA SUPERIOR: LOS 4 CASILLEROS ---
        self.frame_top_container = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_top_container.pack(pady=(10, 10))

        self.target_widgets = []
        for i in range(4):
            lbl = tk.Label(self.frame_top_container, bg=GameConfig.CARD_COLOR, bd=0)
            lbl.pack(side="left", padx=15)
            self.target_widgets.append(lbl)

        # --- ÁREA CENTRAL: COLUMNAS ---
        self.frame_columns = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_columns.pack(expand=True, fill="both", padx=40, pady=5)
        
        for i in range(7): 
            if i % 2 == 0: self.frame_columns.columnconfigure(i, weight=1)
            else: self.frame_columns.columnconfigure(i, weight=0)
        self.frame_columns.rowconfigure(1, weight=1)

        headers = ["Unidad de Mil", "Centena", "Decena", "Unidad"]
        self.column_areas = [] 

        for i, title in enumerate(headers):
            grid_col = i * 2
            
            tk.Label(self.frame_columns, text=title, font=self.font_header, 
                     bg=GameConfig.CARD_COLOR, fg="#555").grid(row=0, column=grid_col, pady=(0,5))
            
            ball_area = tk.Frame(self.frame_columns, bg="#F1F8E9") 
            ball_area.grid(row=1, column=grid_col, sticky="nsew", padx=5)
            self.column_areas.append(ball_area)

            if i < 3:
                sep_col = grid_col + 1
                separator = tk.Frame(self.frame_columns, bg=GameConfig.DIVIDER_COLOR, width=2)
                separator.grid(row=0, column=sep_col, rowspan=2, sticky="ns", padx=2)

    # --- DIBUJO SIMÉTRICO ---
    def _draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            (x1 + radius, y1), (x1 + radius, y1),
            (x2 - radius, y1), (x2 - radius, y1),
            (x2, y1),
            (x2, y1 + radius), (x2, y1 + radius),
            (x2, y2 - radius), (x2, y2 - radius),
            (x2, y2),
            (x2 - radius, y2), (x2 - radius, y2),
            (x1 + radius, y2), (x1 + radius, y2),
            (x1, y2),
            (x1, y2 - radius), (x1, y2 - radius),
            (x1, y1 + radius), (x1, y1 + radius),
            (x1, y1)
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _start_new_round(self):
        # Limpiar
        for area in self.column_areas:
            for widget in area.winfo_children(): widget.destroy()
        
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, "es_ficha_numero"): widget.destroy()

        self.img_slot_vacio = self.crear_imagen_slot_vacio()
        self.slots_filled = [False] * 4
        
        for slot in self.target_widgets:
            slot.config(image=self.img_slot_vacio)
            slot.image = self.img_slot_vacio
            slot.ocupado_por = None

        # Generar
        d1 = random.randint(1, 4)
        d2 = random.randint(1, 5)
        d3 = random.randint(1, 5)
        d4 = random.randint(1, 5)
        self.target_values = [d1, d2, d3, d4]
        
        # Dibujar pelotas
        for i, cantidad in enumerate(self.target_values):
            self.dibujar_pelotas_en_columna(i, cantidad)

        # Generar Fichas
        opciones = self.target_values.copy()
        while len(opciones) < 6: 
            n = random.randint(1, 9)
            opciones.append(n)
        
        random.shuffle(opciones)

        y_pos = self.alto_real_frame - int(140 * self.scale)
        zona_width = self.ancho_real_frame // 6
        
        for i, val in enumerate(opciones):
            img_num = self.crear_imagen_numero(val)
            
            lbl = tk.Label(self.content_frame, image=img_num, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_num 
            lbl.valor = val 
            lbl.es_ficha_numero = True
            
            x_pos = (i * zona_width) + (zona_width // 2) - (self.box_size // 2)
            
            lbl.place(x=x_pos, y=y_pos)
            lbl.home_x = x_pos
            lbl.home_y = y_pos
            lbl.bloqueado = False 

            lbl.bind("<Button-1>", self.start_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def dibujar_pelotas_en_columna(self, col_idx, cantidad):
        area = self.column_areas[col_idx]
        tipo_pelota = GameConfig.BALL_TYPES[col_idx]
        img_pelota = self.crear_imagen_pelota(tipo_pelota)
        
        inner = tk.Frame(area, bg=area.cget("bg"))
        inner.place(relx=0.5, rely=0.1, anchor="n")
        
        cols_visual = 2
        for i in range(cantidad):
            row = i // cols_visual
            col = i % cols_visual
            
            lbl = tk.Label(inner, image=img_pelota, bg=area.cget("bg"))
            lbl.image = img_pelota
            lbl.grid(row=row, column=col, padx=2, pady=5)

    # --- LÓGICA ARRASTRE ---
    def start_drag(self, event):
        widget = event.widget
        if widget.bloqueado: return
        widget.lift()
        self.drag_data["item"] = widget
        self.drag_data["offset_x"] = event.x
        self.drag_data["offset_y"] = event.y

    def do_drag(self, event):
        widget = self.drag_data["item"]
        if not widget: return
        
        x_root = event.x_root
        y_root = event.y_root
        frame_x = self.content_frame.winfo_rootx()
        frame_y = self.content_frame.winfo_rooty()
        
        new_x = x_root - frame_x - self.drag_data["offset_x"]
        new_y = y_root - frame_y - self.drag_data["offset_y"]
        
        widget.place(x=new_x, y=new_y)

    def end_drag(self, event):
        widget = self.drag_data["item"]
        self.drag_data["item"] = None
        if not widget: return

        drop_x = widget.winfo_rootx() + (widget.winfo_width() // 2)
        drop_y = widget.winfo_rooty() + (widget.winfo_height() // 2)

        encontrado = False
        
        for i, target in enumerate(self.target_widgets):
            if self.slots_filled[i]: continue 
            
            tx = target.winfo_rootx()
            ty = target.winfo_rooty()
            tw = target.winfo_width()
            th = target.winfo_height()
            
            if tx < drop_x < tx + tw and ty < drop_y < ty + th:
                if widget.valor == self.target_values[i]:
                    final_x = tx - self.content_frame.winfo_rootx()
                    final_y = ty - self.content_frame.winfo_rooty()
                    
                    ox = (tw - widget.winfo_width()) // 2
                    oy = (th - widget.winfo_height()) // 2
                    
                    widget.place(x=final_x + ox, y=final_y + oy)
                    widget.bloqueado = True
                    self.slots_filled[i] = True
                    encontrado = True
                    
                    if all(self.slots_filled):
                        self.master.after(300, self._show_win_screen)
                    break
        
        if not encontrado:
            widget.place(x=widget.home_x, y=widget.home_y)

    # =============================================================
    # PANTALLA DE FELICITACIÓN PERSONALIZADA (VERDE)
    # =============================================================
    def _show_win_screen(self):
        win = tk.Toplevel(self.master)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.grab_set()

        w, h = int(500 * self.scale), int(350 * self.scale)
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        
        border_color = GameConfig.MAIN_COLOR 
        win.configure(bg=border_color)

        canvas = tk.Canvas(win, width=w, height=h, bg=border_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        self._draw_rounded_rectangle(canvas, 10, 10, w-10, h-10, radius=20, fill="white", outline="white")
        
        tk.Label(win, text="¡Muy Bien!", font=self.font_win_title, bg="white", fg=GameConfig.MAIN_COLOR).place(relx=0.5, rely=0.25, anchor="center")
        
        sub_font = (SYSTEM_FONT, int(16 * self.scale))
        tk.Label(win, text="¡Has contado correctamente! 🔢", font=sub_font, bg="white", fg=GameConfig.TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
        btn_container = tk.Frame(win, bg="white")
        btn_container.place(relx=0.5, rely=0.75, anchor="center")
        
        def action(act):
            win.destroy()
            if act == "next": self._start_new_round()
            elif act == "menu": self.volver_al_menu()
            
        def on_enter_green(e): e.widget['bg'] = GameConfig.HOVER_COLOR
        def on_leave_green(e): e.widget['bg'] = GameConfig.BTN_NEXT_COLOR
        
        def on_enter_blue(e): e.widget['bg'] = '#7FA6D6'
        def on_leave_blue(e): e.widget['bg'] = GameConfig.BTN_MENU_COLOR

        btn_menu = tk.Button(btn_container, text="Menú 🏠", font=self.font_btn,
                             bg=GameConfig.BTN_MENU_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("menu"))
        btn_menu.pack(side=tk.LEFT, padx=15)
        btn_menu.bind("<Enter>", on_enter_blue)
        btn_menu.bind("<Leave>", on_leave_blue)

        btn_next = tk.Button(btn_container, text="Siguiente ➡", font=self.font_btn,
                             bg=GameConfig.BTN_NEXT_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("next"))
        btn_next.pack(side=tk.LEFT, padx=15)
        btn_next.bind("<Enter>", on_enter_green)
        btn_next.bind("<Leave>", on_leave_green)
    # =============================================================

    # --- GENERADORES GRÁFICOS (FONT FIX) ---
    def crear_imagen_numero(self, numero):
        s = self.box_size
        img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.MAIN_COLOR, width=3)
        
        font_name = "arial.ttf" if SYSTEM_OS == "Windows" else "DejaVuSans.ttf"
        try: 
            # TAMAÑO AUMENTADO A 0.85
            font = ImageFont.truetype(font_name, int(s*0.85))
        except: 
            # Fallback a cualquier fuente TrueType que encuentre si falla DejaVu
            try: font = ImageFont.truetype("FreeSans.ttf", int(s*0.85))
            except: font = ImageFont.load_default()

        text = str(numero)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            # Ajuste de centrado
            draw.text(((s-w)/2, (s-h)/2 - (s*0.1)), text, fill=GameConfig.MAIN_COLOR, font=font)
        except:
            draw.text((s//3, s//4), text, fill=GameConfig.MAIN_COLOR)

        return ImageTk.PhotoImage(img)

    def crear_imagen_slot_vacio(self):
        s = self.box_size
        img = Image.new("RGB", (s, s), "white") 
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline="#BDBDBD", width=2)
        try:
            f_name = "arial.ttf" if SYSTEM_OS == "Windows" else "DejaVuSans.ttf"
            f = ImageFont.truetype(f_name, int(s*0.5))
            
            text = "?"
            bbox = draw.textbbox((0, 0), text, font=f)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((s-w)/2, (s-h)/2 - (s*0.1)), text, fill="#E0E0E0", font=f)
        except: pass
        return ImageTk.PhotoImage(img)

    def crear_imagen_pelota(self, tipo):
        s = self.ball_size
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        item_img = None
        rutas = [tipo, os.path.join("..", "nivel3", tipo), os.path.join("assets", tipo)]
        
        for p in rutas:
            fp = os.path.join(SCRIPT_DIR, p)
            if os.path.exists(fp):
                try:
                    item_img = Image.open(fp).convert("RGBA")
                    break
                except: pass

        if item_img:
            img_res = item_img.resize((s, s), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_res)
        else:
            draw.ellipse([2, 2, s-2, s-2], outline="black", width=2)
            if "futbol" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="white", outline="black")
                draw.ellipse([s*0.4, s*0.4, s*0.6, s*0.6], fill="black") 
            elif "basquet" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FF9800", outline="black")
            elif "tenis" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#CCFF00", outline="black")
            elif "voley" in tipo:
                draw.ellipse([2, 2, s-2, s-2], fill="#FFEB3B", outline="black")
            
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
            messagebox.showerror("Error", f"No se encontró el menú en:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathDragGameLevel4(root)
    root.mainloop()
