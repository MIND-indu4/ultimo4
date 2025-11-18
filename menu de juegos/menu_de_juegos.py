import tkinter as tk
from tkinter import messagebox, Frame, Button, Label
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ========== RUTAS ABSOLUTAS FORZADAS ==========
def get_project_root():
    """
    Intenta determinar la raíz del proyecto.
    Prioriza encontrar una carpeta 'MIND' en la ruta del script.
    Si no, usa el directorio padre del script.
    """
    try:
        script_path = os.path.abspath(__file__)
        path_parts = script_path.split(os.sep)

        # Buscar la carpeta 'MIND'
        if 'MIND' in path_parts:
            mind_index = path_parts.index('MIND')
            project_root = os.sep.join(path_parts[:mind_index + 1])
            if os.path.exists(project_root):
                return project_root

        # Fallback: directorio padre del script
        script_dir = os.path.dirname(script_path)
        project_root = os.path.dirname(script_dir) # Asume que el script está en una subcarpeta
        if os.path.exists(project_root):
            return project_root

        # Otro fallback: el propio directorio del script si no se encuentra nada más
        if os.path.exists(script_dir):
            return script_dir

        # Fallback de emergencia si todo lo demás falla (ajusta según tu necesidad)
        fallback_path = r"C:\Users\diego\OneDrive\Videos\Proyecto MIND 2025\mind"
        if os.path.exists(fallback_path):
            return fallback_path
        
        messagebox.showerror("ERROR CRÍTICO", "No se pudo determinar PROJECT_ROOT y no se encontró fallback.")
        sys.exit(1)

    except Exception as e:
        messagebox.showerror("ERROR CRÍTICO", f"Excepción al determinar PROJECT_ROOT:\n{e}")
        sys.exit(1)

PROJECT_ROOT = get_project_root()
print(f"🔒 PROJECT_ROOT FINAL: {PROJECT_ROOT}")

def get_safe_path(*path_parts):
    """Genera una ruta absoluta segura dentro del proyecto."""
    safe_path = os.path.join(PROJECT_ROOT, *path_parts)
    return os.path.abspath(safe_path)

# ========== EXTENSIÓN DE CANVAS (para rectángulos redondeados) ==========
def _round_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1]
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = _round_rectangle

