import tkinter as tk
from tkinter import messagebox, Frame, Button, Label, Toplevel, Canvas
import subprocess
import sys
import os
import platform
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ========== DETECCIÓN DE SISTEMA ==========
ES_WINDOWS = platform.system() == "Windows"

# ========== RUTAS (Optimizada) ==========
def get_project_root():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Si hay una carpeta assets al lado, estamos en la raíz
    if os.path.exists(os.path.join(script_dir, "simondice.png")): 
        return script_dir
    
    # Si no, subimos un nivel (por si organizaste en carpetas)
    parent_dir = os.path.dirname(script_dir)
    return parent_dir

PROJECT_ROOT = get_project_root()

def get_safe_path(*path_parts):
    safe_path = os.path.join(PROJECT_ROOT, *path_parts)
    return os.path.abspath(safe_path)

# ========== FUENTE (Font) COMPATIBLE ==========
def get_font_name():
    if ES_WINDOWS:
        return "arial.ttf"
    else:
        return "DejaVuSans.ttf" 

FONT_NAME = get_font_name()

# ========== EXTENSIÓN DE CANVAS ==========
def _round_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
              x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = _round_rectangle

# ========== CLASE PRINCIPAL DEL MENÚ ==========
class GameMenu:
    def __init__(self, master):
        self.master = master
        self.main_project_root = PROJECT_ROOT
        
        # Configuración de pantalla completa
        master.attributes("-fullscreen", True)
        master.bind("<Escape>", self.toggle_fullscreen)
        
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        
        # Ajuste de escala
        self.base_width = 1000
        self.base_height = 800
        self.scale = min(self.screen_width / self.base_width, self.screen_height / self.base_height)
        
        self.yellow_bg = "#FFDE59"
        self.white_frame_bg = "#FFFFFF"
        self.text_color = "#333333"
        self.red_border = "#FF4B4B"
        self.pink_border = "#FF69B4"
        self.green_border = "#4CAF50"
        self.blue_border = "#00BFFF"
        self.menu_bg = "#F5F5F5" 
        
        master.config(bg=self.yellow_bg)
        self.menu_open = False
        
        # Diccionario de imágenes
        self.icon_paths = {
            "simon": "simondice.png", 
            "puzzle": "rompecabezas.png", 
            "math": "mate.png", 
            "tea": "TEAyudo.png",
            "menu": "menu.png",
            "close": "cerrar.png",
        }
        self.icons = {}
        
        self.create_all_placeholders() 
        self.load_icons()
        self.create_widgets()

    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.master.attributes("-fullscreen")
        self.master.attributes("-fullscreen", not is_fullscreen)
        self.master.after(100, self.position_corner_buttons) 

    def create_all_placeholders(self):
        scaled_size = int(140 * self.scale)
        small_size = int(40 * self.scale)
        
        placeholders_config = {
            "simondice.png": {"size": scaled_size, "color": (255, 0, 0), "text": "S", "type": "game"},
            "rompecabezas.png": {"size": scaled_size, "color": (255, 105, 180), "text": "P", "type": "game"},
            "mate.png": {"size": scaled_size, "color": (0, 128, 0), "text": "M", "type": "game"},
            "TEAyudo.png": {"size": scaled_size, "color": (0, 191, 255), "text": "T", "type": "game"},
            "menu.png": {"size": small_size, "color": (0, 0, 0), "text": "☰", "type": "corner"},
            "cerrar.png": {"size": small_size, "color": (255, 0, 0), "text": "✕", "type": "corner"},
        }

        for filename_relative, config in placeholders_config.items():
            full_path = os.path.join(self.main_project_root, filename_relative)
            if not os.path.exists(full_path):
                size = config["size"]
                color = config["color"]
                text = config["text"]
                icon_type = config["type"]
                img = Image.new('RGBA', (size, size), (255, 255, 255, 0)) 
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype(FONT_NAME, int(size * 0.7) if icon_type == "corner" else int(size * 0.6))
                except IOError:
                    font = ImageFont.load_default()
                
                if icon_type == "game":
                    draw.rounded_rectangle((0, 0, size, size), radius=size//4, fill=color)
                    text_fill_color = (255, 255, 255)
                else: 
                    text_fill_color = color

                bbox = draw.textbbox((0,0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (size - text_width) / 2
                text_y = (size - text_height) / 2 - (5 if icon_type == "game" else 0) 
                draw.text((text_x, text_y), text, font=font, fill=text_fill_color)
                img.save(full_path)

    def load_icons(self):
        scaled_game_size = int(140 * self.scale)
        scaled_small_size = int(40 * self.scale)
        for name, filename in self.icon_paths.items():
            full_path = os.path.join(self.main_project_root, filename)
            try:
                img = Image.open(full_path)
                if name in ["menu", "close"]:
                    img = img.resize((scaled_small_size, scaled_small_size), Image.LANCZOS)
                else:
                    img = img.resize((scaled_game_size, scaled_game_size), Image.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error cargando icono {name}: {e}")
                self.icons[name] = None

    def create_widgets(self):
        margin = int(40 * self.scale)
        self.main_canvas = tk.Canvas(self.master, bg=self.yellow_bg, highlightthickness=0, bd=0)
        self.main_canvas.place(x=margin, y=margin, width=self.screen_width - 2*margin, height=self.screen_height - 2*margin)

        canvas_width = self.screen_width - (2 * margin)
        canvas_height = self.screen_height - (2 * margin)
        self.round_rect_radius = int(40 * self.scale)
        
        self.main_canvas.create_rounded_rectangle(0, 0, canvas_width, canvas_height,
                                                  radius=self.round_rect_radius,
                                                  fill=self.white_frame_bg, outline="", width=0)

        title_font_size = int(28 * self.scale)
        title_label = tk.Label(self.main_canvas, text="Seleccione una actividad",
                               font=("Arial", title_font_size, "bold"),
                               fg=self.text_color, bg=self.white_frame_bg)
        title_y = int(90 * self.scale)
        self.main_canvas.create_window(canvas_width / 2, title_y, window=title_label, anchor="center")

        game_buttons_frame = tk.Frame(self.main_canvas, bg=self.white_frame_bg)
        buttons_y = canvas_height / 2 + int(50 * self.scale)
        self.main_canvas.create_window(canvas_width / 2, buttons_y, window=game_buttons_frame, anchor="center")

        button_width = int(200 * self.scale)
        button_height = int(200 * self.scale)
        button_dimensions = {"width": button_width, "height": button_height}
        pad = int(25 * self.scale)

        self.create_game_button(game_buttons_frame, "Simon dice", self.icons.get("simon"), 
                               self.run_game1, self.red_border, 0, 0, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "Rompecabezas", self.icons.get("puzzle"), 
                               self.run_game2, self.pink_border, 0, 1, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "Matematicas", self.icons.get("math"), 
                               self.run_game3, self.green_border, 1, 0, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "TEAyudo", self.icons.get("tea"), 
                               self.run_game4, self.blue_border, 1, 1, button_dimensions, pad)

        self.create_side_menu()
        self.create_corner_buttons()
        self.position_corner_buttons()

    def create_game_button(self, parent, text, icon_image, command, border_color, row, col, dimensions, pad):
        frame_wrapper = tk.Frame(parent, bg=self.white_frame_bg)
        frame_wrapper.grid(row=row, column=col, padx=pad, pady=pad)

        button_canvas = tk.Canvas(frame_wrapper, width=dimensions["width"], height=dimensions["height"],
                                  bg=self.white_frame_bg, highlightthickness=0)
        button_canvas.pack()

        shadow_offset = int(8 * self.scale)
        radius = int(30 * self.scale)
        
        button_canvas.create_rounded_rectangle(shadow_offset, shadow_offset, 
                                            dimensions["width"]+shadow_offset, dimensions["height"]+shadow_offset,
                                            radius=radius, fill="#E0E0E0", outline="", width=0)
        
        button_canvas.create_rounded_rectangle(0, 0, dimensions["width"], dimensions["height"],
                                            radius=radius, fill=self.white_frame_bg, outline=border_color, width=int(4 * self.scale))

        if icon_image:
            icon_frame = tk.Frame(button_canvas, bg=self.white_frame_bg)
            icon_frame.place(relx=0.5, rely=0.4, anchor="center")
            icon_label = tk.Label(icon_frame, image=icon_image, bg=self.white_frame_bg)
            icon_label.pack()
            icon_label.bind("<Button-1>", lambda e: command())
        else:
            placeholder_label = tk.Label(button_canvas, text="[ICON]", font=("Arial", int(12 * self.scale), "bold"), 
                                       bg=self.white_frame_bg, fg=border_color)
            button_canvas.create_window(dimensions["width"] / 2, dimensions["height"] / 2, 
                                      window=placeholder_label, anchor="center")
            placeholder_label.bind("<Button-1>", lambda e: command())

        text_font_size = int(16 * self.scale)
        text_label = tk.Label(button_canvas, text=text, font=("Arial", text_font_size, "bold"), 
                            fg=self.text_color, bg=self.white_frame_bg)
        text_y = dimensions["height"] * 0.7
        button_canvas.create_window(dimensions["width"] / 2, text_y, window=text_label, anchor="center")
        text_label.bind("<Button-1>", lambda e: command())
        button_canvas.bind("<Button-1>", lambda e: command())

    # ========== MENÚ LATERAL ==========
    def create_side_menu(self):
        self.side_menu_frame = Frame(self.master, bg=self.menu_bg, relief="flat")
        menu_title = Label(self.side_menu_frame, text="MENÚ", 
                          font=("Arial", int(20 * self.scale), "bold"),
                          fg=self.text_color, bg=self.menu_bg)
        menu_title.pack(pady=int(20 * self.scale), padx=int(20 * self.scale))
        
        menu_items = [("📊 Estadísticas", self.show_stats), ("⚙️ Ajustes", self.show_settings), ("ℹ️ Acerca de...", self.show_about), ("⏰ temporizador", self.show_clock)]
        
        for text, command in menu_items:
            btn = Button(self.side_menu_frame, text=text, font=("Arial", int(14 * self.scale)),
                        command=command, bg=self.menu_bg, fg=self.text_color,
                        activebackground=self.white_frame_bg, activeforeground=self.text_color,
                        bd=0, relief="flat", anchor="w", padx=int(20 * self.scale))
            btn.pack(fill="x", pady=int(5 * self.scale), padx=int(10 * self.scale))
            
        separator = Frame(self.side_menu_frame, bg="#CCCCCC", height=2)
        separator.pack(fill="x", padx=int(20 * self.scale), pady=int(20 * self.scale))
        
        logout_btn = Button(self.side_menu_frame, text="🚪 Salir del Sistema", 
                           font=("Arial", int(14 * self.scale), "bold"),
                           command=self.exit_application, bg=self.red_border, fg="white",
                           activebackground=self.red_border, activeforeground="white",
                           bd=0, relief="flat", padx=int(20 * self.scale), pady=int(10 * self.scale))
        logout_btn.pack(fill="x", padx=int(20 * self.scale), pady=int(10 * self.scale))

    def toggle_side_menu(self):
        if self.menu_open: self.close_side_menu()
        else: self.open_side_menu()

    def open_side_menu(self):
        self.menu_open = True
        if hasattr(self, 'menu_btn'): self.menu_btn.config(state="disabled")
        menu_width = int(300 * self.scale)
        menu_height = self.screen_height
        self.side_menu_frame.place(x=0, y=0, width=menu_width, height=menu_height)
        
        close_menu_btn = Button(self.side_menu_frame, text="✕", font=("Arial", int(18 * self.scale), "bold"),
                               command=self.close_side_menu, bg=self.menu_bg, fg=self.text_color,
                               activebackground=self.menu_bg, activeforeground="red", bd=0, relief="flat")
        close_menu_btn.place(x=menu_width - int(40 * self.scale), y=int(10 * self.scale))
        self.master.bind("<Button-1>", self.check_click_outside_menu)

    def close_side_menu(self):
        self.menu_open = False
        self.side_menu_frame.place_forget()
        if hasattr(self, 'menu_btn'): self.menu_btn.config(state="normal")
        self.master.unbind("<Button-1>")

    def check_click_outside_menu(self, event):
        if event.widget != self.menu_btn:
            menu_width = self.side_menu_frame.winfo_width()
            if event.x > menu_width: self.close_side_menu()

    def create_corner_buttons(self):
        if self.icons.get("menu"):
            self.menu_btn = tk.Button(self.master, image=self.icons["menu"], command=self.toggle_side_menu,
                                      bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
        else:
            self.menu_btn = tk.Button(self.master, text="☰ MENU", command=self.toggle_side_menu,
                                    font=("Arial", int(14 * self.scale), "bold"), bg=self.yellow_bg, bd=0, 
                                    fg=self.text_color, activebackground=self.yellow_bg, activeforeground=self.text_color)
        
        if self.icons.get("close"):
            self.close_btn = tk.Button(self.master, image=self.icons["close"], command=self.exit_application,
                                       bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
        else:
            self.close_btn = tk.Button(self.master, text="✕ SALIR", command=self.exit_application,
                                    font=("Arial", int(14 * self.scale), "bold"), fg="#D32F2F", bg=self.yellow_bg,
                                    activebackground=self.yellow_bg, bd=0, padx=int(10 * self.scale), pady=int(5 * self.scale))

    def position_corner_buttons(self):
        button_padding = int(35 * self.scale)
        self.master.update_idletasks()
        if hasattr(self, 'menu_btn'): self.menu_btn.place(x=button_padding, y=button_padding)
        if hasattr(self, 'close_btn'):
            window_width = self.master.winfo_width()
            btn_width = self.close_btn.winfo_width()
            x_pos = window_width - btn_width - button_padding
            self.close_btn.place(x=x_pos, y=button_padding)

    # ========== LÓGICA DE JUEGOS ==========
    def run_game1(self):
        self._open_and_close('simon dice', 'menu', 'menu_simondice.py') 

    def run_game2(self):
        self._open_and_close('rompecabezas', 'menu', 'menu_rompecabezas.py')

    def run_game3(self):
        self._open_and_close('matematicas', 'menu', 'menumatematicas.py')

    def run_game4(self):
        self._open_and_close('pictogramas', 'TEAyudo.py')  

    def _open_and_close(self, *path_segments_to_script):
        try:
            if len(path_segments_to_script) == 1 and path_segments_to_script[0].endswith(".py"):
                script_path = os.path.join(os.path.dirname(__file__), path_segments_to_script[0])
            else:
                script_path = get_safe_path(*path_segments_to_script)
            
            script_dir = os.path.dirname(script_path)

            if not os.path.exists(script_path):
                messagebox.showerror("Error CRÍTICO", f"Archivo no encontrado:\n{script_path}")
                return

            self.master.destroy() 
            
            cmd = [sys.executable, "-u", script_path]
            
            kwargs = {}
            if ES_WINDOWS:
                kwargs['creationflags'] = subprocess.DETACHED_PROCESS
            
            subprocess.Popen(cmd, cwd=script_dir, **kwargs)
            sys.exit(0)
            
        except Exception as e:
            print(f"Error al abrir juego: {e}")

    # ========== OPCIONES DE MENÚ ==========
    def show_stats(self):
        messagebox.showinfo("Estadísticas", "Próximamente: Estadísticas de juego")
        self.close_side_menu()

    def show_settings(self):
        messagebox.showinfo("Ajustes", "Próximamente: Panel de configuración")
        self.close_side_menu()

    # --- NUEVA LÓGICA DE ACERCA DE ---
    def show_about(self):
        self.close_side_menu() 

        ventana_acerca = Toplevel(self.master)
        ventana_acerca.title("Acerca de Nosotros")
        ventana_acerca.attributes('-fullscreen', True)
        ventana_acerca.configure(bg="white")

        canvas_main = Canvas(ventana_acerca, bg="white", highlightthickness=0)
        canvas_main.pack(fill="both", expand=True)

        ruta_imagen = os.path.join(self.main_project_root, "nosotros.png")
        
        if os.path.exists(ruta_imagen):
            try:
                imagen_original = Image.open(ruta_imagen)
                
                ancho_pantalla = self.master.winfo_screenwidth()
                alto_pantalla = self.master.winfo_screenheight()

                ratio = min(ancho_pantalla / imagen_original.width, alto_pantalla / imagen_original.height)
                nuevo_ancho = int(imagen_original.width * ratio)
                nuevo_alto = int(imagen_original.height * ratio)

                pos_x = (ancho_pantalla - nuevo_ancho) // 2
                pos_y = (alto_pantalla - nuevo_alto) // 2

                imagen_redimensionada = imagen_original.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)

                canvas_main.create_image(pos_x, pos_y, anchor="nw", image=imagen_tk)
                canvas_main.image = imagen_tk 
            except Exception as e:
                print(f"Error cargando imagen nosotros: {e}")
                canvas_main.create_text(self.screen_width//2, self.screen_height//2, text="Error al cargar imagen")
        else:
            canvas_main.create_text(self.screen_width//2, self.screen_height//2, 
                                    text="No se encontró 'nosotros.png'", font=("Arial", 20))

        self._dibujar_boton_volver(canvas_main, ventana_acerca)

        ventana_acerca.bind("<Escape>", lambda event: ventana_acerca.destroy())

    def _dibujar_boton_volver(self, canvas, ventana):
        ancho_btn = 140
        alto_btn = 45
        radio = 20
        # Posición: Esquina superior derecha con margen
        x = self.screen_width - ancho_btn - 30 
        y = 30
        color_normal = "#FF5733" # Naranja
        color_hover = "#C70039"  # Rojo oscuro
        
        x1, y1 = x, y
        x2, y2 = x + ancho_btn, y + alto_btn
        points = [x1+radio, y1, x1+radio, y1, x2-radio, y1, x2-radio, y1, x2, y1, x2, y1+radio, x2, y1+radio, 
                  x2, y2-radio, x2, y2-radio, x2, y2, x2-radio, y2, x2-radio, y2, x1+radio, y2, x1+radio, y2, 
                  x1, y2, x1, y2-radio, x1, y2-radio, x1, y1+radio, x1, y1+radio, x1, y1]

        btn_bg = canvas.create_polygon(points, fill=color_normal, smooth=True, tags="btn_volver")
        canvas.create_text(x + ancho_btn/2, y + alto_btn/2, text="⬅ Volver", fill="white", 
                           font=("Arial", 12, "bold"), tags="btn_volver")

        def al_entrar(e):
            canvas.itemconfig(btn_bg, fill=color_hover)
            canvas.config(cursor="hand2")

        def al_salir(e):
            canvas.itemconfig(btn_bg, fill=color_normal)
            canvas.config(cursor="")

        def al_clic(e):
            ventana.destroy()

        canvas.tag_bind("btn_volver", "<Enter>", al_entrar)
        canvas.tag_bind("btn_volver", "<Leave>", al_salir)
        canvas.tag_bind("btn_volver", "<Button-1>", al_clic)

    def show_clock(self):
        self._open_and_close('reloj_semaforo.py')

    def exit_application(self):
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
            self.master.destroy()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    menu = GameMenu(root)
    root.update_idletasks() 
    menu.position_corner_buttons() 
    root.mainloop()