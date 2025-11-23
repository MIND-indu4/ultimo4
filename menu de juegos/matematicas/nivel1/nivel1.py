import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess

# --- CONFIGURACIÓN ---
class GameConfig:
    MAIN_COLOR = "#4CAF50"       # Verde vibrante
    HOVER_COLOR = "#66BB6A"
    TEXT_DARK = "#212121"
    CARD_COLOR = "white"
    
    # Nombres de tus imágenes
    IMAGENES = [
        "manzana.png", 
        "pera.jpg", 
        "banana.png", 
        "frutilla.png", 
        "naranja.png",
        "limon.png",
        "piña.png",
        "sandia.png"
    ]


# --- FUNCIONES AUXILIARES ---
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
              x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class MathDragGame:
    def __init__(self, master):
        self.master = master
        master.title("Matemáticas - Nivel 1")
        master.attributes("-fullscreen", True)
        master.configure(bg=GameConfig.MAIN_COLOR)

        # Escala dinámica
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1280
        base_height = 800
        self.scale = min(screen_width / base_width, screen_height / base_height)

        # Fuentes y Tamaños
        self.font_title = ("Arial", int(32 * self.scale), "bold")
        self.font_signos = ("Arial", int(50 * self.scale), "bold")
        self.font_btn = ("Arial", int(14 * self.scale), "bold")
        
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
        
        # Calculamos el ancho de la tarjeta (85% de la pantalla)
        cw = int(sw * 0.85)
        ch = int(sh * 0.85)
        cx = sw // 2
        cy = sh // 2
        
        # --- CORRECCIÓN DE CENTRADO ---
        # Guardamos el ancho real disponible para el contenido (ancho tarjeta - padding)
        # Esto asegura que el cálculo sea exacto desde el milisegundo 0.
        self.ancho_real_frame = cw - 40 

        # Dibujar fondo blanco redondeado
        create_rounded_rectangle(self.main_canvas, cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2, radius=40, fill=GameConfig.CARD_COLOR)

        # Frame principal SOBRE la tarjeta
        self.content_frame = tk.Frame(self.main_canvas, bg=GameConfig.CARD_COLOR)
        self.content_frame.place(x=cx - cw//2 + 20, y=cy - ch//2 + 20, width=self.ancho_real_frame, height=ch-40)

        # Botón Menú
        self.btn_menu = tk.Label(self.content_frame, text="Menú", font=self.font_btn, 
                                   bg=GameConfig.MAIN_COLOR, fg="white", padx=15, pady=8, cursor="hand2")
        self.btn_menu.place(x=10, y=10)
        self.btn_menu.bind("<Button-1>", self.volver_al_menu)
        
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
        # --- CORRECCIÓN: Usamos el ancho calculado matemáticamente, no el del widget ---
        frame_w = self.ancho_real_frame 
        
        # Posición Y en la parte inferior
        y_pos = self.content_frame.winfo_height() - int(180 * self.scale)
        # Si es la primera vez y height da 1, usamos un estimado
        if y_pos < 0: 
            y_pos = int(self.master.winfo_screenheight() * 0.85) - int(220 * self.scale)

        # Dividimos el ancho total en 4 zonas exactas
        zona_width = frame_w // 4
        
        for i, op in enumerate(opciones):
            img_opt = self.crear_imagen_compuesta(self.img_actual_name, op["valor"], is_option=True)
            
            lbl = tk.Label(self.content_frame, image=img_opt, bg="white", bd=1, relief="raised", cursor="hand2")
            lbl.image = img_opt 
            lbl.es_correcta = op["correcta"]
            lbl.es_opcion_juego = True
            
            # Cálculo de centro exacto
            # (i * ancho_zona) nos lleva al inicio de la zona
            # + (ancho_zona // 2) nos lleva al centro de la zona
            # - (tamaño_caja // 2) retrocede la mitad de la imagen para que quede centrada
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
                final_x = self.lbl_target.winfo_rootx() - self.content_frame.winfo_rootx()
                final_y = self.lbl_target.winfo_rooty() - self.content_frame.winfo_rooty()
                
                widget.place(x=final_x, y=final_y)
                widget.lift()
                
                self.master.after(200, self.game_win)
            else:
                self.return_to_home(widget)
        else:
            self.return_to_home(widget)

    def return_to_home(self, widget):
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
        tk.Label(win, text="¡Excelente trabajo! 🎉", font=("Arial", 14), bg="white", fg="#555").pack(pady=10)
        
        btn = tk.Label(win, text="Siguiente Nivel", font=("Arial", 14, "bold"),
                       bg=GameConfig.MAIN_COLOR, fg="white", padx=20, pady=10, cursor="hand2")
        btn.pack(pady=20)
        
        def reiniciar(e):
            win.destroy()
            self._start_new_round()
            
        btn.bind("<Button-1>", reiniciar)

    def crear_imagen_compuesta(self, nombre_archivo, cantidad, is_option=False):
        s = self.box_size
        canvas_img = Image.new("RGB", (s, s), "white")
        draw = ImageDraw.Draw(canvas_img)
        
        draw.rectangle([0, 0, s-1, s-1], outline="black" if is_option else GameConfig.TEXT_DARK, width=2)

        item_img = None
        rutas = [nombre_archivo, os.path.join("imagenes", nombre_archivo), os.path.join("assets", nombre_archivo)]
        for r in rutas:
            if os.path.exists(r):
                try:
                    item_img = Image.open(r).convert("RGBA")
                    break
                except: pass

        cols = 2
        if cantidad > 4: cols = 3
        if cantidad > 6: cols = 3 
        
        rows = (cantidad + cols - 1) // cols
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
                draw.ellipse([x, y, x+tw, y+th], fill=GameConfig.MAIN_COLOR, outline="black")

        return ImageTk.PhotoImage(canvas_img)

    def crear_imagen_interrogacion(self):
        s = self.box_size
        img = Image.new("RGB", (s, s), "#EEEEEE")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, s-1, s-1], outline="#9E9E9E", width=2)
        try:
            font = ImageFont.truetype("arial.ttf", int(s/2))
            bbox = draw.textbbox((0, 0), "?", font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((s-w)/2, (s-h)/2 - 10), "?", fill="#9E9E9E", font=font)
        except:
            draw.text((s//3, s//4), "?", fill="#9E9E9E")
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
    game = MathDragGame(root)
    root.mainloop()