# ========== CLASE PRINCIPAL DEL MENÚ ==========
class GameMenu:
    def __init__(self, master):
        self.master = master
        self.main_project_root = PROJECT_ROOT
        
        # ===== CONFIGURACIÓN DE VENTANA =====
        master.attributes("-fullscreen", True)
        master.bind("<Escape>", self.toggle_fullscreen)
        
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.base_width = 1000
        self.base_height = 800
        # Usar min para escalar siempre al factor más restrictivo y evitar desbordamientos
        self.scale = min(self.screen_width / self.base_width, self.screen_height / self.base_height)
        
        # COLORES
        self.yellow_bg = "#FFDE59"
        self.white_frame_bg = "#FFFFFF"
        self.text_color = "#333333"
        self.red_border = "#FF4B4B"
        self.pink_border = "#FF69B4"
        self.green_border = "#4CAF50"
        self.blue_border = "#00BFFF"
        self.menu_bg = "#F5F5F5" # Color de fondo del menú lateral
        
        master.config(bg=self.yellow_bg)
        
        # Variables de control
        self.menu_open = False
        
        # RUTAS DE ICONOS (relativas a PROJECT_ROOT)
        self.icon_paths = {
            "simon": "simondice.png", 
            "puzzle": "rompecabezas.png", 
            "math": "mate.png", 
            "tea": "TEAyudo.png",
            "menu": "menu.png",
            "close": "cerrar.png",
        }
        self.icons = {}
        
        # CREAR PLACEHOLDERS Y CARGAR ICONOS
        # Aseguramos que se creen antes de intentar cargarlos
        self.create_all_placeholders() 
        self.load_icons()
        
        # CREAR WIDGETS
        self.create_widgets()

    def toggle_fullscreen(self, event=None):
        """Alterna el modo de pantalla completa."""
        is_fullscreen = self.master.attributes("-fullscreen")
        self.master.attributes("-fullscreen", not is_fullscreen)
        # Reposiciona los botones de esquina después del cambio de fullscreen
        self.master.after(100, self.position_corner_buttons) 

    def create_all_placeholders(self):
        """Crea iconos placeholder PNG si los archivos no existen."""
        scaled_size = int(140 * self.scale) # Tamaño para iconos de juegos
        small_size = int(40 * self.scale) # Tamaño para iconos de menú/cerrar
        
        # Diccionario para controlar qué placeholder corresponde a qué archivo y estilo
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
                print(f"Creando placeholder: {full_path}")
                size = config["size"]
                color = config["color"]
                text = config["text"]
                icon_type = config["type"]

                img = Image.new('RGBA', (size, size), (255, 255, 255, 0)) # Fondo transparente
                draw = ImageDraw.Draw(img)
                
                try:
                    # Intentar usar una fuente TrueType si está disponible
                    font_path = "arial.ttf" # Asume que Arial está disponible
                    if icon_type == "corner":
                        font = ImageFont.truetype(font_path, int(size * 0.7)) # Más grande para símbolos
                    else: # Game icon
                        font = ImageFont.truetype(font_path, int(size * 0.6))
                except IOError:
                    # Si no se encuentra Arial, usar la fuente predeterminada de PIL
                    print(f"Advertencia: No se encontró {font_path}, usando fuente por defecto.")
                    if icon_type == "corner":
                        font = ImageFont.load_default(int(size * 0.7))
                    else:
                        font = ImageFont.load_default(int(size * 0.6))
                
                # Dibujar el contenido del placeholder
                if icon_type == "game":
                    # Rectángulo redondeado para iconos de juego
                    draw.rounded_rectangle((0, 0, size, size), radius=size//4, fill=color)
                    text_fill_color = (255, 255, 255) # Texto blanco para iconos de juego
                else: # Corner icon (☰, ✕)
                    text_fill_color = color # Color del texto es el color configurado

                # Centrar el texto
                bbox = draw.textbbox((0,0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                # Ajuste vertical para centrado estético
                text_x = (size - text_width) / 2
                text_y = (size - text_height) / 2 - (5 if icon_type == "game" else 0) 
                draw.text((text_x, text_y), text, font=font, fill=text_fill_color)
                
                img.save(full_path)

    def load_icons(self):
        """Carga los iconos desde disco (o usa los placeholders creados)."""
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
                print(f"Error cargando {full_path}: {e}. Se usará placeholder o se ignorará.")
                self.icons[name] = None # En caso de error, el ícono es None

    def create_widgets(self):
        """Crea los widgets principales de la interfaz."""
        margin = int(40 * self.scale)
        
        # Canvas principal que ocupa el centro de la pantalla
        self.main_canvas = tk.Canvas(self.master, bg=self.yellow_bg, highlightthickness=0, bd=0)
        self.main_canvas.place(x=margin, y=margin, width=self.screen_width - 2*margin, height=self.screen_height - 2*margin)

        # RECTÁNGULO BLANCO INTERIOR (fondo del menú)
        canvas_width = self.screen_width - (2 * margin)
        canvas_height = self.screen_height - (2 * margin)
        self.round_rect_radius = int(40 * self.scale)
        
        self.main_canvas.create_rounded_rectangle(0, 0, canvas_width, canvas_height,
                                                  radius=self.round_rect_radius,
                                                  fill=self.white_frame_bg, outline="", width=0)

        # Título centrado
        title_font_size = int(28 * self.scale)
        title_label = tk.Label(self.main_canvas, text="Seleccione una actividad",
                               font=("Arial", title_font_size, "bold"),
                               fg=self.text_color, bg=self.white_frame_bg)
        title_y = int(90 * self.scale)
        self.main_canvas.create_window(canvas_width / 2, title_y, window=title_label, anchor="center")

        # Frame de botones centrado (para las 4 actividades)
        game_buttons_frame = tk.Frame(self.main_canvas, bg=self.white_frame_bg)
        buttons_y = canvas_height / 2 + int(50 * self.scale) # Posición central ligeramente desplazada
        self.main_canvas.create_window(canvas_width / 2, buttons_y, 
                                      window=game_buttons_frame, anchor="center")

        # Dimensiones de botones de actividad
        button_width = int(200 * self.scale)
        button_height = int(200 * self.scale)
        button_dimensions = {"width": button_width, "height": button_height}
        pad = int(25 * self.scale) # Espaciado entre botones

        # CREAR BOTONES DE JUEGO (4 botones en una cuadrícula 2x2)
        self.create_game_button(game_buttons_frame, "Simon dice", self.icons.get("simon"), 
                               self.run_game1, self.red_border, 0, 0, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "Rompecabezas", self.icons.get("puzzle"), 
                               self.run_game2, self.pink_border, 0, 1, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "Matematicas", self.icons.get("math"), 
                               self.run_game3, self.green_border, 1, 0, button_dimensions, pad)
        self.create_game_button(game_buttons_frame, "TEAayudo", self.icons.get("tea"), 
                               self.run_game4, self.blue_border, 1, 1, button_dimensions, pad)

        # CREAR MENÚ LATERAL y BOTONES DE ESQUINA
        self.create_side_menu()
        self.create_corner_buttons()
        # Posicionar los botones de esquina inmediatamente después de crearlos
        self.position_corner_buttons()

    def create_game_button(self, parent, text, icon_image, command, border_color, row, col, dimensions, pad):
        """
        Crea un botón de juego con un diseño visual específico (redondeado, sombra, icono y texto).
        """
        frame_wrapper = tk.Frame(parent, bg=self.white_frame_bg)
        frame_wrapper.grid(row=row, column=col, padx=pad, pady=pad)

        button_canvas = tk.Canvas(frame_wrapper, width=dimensions["width"], height=dimensions["height"],
                                  bg=self.white_frame_bg, highlightthickness=0)
        button_canvas.pack()

        # Sombra y rectángulo principal
        shadow_offset = int(8 * self.scale)
        radius = int(30 * self.scale)
        
        # Sombra
        button_canvas.create_rounded_rectangle(shadow_offset, shadow_offset, 
                                            dimensions["width"]+shadow_offset, dimensions["height"]+shadow_offset,
                                            radius=radius, fill="#E0E0E0", outline="", width=0)
        
        # Rectángulo principal con borde
        button_canvas.create_rounded_rectangle(0, 0, dimensions["width"], dimensions["height"],
                                            radius=radius, fill=self.white_frame_bg, outline=border_color, width=int(4 * self.scale))

        # Icono
        if icon_image:
            # Usar un Frame para el icono permite un posicionamiento más flexible dentro del canvas
            icon_frame = tk.Frame(button_canvas, bg=self.white_frame_bg)
            icon_frame.place(relx=0.5, rely=0.4, anchor="center") # 40% desde arriba para dejar espacio al texto
            
            icon_label = tk.Label(icon_frame, image=icon_image, bg=self.white_frame_bg)
            icon_label.pack()
            icon_label.bind("<Button-1>", lambda e: command()) # Clic en el icono también activa el comando
        else:
            # Placeholder de texto si no hay imagen
            placeholder_label = tk.Label(button_canvas, text="[ICON]", font=("Arial", int(12 * self.scale), "bold"), 
                                       bg=self.white_frame_bg, fg=border_color)
            button_canvas.create_window(dimensions["width"] / 2, dimensions["height"] / 2, 
                                      window=placeholder_label, anchor="center")
            placeholder_label.bind("<Button-1>", lambda e: command())

        # Texto del botón
        text_font_size = int(16 * self.scale)
        text_label = tk.Label(button_canvas, text=text, font=("Arial", text_font_size, "bold"), 
                            fg=self.text_color, bg=self.white_frame_bg)
        text_y = dimensions["height"] * 0.7 # 70% desde arriba (debajo del icono)
        button_canvas.create_window(dimensions["width"] / 2, text_y, window=text_label, anchor="center")
        text_label.bind("<Button-1>", lambda e: command()) # Clic en el texto también activa el comando

        # El clic en el canvas general del botón también activa el comando
        button_canvas.bind("<Button-1>", lambda e: command())

    # ========== MENÚ LATERAL DESPLEGABLE ==========
    def create_side_menu(self):
        """Crea el panel lateral de menú que se despliega desde la izquierda."""
        self.side_menu_frame = Frame(self.master, bg=self.menu_bg, relief="flat")
        
        # Título del menú lateral
        menu_title = Label(self.side_menu_frame, text="MENÚ", 
                          font=("Arial", int(20 * self.scale), "bold"),
                          fg=self.text_color, bg=self.menu_bg)
        menu_title.pack(pady=int(20 * self.scale), padx=int(20 * self.scale))
        
        # Opciones del menú
        menu_items = [
            ("📊 Estadísticas", self.show_stats),
            ("⚙️ Ajustes", self.show_settings),
            ("ℹ️ Acerca de...", self.show_about),
            ("⏰ temporizador", self.show_clock)
        ]
        
        for text, command in menu_items:
            btn = Button(self.side_menu_frame, text=text, 
                        font=("Arial", int(14 * self.scale)),
                        command=command, bg=self.menu_bg, fg=self.text_color,
                        activebackground=self.white_frame_bg, activeforeground=self.text_color,
                        bd=0, relief="flat", anchor="w", padx=int(20 * self.scale))
            btn.pack(fill="x", pady=int(5 * self.scale), padx=int(10 * self.scale))
            
        # Separador visual
        separator = Frame(self.side_menu_frame, bg="#CCCCCC", height=2)
        separator.pack(fill="x", padx=int(20 * self.scale), pady=int(20 * self.scale))
        
        # Botón de salir del sistema
        logout_btn = Button(self.side_menu_frame, text="🚪 Salir del Sistema", 
                           font=("Arial", int(14 * self.scale), "bold"),
                           command=self.exit_application, bg=self.red_border, fg="white",
                           activebackground=self.red_border, activeforeground="white",
                           bd=0, relief="flat", padx=int(20 * self.scale), pady=int(10 * self.scale))
        logout_btn.pack(fill="x", padx=int(20 * self.scale), pady=int(10 * self.scale))

    def toggle_side_menu(self):
        """Alterna la visibilidad del menú lateral."""
        if self.menu_open:
            self.close_side_menu()
        else:
            self.open_side_menu()

    def open_side_menu(self):
        """Muestra el menú lateral."""
        self.menu_open = True
        
        # Deshabilitar botón de menú principal mientras el menú lateral está abierto
        if hasattr(self, 'menu_btn'):
            self.menu_btn.config(state="disabled")
        
        menu_width = int(300 * self.scale)
        menu_height = self.screen_height # Ocupa toda la altura de la pantalla
        
        self.side_menu_frame.place(x=0, y=0, width=menu_width, height=menu_height)
        
        # Botón para cerrar el menú lateral (una 'X' en la esquina superior derecha del menú lateral)
        close_menu_btn = Button(self.side_menu_frame, text="✕", 
                               font=("Arial", int(18 * self.scale), "bold"),
                               command=self.close_side_menu, bg=self.menu_bg, fg=self.text_color,
                               activebackground=self.menu_bg, activeforeground="red",
                               bd=0, relief="flat")
        close_menu_btn.place(x=menu_width - int(40 * self.scale), y=int(10 * self.scale))
        
        # Enlazar un evento para cerrar el menú al hacer clic fuera de él
        self.master.bind("<Button-1>", self.check_click_outside_menu)

    def close_side_menu(self):
        """Oculta el menú lateral."""
        self.menu_open = False
        self.side_menu_frame.place_forget()
        
        # Rehabilitar botón de menú principal
        if hasattr(self, 'menu_btn'):
            self.menu_btn.config(state="normal")
        
        # Desvincular el evento de clic fuera del menú
        self.master.unbind("<Button-1>")

    def check_click_outside_menu(self, event):
        """Verifica si el clic ocurrió fuera del menú lateral para cerrarlo."""
        # Asegurarse de que el evento no es el botón del menú en sí
        if event.widget != self.menu_btn:
            menu_width = self.side_menu_frame.winfo_width()
            # Si el clic está a la derecha del menú (fuera de él)
            if event.x > menu_width:
                self.close_side_menu()

    def create_corner_buttons(self):
        """Crea los botones de menú y cerrar en las esquinas de la ventana principal."""
        # Botón de menú (abre el menú lateral)
        if self.icons.get("menu"):
            self.menu_btn = tk.Button(self.master, image=self.icons["menu"], command=self.toggle_side_menu,
                                      bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
        else:
            # Fallback si el icono no carga
            self.menu_btn = tk.Button(self.master, text="☰ MENU", command=self.toggle_side_menu,
                                    font=("Arial", int(14 * self.scale), "bold"), bg=self.yellow_bg, bd=0, 
                                    fg=self.text_color, activebackground=self.yellow_bg, activeforeground=self.text_color)
        
        # Botón cerrar (cierra la aplicación)
        if self.icons.get("close"):
            self.close_btn = tk.Button(self.master, image=self.icons["close"], command=self.exit_application,
                                       bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
        else:
            # Fallback si el icono no carga
            self.close_btn = tk.Button(self.master, text="✕ SALIR", command=self.exit_application,
                                    font=("Arial", int(14 * self.scale), "bold"), fg="#D32F2F", bg=self.yellow_bg,
                                    activebackground=self.yellow_bg, bd=0, padx=int(10 * self.scale), pady=int(5 * self.scale))

    def position_corner_buttons(self):
        """
        Ajusta la posición de los botones de esquina (menú y cerrar).
        Usa place para posicionamiento absoluto.
        """
        button_padding = int(35 * self.scale)
        self.master.update_idletasks() # Asegura que los widgets tienen sus dimensiones finales

        # Botón menú (esquina superior izquierda)
        if hasattr(self, 'menu_btn'):
            self.menu_btn.place(x=button_padding, y=button_padding)

        # Botón cerrar (esquina superior derecha)
        if hasattr(self, 'close_btn'):
            window_width = self.master.winfo_width()
            btn_width = self.close_btn.winfo_width()
            
            # Calcular posición X para alinear a la derecha
            x_pos = window_width - btn_width - button_padding
            self.close_btn.place(x=x_pos, y=button_padding)

    # ========== LÓGICA DE NAVEGACIÓN (inicio de juegos) ==========
    def run_game1(self):
        """Inicia el juego 'Simon dice'."""
        self._open_and_close('menu de juegos', 'simon dice', 'menu', 'menu_simondice.py') 

    def run_game2(self):
        """Inicia el juego 'Rompecabezas'."""
        self._open_and_close('menu de juegos', 'rompecabezas', 'menu', 'menu_rompecabezas.py')

    def run_game3(self):
        """Inicia el juego 'Matematicas'."""
        self._open_and_close('menu de juegos', 'matematicas', 'menu', 'menumatematicas.py')

    def run_game4(self):
        """Placeholder para 'TEAayudo'."""
        messagebox.showinfo("Juego", "Iniciando TEAayuda...")
        # self._open_and_close('menu de juegos', 'TEAayudo', 'menu', 'menu_teaayudo.py') # Descomentar para un juego real

    def _open_and_close(self, *path_segments_to_script):
        """
        Método UNIFICADO para abrir cualquier juego/script como un subproceso
        y opcionalmente cerrar este menú.
        """
        try:
            # Asegurarse de que el primer segmento sea el nombre del script o la subcarpeta
            # para construir la ruta correctamente desde PROJECT_ROOT.
            # Si el script está en la misma carpeta que este menú, la ruta es directa.
            if len(path_segments_to_script) == 1 and path_segments_to_script[0].endswith(".py"):
                script_path = os.path.join(os.path.dirname(__file__), path_segments_to_script[0])
            else:
                script_path = get_safe_path(*path_segments_to_script)
            
            script_dir = os.path.dirname(script_path)

            print(f"🎯 Intentando abrir: {script_path}")
            print(f"📂 Directorio: {script_dir}")
            print(f"✅ ¿Existe archivo? {os.path.exists(script_path)}")

            if not os.path.exists(script_path):
                messagebox.showerror("Error CRÍTICO", f"Archivo no encontrado:\n{script_path}")
                return

            # Cierra esta ventana ANTES de lanzar el juego.
            self.master.destroy() 
            
            # Lanza el juego como un proceso independiente.
            # Usamos sys.executable para asegurar que se use el mismo intérprete Python
            # y 'python -u' para salida sin buffer.
            cmd = [sys.executable, "-u", script_path] # Añadido "-u"
            flags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
            subprocess.Popen(cmd, cwd=script_dir, creationflags=flags)
            
            # Es importante salir del proceso actual después de destruir la ventana
            # para evitar que el script siga ejecutándose en segundo plano sin UI.
            sys.exit(0) # Añadir esta línea para una salida limpia.
            
        except Exception as e:
            messagebox.showerror("Error Fatal", f"Error al abrir juego:\n{e}")
            import traceback
            traceback.print_exc()

    # ========== FUNCIONES DEL MENÚ LATERAL (placeholders) ==========
    def show_stats(self):
        """Muestra estadísticas (placeholder)."""
        messagebox.showinfo("Estadísticas", "Próximamente: Estadísticas de juego")
        self.close_side_menu() # Cierra el menú lateral después de la acción

    def show_settings(self):
        """Muestra ajustes (placeholder)."""
        messagebox.showinfo("Ajustes", "Próximamente: Panel de configuración")
        self.close_side_menu()

    def show_about(self):
        """Muestra información del sistema."""
        messagebox.showinfo("Acerca de", "MIND - Sistema de Terapia Cognitiva\nVersión 1.0")
        self.close_side_menu()

    def show_clock(self):
        """
        Inicia el reloj/semáforo y cierra la ventana actual del menú.
        """
        print("Iniciando reloj_semaforo.py...")
        self._open_and_close('reloj_semaforo.py') # Llama al método unificado con la ruta directa

    def exit_application(self):
        """Cierra completamente la aplicación."""
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
            self.master.destroy()
            sys.exit()

# ========== EJECUCIÓN PRINCIPAL ==========
if __name__ == "__main__":
    root = tk.Tk()
    menu = GameMenu(root)
    
    # Asegura que todos los widgets se dibujen y tengan dimensiones antes de posicionar.
    # Esto es crucial para los botones de esquina.
    root.update_idletasks() 
    menu.position_corner_buttons() # Llama de nuevo para asegurar el posicionamiento final

    root.mainloop()