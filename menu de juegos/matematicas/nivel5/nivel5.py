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

# --- CONFIGURACIÓN VISUAL (NIVEL 5) ---
class GameConfig:
    # Colores
    MAIN_COLOR = "#00C853"       # Verde vibrante
    HOVER_COLOR = "#66BB6A"
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    
    # Colores Ventana Victoria
    BTN_MENU_COLOR = "#5B84B1"
    BTN_NEXT_COLOR = "#00C853"
    
    # Imágenes (Verduras y Frutas)
    IMAGENES = [
        "manzana.png", "pera.png", "banana.png", 
        "frutilla.png", "naranja.png", "limon.png",
        "piña.png", "sandia.png",
        "papa.png", "zanahoria.png", "brocoli.png", 
        "cebolla.png", "tomate.png", "lechuga.png",    
        "pepino.png", "calabaza.png"
    ]

# --- FUNCIONES AUXILIARES ---
class MathDragGameLevel5:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 5: Completar Suma")
        
        # --- CONFIGURACIÓN PANTALLA ---
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
        self.font_title = (SYSTEM_FONT, int(32 * self.scale), "bold")
        self.font_signos = (SYSTEM_FONT, int(60 * self.scale), "bold") 
        self.font_btn = (SYSTEM_FONT, int(14 * self.scale), "bold")
        self.font_win_title = (SYSTEM_FONT, int(40 * self.scale), "bold")
        
        # Tamaño de las cajas
        self.box_size = int(140 * self.scale) 
        
        self.drag_data = {"item": None, "offset_x": 0, "offset_y": 0}

        self._create_gui()
        self._start_new_round()

    def _create_gui(self):
        self.main_canvas = tk.Canvas(self.master, bg=GameConfig.MAIN_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        
        cw = int(sw * 0.85)
        ch = int(sh * 0.85)
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
        tk.Label(self.content_frame, text="¡COMPLÉTALO!", font=self.font_title, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.MAIN_COLOR).pack(pady=(20, 40))

        # --- ÁREA DE ECUACIÓN (Arriba) ---
        self.frame_ecuacion = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_ecuacion.pack(pady=20)

        # 1. Parte Conocida
        self.lbl_parte1 = tk.Label(self.frame_ecuacion, bg="white", bd=2, relief="solid")
        self.lbl_parte1.grid(row=0, column=0, padx=20)
        
        # Signo +
        tk.Label(self.frame_ecuacion, text="+", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg="black").grid(row=0, column=1)
        
        # 2. TARGET (La incógnita)
        self.lbl_target = tk.Label(self.frame_ecuacion, bg="#EEEEEE", bd=2, relief="solid")
        self.lbl_target.grid(row=0, column=2, padx=20)
        
        # Signo =
        tk.Label(self.frame_ecuacion, text="=", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg="black").grid(row=0, column=3)
        
        # 3. Resultado Total
        self.lbl_total = tk.Label(self.frame_ecuacion, bg="white", bd=2, relief="solid")
        self.lbl_total.grid(row=0, column=4, padx=20)

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
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, "es_opcion_juego"): widget.destroy()

        # Reiniciar Target
        self.img_slot_vacio = self.crear_imagen_slot_vacio()
        self.lbl_target.config(image=self.img_slot_vacio)
        self.lbl_target.image = self.img_slot_vacio
        self.lbl_target.ocupado = False

        # 1. Lógica Matemática
        self.item_type = random.choice(GameConfig.IMAGENES)
        
        self.total_num = random.randint(2, 9)
        self.num1 = random.randint(1, self.total_num - 1)
        self.missing_num = self.total_num - self.num1

        # 2. Actualizar Pantalla
        img1 = self.crear_imagen_verdura(self.item_type, self.num1)
        self.lbl_parte1.config(image=img1)
        self.lbl_parte1.image = img1

        img_total = self.crear_imagen_verdura(self.item_type, self.total_num)
        self.lbl_total.config(image=img_total)
        self.lbl_total.image = img_total

        # 3. Generar Opciones
        opciones = []
        opciones.append({"cant": self.missing_num, "tipo": self.item_type, "correcta": True})
        
        while len(opciones) < 5:
            es_tipo_correcto = random.choice([True, False])
            
            if es_tipo_correcto:
                cant = random.randint(1, 9)
                tipo = self.item_type
            else:
                cant = random.randint(1, 9)
                tipo = random.choice(GameConfig.IMAGENES)
                if tipo == self.item_type: tipo = "banana.png"
            
            if cant == self.missing_num and tipo == self.item_type:
                continue
                
            opciones.append({"cant": cant, "tipo": tipo, "correcta": False})
        
        random.shuffle(opciones)

        # 4. Dibujar Fichas
        y_pos = self.alto_real_frame - int(180 * self.scale)
        zona_width = self.ancho_real_frame // 5
        
        for i, op in enumerate(opciones):
            img_op = self.crear_imagen_verdura(op["tipo"], op["cant"], es_opcion=True)
            
            lbl = tk.Label(self.content_frame, image=img_op, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_op 
            lbl.es_correcta = op["correcta"]
            lbl.es_opcion_juego = True
            
            x_pos = (i * zona_width) + (zona_width // 2) - (self.box_size // 2)
            
            lbl.place(x=x_pos, y=y_pos)
            lbl.home_x = x_pos
            lbl.home_y = y_pos
            lbl.bloqueado = False 

            lbl.bind("<Button-1>", self.start_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

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

        target = self.lbl_target
        tx1 = target.winfo_rootx()
        ty1 = target.winfo_rooty()
        tx2 = tx1 + target.winfo_width()
        ty2 = ty1 + target.winfo_height()

        if tx1 < drop_x < tx2 and ty1 < drop_y < ty2:
            if widget.es_correcta:
                final_x = tx1 - self.content_frame.winfo_rootx() + (target.winfo_width() - widget.winfo_width()) // 2
                final_y = ty1 - self.content_frame.winfo_rooty() + (target.winfo_height() - widget.winfo_height()) // 2
                
                widget.place(x=final_x, y=final_y)
                widget.bloqueado = True
                
                self.master.after(300, self._show_win_screen)
            else:
                self.return_to_home(widget)
        else:
            self.return_to_home(widget)

    def return_to_home(self, widget):
        widget.place(x=widget.home_x, y=widget.home_y)

    # =============================================================
    # PANTALLA DE FELICITACIÓN MEJORADA (VERDE)
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
        tk.Label(win, text="¡Completaste la operación! ➕", font=sub_font, bg="white", fg=GameConfig.TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
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

    # --- GENERADORES ---
    def crear_imagen_verdura(self, nombre_archivo, cantidad, es_opcion=False):
        s = self.box_size
        canvas_img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(canvas_img)
        
        color_borde = GameConfig.MAIN_COLOR if es_opcion else GameConfig.TEXT_DARK
        w_borde = 3 if es_opcion else 2
        draw.rectangle([0, 0, s-1, s-1], outline=color_borde, width=w_borde)

        item_img = None
        base = os.path.splitext(nombre_archivo)[0]
        exts = [".png", ".jpg", ".jpeg"]
        rutas = []
        for ext in exts:
            f = base + ext
            rutas.append(f)
            rutas.append(os.path.join("imagenes", f))
            rutas.append(os.path.join("assets", f))
            rutas.append(os.path.join("..", "nivel1", f)) 
            rutas.append(os.path.join("..", "nivel2", f))

        for r in rutas:
            if os.path.exists(os.path.join(SCRIPT_DIR, r)):
                try:
                    item_img = Image.open(os.path.join(SCRIPT_DIR, r)).convert("RGBA")
                    break
                except: pass

        if cantidad <= 4:
            cols = 2; rows = 2
        else:
            cols = 3; rows = 3
        
        cell_w = s // cols
        cell_h = s // rows 

        for i in range(cantidad):
            r = i // cols
            c = i % cols
            pad = 5
            x = c * cell_w + pad
            y = r * cell_h + pad
            tw = cell_w - (pad*2)
            th = cell_h - (pad*2)

            if item_img:
                aspect = item_img.width / item_img.height
                if tw / th > aspect:
                    new_h = th
                    new_w = int(th * aspect)
                else:
                    new_w = tw
                    new_h = int(tw / aspect)
                
                img_res = item_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                off_x = (tw - new_w)//2
                off_y = (th - new_h)//2
                canvas_img.paste(img_res, (x+off_x, y+off_y), img_res)
            else:
                diam = min(tw, th)
                off_x = (tw - diam) // 2
                off_y = (th - diam) // 2
                draw.ellipse([x+off_x, y+off_y, x+off_x+diam, y+off_y+diam], 
                             fill=GameConfig.MAIN_COLOR, outline="black")

        return ImageTk.PhotoImage(canvas_img)

    def crear_imagen_slot_vacio(self):
        s = self.box_size
        img = Image.new("RGB", (s, s), "white") 
        return ImageTk.PhotoImage(img)

    def volver_al_menu(self, event=None):
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_menu = os.path.join(ruta_actual, "..", "menu", "menumatematicas.py")
        ruta_menu = os.path.normpath(ruta_menu)
        
        if os.path.exists(ruta_menu):
            self.master.destroy()
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, ruta_menu], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, ruta_menu])
        else:
            messagebox.showerror("Error", f"No se encontró el menú en:\n{ruta_menu}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathDragGameLevel5(root)
    root.mainloop()
