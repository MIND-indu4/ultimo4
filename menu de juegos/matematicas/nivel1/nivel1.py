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
    # COLORES DEL JUEGO (VERDE)
    MAIN_COLOR = "#00C853"       # Verde principal
    HOVER_COLOR = "#00E676"      # Verde más claro para hover
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    
    # Colores para la ventana de victoria
    BTN_MENU_COLOR = "#5B84B1"   # Azul grisáceo (para diferenciar)
    BTN_NEXT_COLOR = "#00C853"   # Verde del juego
    
    IMAGENES = [
        "manzana.png", "pera.png", "banana.png", 
        "frutilla.png", "naranja.png", "limon.png",
        "piña.png", "sandia.png"
    ]

class MathDragGame:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 1")
        
        # --- CONFIGURACIÓN DE PANTALLA ---
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

        # Fuentes y Tamaños
        self.font_title = (SYSTEM_FONT, int(32 * self.scale), "bold")
        self.font_signos = (SYSTEM_FONT, int(50 * self.scale), "bold")
        self.font_btn = (SYSTEM_FONT, int(14 * self.scale), "bold")
        self.font_win_title = (SYSTEM_FONT, int(40 * self.scale), "bold") # Fuente Titulo Ventana
        
        self.box_size = int(130 * self.scale)
        
        self.drag_data = {"item": None}

        self._create_gui()
        self._start_new_round()

    def _create_gui(self):
        # Canvas Principal
        self.main_canvas = tk.Canvas(self.master, bg=GameConfig.MAIN_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        # Dimensiones tarjeta blanca
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        
        cw = int(sw * 0.85)
        ch = int(sh * 0.85)
        cx = sw // 2
        cy = sh // 2
        
        self.ancho_real_frame = cw - 40 

        # Dibujar fondo blanco redondeado con la función simétrica
        self._draw_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR, outline="")

        # Frame principal SOBRE la tarjeta
        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=self.ancho_real_frame, height=ch-40)

        # Botón Menú (Arriba a la izquierda)
        self.btn_menu = tk.Label(self.content_frame, text="⬅ Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", lambda e: self.volver_al_menu())
        
        # Título
        tk.Label(self.content_frame, text="Arrastra la respuesta correcta", font=self.font_title, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).pack(pady=(20, 40))

        # --- ÁREA DE ECUACIÓN ---
        self.frame_ecuacion = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_ecuacion.pack(pady=20)

        # Caja 1
        self.lbl_caja1 = tk.Label(self.frame_ecuacion, bg="white", bd=2, relief="solid")
        self.lbl_caja1.grid(row=0, column=0, padx=15)

        # Signo +
        tk.Label(self.frame_ecuacion, text="+", font=self.font_signos, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=1, padx=5)

        # Caja 2
        self.lbl_caja2 = tk.Label(self.frame_ecuacion, bg="white", bd=2, relief="solid")
        self.lbl_caja2.grid(row=0, column=2, padx=15)

        # Signo =
        tk.Label(self.frame_ecuacion, text="=", font=self.font_signos, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=3, padx=5)

        # TARGET (Signo de Interrogación)
        self.lbl_target = tk.Label(self.frame_ecuacion, bg="#EEEEEE", bd=2, relief="solid")
        self.lbl_target.grid(row=0, column=4, padx=15)

    # --- FUNCIÓN DE DIBUJO SIMÉTRICA (LA QUE TE GUSTÓ) ---
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
        # Limpiar fichas anteriores
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, "es_opcion_juego"):
                widget.destroy()

        # 1. Lógica
        self.img_actual_name = random.choice(GameConfig.IMAGENES)
        self.num1 = random.randint(1, 3)
        self.num2 = random.randint(1, 3)
        self.resultado = self.num1 + self.num2

        # 2. Actualizar Ecuación
        img1 = self.crear_imagen_compuesta(self.img_actual_name, self.num1)
        self.lbl_caja1.config(image=img1)
        self.lbl_caja1.image = img1

        img2 = self.crear_imagen_compuesta(self.img_actual_name, self.num2)
        self.lbl_caja2.config(image=img2)
        self.lbl_caja2.image = img2

        img_q = self.crear_imagen_interrogacion()
        self.lbl_target.config(image=img_q)
        self.lbl_target.image = img_q

        # 3. Generar 4 Opciones
        opciones = [{"valor": self.resultado, "correcta": True}]
        
        while len(opciones) < 4:
            val = random.randint(2, 8)
            if not any(d['valor'] == val for d in opciones):
                opciones.append({"valor": val, "correcta": False})
        random.shuffle(opciones)

        # 4. Crear Fichas
        frame_w = self.ancho_real_frame 
        
        y_pos = self.content_frame.winfo_height() - int(180 * self.scale)
        if y_pos < 0: 
            y_pos = int(self.master.winfo_screenheight() * 0.85) - int(220 * self.scale)

        zona_width = frame_w // 4
        
        for i, op in enumerate(opciones):
            img_opt = self.crear_imagen_compuesta(self.img_actual_name, op["valor"], is_option=True)
            
            lbl = tk.Label(self.content_frame, image=img_opt, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_opt 
            lbl.es_correcta = op["correcta"]
            lbl.es_opcion_juego = True
            
            x_pos = (i * zona_width) + (zona_width // 2) - (self.box_size // 2)
            
            lbl.place(x=x_pos, y=y_pos)
            
            self.master.update_idletasks() 
            lbl.home_x = x_pos
            lbl.home_y = y_pos

            lbl.bind("<Button-1>", self.start_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        widget = event.widget
        widget.lift()
        self.drag_data["item"] = widget

    def do_drag(self, event):
        widget = self.drag_data["item"]
        if not widget: return
        
        mouse_x = self.content_frame.winfo_pointerx() - self.content_frame.winfo_rootx()
        mouse_y = self.content_frame.winfo_pointery() - self.content_frame.winfo_rooty()
        
        new_x = mouse_x - (widget.winfo_width() // 2)
        new_y = mouse_y - (widget.winfo_height() // 2)
        
        widget.place(x=new_x, y=new_y)

    def end_drag(self, event):
        widget = self.drag_data["item"]
        self.drag_data["item"] = None
        if not widget: return

        drop_x = widget.winfo_rootx() + (widget.winfo_width() // 2)
        drop_y = widget.winfo_rooty() + (widget.winfo_height() // 2)

        t_x1 = self.lbl_target.winfo_rootx()
        t_y1 = self.lbl_target.winfo_rooty()
        t_x2 = t_x1 + self.lbl_target.winfo_width()
        t_y2 = t_y1 + self.lbl_target.winfo_height()

        if t_x1 < drop_x < t_x2 and t_y1 < drop_y < t_y2:
            if widget.es_correcta:
                # Centrar ficha en el objetivo
                final_x = self.lbl_target.winfo_rootx() - self.content_frame.winfo_rootx()
                final_y = self.lbl_target.winfo_rooty() - self.content_frame.winfo_rooty()
                
                widget.place(x=final_x, y=final_y)
                widget.lift()
                
                # Llamar a la nueva pantalla de victoria
                self.master.after(200, self._show_win_screen)
            else:
                self.return_to_home(widget)
        else:
            self.return_to_home(widget)

    def return_to_home(self, widget):
        widget.place(x=widget.home_x, y=widget.home_y)

    # =============================================================
    # PANTALLA DE FELICITACIÓN PERSONALIZADA (VERDE)
    # =============================================================
    def _show_win_screen(self):
        win = tk.Toplevel(self.master)
        
        # 1. Configuración Sin Bordes
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.grab_set()

        # Dimensiones
        w, h = int(500 * self.scale), int(350 * self.scale)
        
        # Centrar
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        
        # Color del borde (VERDE del juego)
        border_color = GameConfig.MAIN_COLOR 
        win.configure(bg=border_color)

        # 2. Canvas para fondo redondeado
        canvas = tk.Canvas(win, width=w, height=h, bg=border_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Fondo blanco con esquinas redondeadas SIMÉTRICAS
        self._draw_rounded_rectangle(canvas, 10, 10, w-10, h-10, radius=20, fill="white", outline="white")
        
        # --- CONTENIDO ---
        
        # Título "¡Muy Bien!" en VERDE
        tk.Label(win, text="¡Muy Bien!", font=self.font_win_title, bg="white", fg=GameConfig.MAIN_COLOR).place(relx=0.5, rely=0.25, anchor="center")
        
        # Subtítulo con la respuesta correcta
        sub_font = (SYSTEM_FONT, int(16 * self.scale))
        tk.Label(win, text=f"¡La respuesta es {self.resultado}!", font=sub_font, bg="white", fg=GameConfig.TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
        # --- BOTONES ---
        btn_container = tk.Frame(win, bg="white")
        btn_container.place(relx=0.5, rely=0.75, anchor="center")
        
        def action(act):
            win.destroy()
            if act == "next": self._start_new_round()
            elif act == "menu": self.volver_al_menu()
            
        # Efectos Hover
        def on_enter_green(e): e.widget['bg'] = GameConfig.HOVER_COLOR
        def on_leave_green(e): e.widget['bg'] = GameConfig.BTN_NEXT_COLOR
        
        def on_enter_blue(e): e.widget['bg'] = '#7FA6D6'
        def on_leave_blue(e): e.widget['bg'] = GameConfig.BTN_MENU_COLOR

        # Botón Menú (Azul)
        btn_menu = tk.Button(btn_container, text="Menú 🏠", font=self.font_btn,
                             bg=GameConfig.BTN_MENU_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("menu"))
        btn_menu.pack(side=tk.LEFT, padx=15)
        btn_menu.bind("<Enter>", on_enter_blue)
        btn_menu.bind("<Leave>", on_leave_blue)

        # Botón Siguiente (Verde)
        btn_next = tk.Button(btn_container, text="Siguiente ➡", font=self.font_btn,
                             bg=GameConfig.BTN_NEXT_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("next"))
        btn_next.pack(side=tk.LEFT, padx=15)
        btn_next.bind("<Enter>", on_enter_green)
        btn_next.bind("<Leave>", on_leave_green)
    # =============================================================

    def crear_imagen_compuesta(self, nombre_archivo, cantidad, is_option=False):
        s = self.box_size
        canvas_img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(canvas_img)
        
        draw.rectangle([0, 0, s-1, s-1], outline="black" if is_option else GameConfig.TEXT_DARK, width=2)

        item_img = None
        ruta = os.path.join(SCRIPT_DIR, nombre_archivo)
        
        if os.path.exists(ruta):
            try:
                item_img = Image.open(ruta).convert("RGBA")
            except: pass

        cols = 2
        if cantidad > 4: cols = 3
        if cantidad > 6: cols = 3 
        
        cell_w = s // cols
        cell_h = s // ((cantidad + cols - 1) // cols) if cantidad > 2 else s // 2
        if cell_h > s // 2: cell_h = s // 2

        for i in range(cantidad):
            r = i // cols
            c = i % cols
            pad = 4
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
                draw.ellipse([x, y, x+tw, y+th], fill="red", outline="black")

        return ImageTk.PhotoImage(canvas_img)

    def crear_imagen_interrogacion(self):
        s = self.box_size
        img = Image.new("RGB", (s, s), "#EEEEEE")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline="#9E9E9E", width=2)
        try:
            font_name = "arial.ttf" if SYSTEM_OS == "Windows" else "DejaVuSans.ttf"
            font = ImageFont.truetype(font_name, int(s/2))
            bbox = draw.textbbox((0, 0), "?", font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((s-w)/2, (s-h)/2 - 10), "?", fill="#9E9E9E", font=font)
        except:
            draw.text((s//3, s//4), "?", fill="#9E9E9E")
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
    game = MathDragGame(root)
    root.mainloop()
