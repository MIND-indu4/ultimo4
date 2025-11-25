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

# --- CONFIGURACIÓN VISUAL (NIVEL 2) ---
class GameConfig:
    # Colores principales (Verde vibrante pero legible)
    MAIN_COLOR = "#4CAF50"       
    HOVER_COLOR = "#66BB6A"      
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    
    # Colores para la ventana de victoria
    BTN_MENU_COLOR = "#5B84B1"   # Azul grisáceo
    BTN_NEXT_COLOR = "#4CAF50"   # Verde del juego
    
    # Imágenes (Se buscarán en esta carpeta o en ../nivel1)
    IMAGENES = [
        "papa.png", "zanahoria.png", "brocoli.png", "cebolla.png",
        "tomate.png", "lechuga.png", "pepino.png", "calabaza.png",
        "manzana.png", "pera.png", "banana.png"
    ]

# --- FUNCIONES AUXILIARES ---
class MathDragGameLevel2:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 2")
        
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
        self.font_signos = (SYSTEM_FONT, int(50 * self.scale), "bold")
        self.font_btn = (SYSTEM_FONT, int(14 * self.scale), "bold")
        self.font_win_title = (SYSTEM_FONT, int(40 * self.scale), "bold")
        
        self.box_size = int(120 * self.scale) 
        
        self.drag_data = {"item": None}

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

        # Fondo blanco redondeado simétrico
        self._draw_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR, outline="")

        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=self.ancho_real_frame, height=ch-40)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="⬅ Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", lambda e: self.volver_al_menu())
        
        tk.Label(self.content_frame, text="¡Traduce la operación!", font=self.font_title, 
                 bg=GameConfig.CARD_COLOR, fg=GameConfig.MAIN_COLOR).pack(pady=(10, 20))

        # --- ÁREA VISUAL (Imágenes) ---
        self.frame_visual = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_visual.pack(pady=5)

        self.lbl_img1 = tk.Label(self.frame_visual, bg="white", bd=2, relief="solid")
        self.lbl_img1.grid(row=0, column=0, padx=20)
        
        tk.Label(self.frame_visual, text="+", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=1)
        
        self.lbl_img2 = tk.Label(self.frame_visual, bg="white", bd=2, relief="solid")
        self.lbl_img2.grid(row=0, column=2, padx=20)
        
        tk.Label(self.frame_visual, text="=", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=3)
        
        self.lbl_img_res = tk.Label(self.frame_visual, bg="white", bd=2, relief="solid")
        self.lbl_img_res.grid(row=0, column=4, padx=20)

        # --- ÁREA SLOTS (Donde se sueltan los números) ---
        self.frame_slots = tk.Frame(self.content_frame, bg=GameConfig.CARD_COLOR)
        self.frame_slots.pack(pady=10)

        # Slot 1
        self.lbl_target1 = tk.Label(self.frame_slots, bg="white", bd=0) 
        self.lbl_target1.grid(row=0, column=0, padx=20)
        
        tk.Label(self.frame_slots, text="+", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=1)
        
        # Slot 2
        self.lbl_target2 = tk.Label(self.frame_slots, bg="white", bd=0)
        self.lbl_target2.grid(row=0, column=2, padx=20)
        
        tk.Label(self.frame_slots, text="=", font=self.font_signos, bg=GameConfig.CARD_COLOR, fg=GameConfig.TEXT_DARK).grid(row=0, column=3)
        
        # Slot 3 (Resultado)
        self.lbl_target3 = tk.Label(self.frame_slots, bg="white", bd=0)
        self.lbl_target3.grid(row=0, column=4, padx=20)

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
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, "es_ficha_numero"):
                widget.destroy()

        self.estado_slots = [False, False, False] 
        self.img_empty_slot = self.crear_imagen_slot_vacio()
        
        for slot in [self.lbl_target1, self.lbl_target2, self.lbl_target3]:
            slot.config(image=self.img_empty_slot)
            slot.image = self.img_empty_slot 
            slot.ocupado_por = None 

        # Lógica Matemática
        self.img_actual_name = random.choice(GameConfig.IMAGENES)
        self.num1 = random.randint(1, 4)
        self.num2 = random.randint(1, 4)
        self.resultado = self.num1 + self.num2

        self.lbl_target1.valor_esperado = self.num1
        self.lbl_target2.valor_esperado = self.num2
        self.lbl_target3.valor_esperado = self.resultado

        # Actualizar Imágenes Visuales
        img1 = self.crear_imagen_verdura(self.img_actual_name, self.num1)
        self.lbl_img1.config(image=img1)
        self.lbl_img1.image = img1

        img2 = self.crear_imagen_verdura(self.img_actual_name, self.num2)
        self.lbl_img2.config(image=img2)
        self.lbl_img2.image = img2

        img_res = self.crear_imagen_verdura(self.img_actual_name, self.resultado)
        self.lbl_img_res.config(image=img_res)
        self.lbl_img_res.image = img_res

        # Generar Opciones (Fichas de números)
        numeros_disponibles = [self.num1, self.num2, self.resultado]
        while len(numeros_disponibles) < 6:
            n = random.randint(1, 9)
            if n not in numeros_disponibles: 
                numeros_disponibles.append(n)
            elif len(numeros_disponibles) < 9: 
                 numeros_disponibles.append(n)
        
        numeros_disponibles = numeros_disponibles[:6]
        random.shuffle(numeros_disponibles)

        frame_w = self.ancho_real_frame 
        y_pos = self.content_frame.winfo_height() - int(150 * self.scale)
        if y_pos < 0: y_pos = int(self.master.winfo_screenheight() * 0.85) - int(180 * self.scale)

        zona_width = frame_w // 6
        
        for i, val in enumerate(numeros_disponibles):
            img_num = self.crear_imagen_numero(val)
            
            lbl = tk.Label(self.content_frame, image=img_num, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_num 
            lbl.valor = val 
            lbl.es_ficha_numero = True
            
            x_pos = (i * zona_width) + (zona_width // 2) - (self.box_size // 2)
            
            lbl.place(x=x_pos, y=y_pos)
            
            self.master.update_idletasks() 
            lbl.home_x = x_pos
            lbl.home_y = y_pos
            lbl.bloqueado = False 

            lbl.bind("<Button-1>", self.start_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        widget = event.widget
        if widget.bloqueado: return 
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

        targets = [self.lbl_target1, self.lbl_target2, self.lbl_target3]
        encontrado = False

        for i, target in enumerate(targets):
            if self.estado_slots[i]: continue 
            
            t_x1 = target.winfo_rootx()
            t_y1 = target.winfo_rooty()
            t_x2 = t_x1 + target.winfo_width()
            t_y2 = t_y1 + target.winfo_height()

            if t_x1 < drop_x < t_x2 and t_y1 < drop_y < t_y2:
                if widget.valor == target.valor_esperado:
                    final_x = target.winfo_rootx() - self.content_frame.winfo_rootx()
                    final_y = target.winfo_rooty() - self.content_frame.winfo_rooty()
                    
                    widget.place(x=final_x, y=final_y)
                    widget.bloqueado = True 
                    self.estado_slots[i] = True
                    encontrado = True
                    
                    if all(self.estado_slots):
                        self.master.after(300, self._show_win_screen)
                    break

        if not encontrado:
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
        
        # Color del borde
        border_color = GameConfig.MAIN_COLOR 
        win.configure(bg=border_color)

        # 2. Canvas
        canvas = tk.Canvas(win, width=w, height=h, bg=border_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Fondo blanco simétrico
        self._draw_rounded_rectangle(canvas, 10, 10, w-10, h-10, radius=20, fill="white", outline="white")
        
        # --- CONTENIDO ---
        tk.Label(win, text="¡Muy Bien!", font=self.font_win_title, bg="white", fg=GameConfig.MAIN_COLOR).place(relx=0.5, rely=0.25, anchor="center")
        
        sub_font = (SYSTEM_FONT, int(16 * self.scale))
        tk.Label(win, text="¡Completaste la operación! ➕", font=sub_font, bg="white", fg=GameConfig.TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
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

        # Botón Menú
        btn_menu = tk.Button(btn_container, text="Menú 🏠", font=self.font_btn,
                             bg=GameConfig.BTN_MENU_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("menu"))
        btn_menu.pack(side=tk.LEFT, padx=15)
        btn_menu.bind("<Enter>", on_enter_blue)
        btn_menu.bind("<Leave>", on_leave_blue)

        # Botón Siguiente
        btn_next = tk.Button(btn_container, text="Siguiente ➡", font=self.font_btn,
                             bg=GameConfig.BTN_NEXT_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("next"))
        btn_next.pack(side=tk.LEFT, padx=15)
        btn_next.bind("<Enter>", on_enter_green)
        btn_next.bind("<Leave>", on_leave_green)
    # =============================================================

    # --- CARGA DE IMÁGENES ---
    def crear_imagen_verdura(self, nombre_archivo, cantidad):
        s = self.box_size
        canvas_img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(canvas_img)
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.TEXT_DARK, width=2)

        item_img = None
        
        # Busca .png, .jpg, .jpeg
        exts = ["", ".png", ".jpg", ".jpeg"]
        base_name = os.path.splitext(nombre_archivo)[0]
        
        posibles_rutas = []
        for ext in exts:
            fname = base_name + ext
            posibles_rutas.append(os.path.join(SCRIPT_DIR, fname))
            posibles_rutas.append(os.path.join(SCRIPT_DIR, "imagenes", fname))
            posibles_rutas.append(os.path.join(SCRIPT_DIR, "assets", fname))
            # Buscar en nivel1 si comparten recursos
            posibles_rutas.append(os.path.join(SCRIPT_DIR, "..", "nivel1", fname))
        
        for r in posibles_rutas:
            if os.path.exists(r):
                try:
                    item_img = Image.open(r).convert("RGBA")
                    break
                except: pass

        cols = 2
        if cantidad > 4: cols = 3
        
        rows_visuales = 2
        if cantidad > 4: rows_visuales = 3
        
        cell_w = s // cols
        cell_h = s // rows_visuales

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
                try:
                    font_err = ImageFont.truetype("arial.ttf", 10)
                except:
                    font_err = ImageFont.load_default()
                draw.text((x, y + th//2 - 5), "?", fill="red", font=font_err)

        return ImageTk.PhotoImage(canvas_img)

    def crear_imagen_numero(self, numero):
        s = self.box_size
        img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.MAIN_COLOR, width=3)
        
        try:
            font_name = "arial.ttf" if SYSTEM_OS == "Windows" else "DejaVuSans.ttf"
            font = ImageFont.truetype(font_name, int(s*0.6))
        except:
            font = ImageFont.load_default()

        text = str(numero)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((s-w)/2, (s-h)/2 - 5), text, fill=GameConfig.MAIN_COLOR, font=font)
        except:
            draw.text((s//3, s//4), text, fill=GameConfig.MAIN_COLOR)

        return ImageTk.PhotoImage(img)

    def crear_imagen_slot_vacio(self):
        s = self.box_size
        img = Image.new("RGB", (s, s), "white") 
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline=GameConfig.MAIN_COLOR, width=2)
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
    game = MathDragGameLevel2(root)
    root.mainloop()
