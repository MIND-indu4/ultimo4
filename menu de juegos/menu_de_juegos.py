import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading

# --- EXTENSIÓN DE CANVAS ---
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
# --- FIN DE EXTENSIÓN ---

class GameMenu:
    def __init__(self, master):
        self.master = master
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # === PANTALLA COMPLETA CON FONDO AMARILLO FORZADO ===
        master.attributes("-fullscreen", True)
        master.bind("<Escape>", self.toggle_fullscreen)
        
        # OBTENER DIMENSIONES REALES
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.base_width = 1000
        self.base_height = 800
        self.scale = min(self.screen_width / self.base_width, self.screen_height / self.base_height)
        
        # === FORZAR COLOR DE FONDO EN TODOS LOS ELEMENTOS ===
        self.yellow_bg = "#FFDE59"
        self.white_frame_bg = "#FFFFFF"
        self.text_color = "#333333"
        self.red_border = "#FF4B4B"
        self.pink_border = "#FF69B4"
        self.green_border = "#4CAF50"
        self.blue_border = "#00BFFF"
        
        # Aplicar color amarillo al root y forzar no sobreescritura por tema del sistema
        master.config(bg=self.yellow_bg)
        master.option_add("*Background", self.yellow_bg)  # Forzar en todos los widgets
        
        self.icon_paths = {
            "simon": "simondice.png", "puzzle": "rompecabezas.png",
            "math": "mate.png", "tea": "TEAyudo.png",
            "menu": "menu.png", "close": "cerrar.png",
        }
        self.icons = {}
        
        # CREAR PLACEHOLDERS CON COLORES CORRECTOS
        self.create_all_placeholders()
        self.load_icons()
        self.create_widgets()

    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.master.attributes("-fullscreen")
        self.master.attributes("-fullscreen", not is_fullscreen)
        if not is_fullscreen:
            self.master.after(100, self.position_corner_buttons)

    def create_all_placeholders(self):
        """Crea placeholders con los COLORES CORRECTOS de cada juego."""
        scaled_size = int(140 * self.scale)
        # COLORES ESPECÍFICOS para cada placeholder (igual que los bordes)
        self.create_placeholder_icon("simondice.png", scaled_size, (255, 0, 0), "S")      # ROJO
        self.create_placeholder_icon("rompecabezas.png", scaled_size, (255, 105, 180), "P") # ROSA
        self.create_placeholder_icon("mate.png", scaled_size, (0, 128, 0), "M")            # VERDE
        self.create_placeholder_icon("TEAyudo.png", scaled_size, (0, 191, 255), "T")       # AZUL
        small_size = int(40 * self.scale)
        self.create_placeholder_icon("menu.png", small_size, (0, 0, 0), "☰")
        self.create_placeholder_icon("cerrar.png", small_size, (255, 0, 0), "✕")

    def create_placeholder_icon(self, filename_relative, size, color, text):
        """Crea placeholder con COLOR EXACTO especificado."""
        full_path = os.path.join(self.script_dir, filename_relative)
        
        if not os.path.exists(full_path):
            print(f"Creando placeholder: {full_path}")
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", int(size[0]*0.4))
            except IOError:
                font = ImageFont.load_default()
            
            if text in ["☰", "✕"]:
                font_size = int(size[0]*0.7)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0,0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text(((size[0] - text_width) / 2, (size[1] - text_height) / 2), 
                         text, font=font, fill=color)
            else:
                # DIBUJAR RECTÁNGULO REDONDEADO CON COLOR EXACTO DEL JUEGO
                draw.rounded_rectangle((0, 0, size[0], size[1]), radius=size[0]//4, fill=color)
                
                text_font_size = int(size[0]*0.6)
                try:
                    font_game = ImageFont.truetype("arial.ttf", text_font_size)
                except IOError:
                    font_game = ImageFont.load_default()
                
                bbox = draw.textbbox((0,0), text, font=font_game)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text(((size[0] - text_width) / 2, (size[1] - text_height) / 2 - 5), 
                         text, font=font_game, fill=(255,255,255))
            
            img.save(full_path)
            print(f"✓ Placeholder creado: {full_path}")

    def load_icons(self):
        """Carga iconos con tamaño ESCALADO."""
        scaled_game_size = int(140 * self.scale)
        scaled_small_size = int(40 * self.scale)
        
        for name, filename in self.icon_paths.items():
            full_path = os.path.join(self.script_dir, filename)
            
            try:
                print(f"Cargando icono: {full_path}")
                img = Image.open(full_path)
                
                if name in ["menu", "close"]:
                    img = img.resize((scaled_small_size, scaled_small_size), Image.LANCZOS)
                else:
                    img = img.resize((scaled_game_size, scaled_game_size), Image.LANCZOS)
                
                self.icons[name] = ImageTk.PhotoImage(img)
                print(f"✓ Icono '{name}' cargado correctamente")
                
            except Exception as e:
                print(f"✗ Error cargando {full_path}: {e}")
                self.icons[name] = None

    def create_widgets(self):
        """Crea widgets con dimensiones ESCALADAS y COLORES CORRECTOS."""
        margin = int(40 * self.scale)
        
        # === CANVAS PRINCIPAL CON FONDO AMARILLO FORZADO ===
        self.main_canvas = tk.Canvas(self.master, bg=self.yellow_bg, highlightthickness=0, bd=0)
        self.main_canvas.pack(fill="both", expand=True, padx=margin, pady=margin)

        canvas_width = self.screen_width - 2 * margin
        canvas_height = self.screen_height - 2 * margin
        self.round_rect_radius = int(40 * self.scale)

        # === RECTÁNGULO BLANCO INTERIOR ===
        self.main_canvas.create_rounded_rectangle(0, 0, canvas_width, canvas_height,
                                                  radius=self.round_rect_radius,
                                                  fill=self.white_frame_bg, outline="", width=0)

        # Título con fuente escalada
        title_font_size = int(28 * self.scale)
        title_label = tk.Label(self.main_canvas, text="Seleccione una actividad",
                               font=("Arial", title_font_size, "bold"),
                               fg=self.text_color,
                               bg=self.white_frame_bg)
        title_y = int(90 * self.scale)
        self.main_canvas.create_window(canvas_width / 2, title_y, window=title_label, anchor="center")

        # Frame de botones
        game_buttons_frame = tk.Frame(self.main_canvas, bg=self.white_frame_bg)
        buttons_y = canvas_height / 2 + int(50 * self.scale)
        self.main_canvas.create_window(canvas_width / 2, buttons_y, 
                                      window=game_buttons_frame, anchor="center")

        # Dimensiones escaladas
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
        self.create_game_button(game_buttons_frame, "TEAayudo", self.icons.get("tea"), 
                               self.run_game4, self.blue_border, 1, 1, button_dimensions, pad)

        # Botones de esquina
        if self.icons.get("menu"):
            self.menu_btn = tk.Button(self.master, image=self.icons["menu"], command=self.show_menu,
                                      bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
            self.menu_btn.place(x=0, y=0)

        if self.icons.get("close"):
            self.close_btn = tk.Button(self.master, image=self.icons["close"], command=self.exit_application,
                                       bd=0, bg=self.yellow_bg, activebackground=self.yellow_bg, relief="flat")
        else:
            self.close_btn = tk.Button(self.master, text="✕", command=self.exit_application,
                                    font=("Arial", int(18 * self.scale), "bold"), fg="#D32F2F", bg=self.yellow_bg,
                                    activebackground=self.yellow_bg, bd=0, padx=10, pady=5)
        self.close_btn.place(x=0, y=0)
        
        self.master.after(100, self.position_corner_buttons)

    def create_game_button(self, parent, text, icon_image, command, border_color, row, col, dimensions, pad):
        """Crea botón de juego ESCALADO con COLORES CORRECTOS."""
        frame_wrapper = tk.Frame(parent, bg=self.white_frame_bg)  # FONDO BLANCO
        frame_wrapper.grid(row=row, column=col, padx=pad, pady=pad)

        button_canvas = tk.Canvas(frame_wrapper, width=dimensions["width"], height=dimensions["height"],
                                  bg=self.white_frame_bg, highlightthickness=0)
        button_canvas.pack()

        # Dibujar sombra y rectángulo con grosor escalado
        shadow_offset = int(8 * self.scale)
        radius = int(30 * self.scale)
        button_canvas.create_rounded_rectangle(shadow_offset, shadow_offset, 
                                            dimensions["width"]+shadow_offset, dimensions["height"]+shadow_offset,
                                            radius=radius, fill="#E0E0E0", outline="", width=0)
        button_canvas.create_rounded_rectangle(0, 0, dimensions["width"], dimensions["height"],
                                            radius=radius, fill=self.white_frame_bg, outline=border_color, width=int(4 * self.scale))

        if icon_image:
            icon_label = tk.Label(button_canvas, image=icon_image, bg=self.white_frame_bg)
            icon_y = dimensions["height"] / 2 - int(25 * self.scale)
            button_canvas.create_window(dimensions["width"] / 2, icon_y, window=icon_label, anchor="center")
            icon_label.bind("<Button-1>", lambda e: command())
        else:
            placeholder_label = tk.Label(button_canvas, text="[ICON]", font=("Arial", int(12 * self.scale), "bold"), 
                                       bg=self.white_frame_bg, fg=border_color)
            button_canvas.create_window(dimensions["width"] / 2, dimensions["height"] / 2 - int(25 * self.scale), 
                                      window=placeholder_label, anchor="center")
            placeholder_label.bind("<Button-1>", lambda e: command())

        # Texto con fuente escalada
        text_font_size = int(16 * self.scale)
        text_label = tk.Label(button_canvas, text=text, font=("Arial", text_font_size, "bold"), 
                            fg=self.text_color, bg=self.white_frame_bg)
        text_y = dimensions["height"] / 2 + int(65 * self.scale)
        button_canvas.create_window(dimensions["width"] / 2, text_y, window=text_label, anchor="center")
        text_label.bind("<Button-1>", lambda e: command())

        button_canvas.bind("<Button-1>", lambda e: command())
        button_canvas.bind("<Enter>", lambda e: self.on_enter(e, button_canvas, border_color))
        button_canvas.bind("<Leave>", lambda e: self.on_leave(e, button_canvas, border_color))

    def on_enter(self, event, widget_canvas, original_border_color):
        widget_canvas.itemconfig(widget_canvas.find_all()[1], outline="black", width=int(5 * self.scale))
        widget_canvas.config(cursor="hand2")

    def on_leave(self, event, widget_canvas, original_border_color):
        widget_canvas.itemconfig(widget_canvas.find_all()[1], outline=original_border_color, width=int(4 * self.scale))
        widget_canvas.config(cursor="")

    def run_game1(self):
        target_script_path = os.path.join(self.script_dir, "simon dice", "menu", "menu_simondice.py")
        self.execute_game_and_wait(target_script_path)

    def run_game2(self):
        target_script_path = os.path.join(self.script_dir, "rompecabezas", "menu", "menu_rompecabezas.py")
        self.execute_game_and_wait(target_script_path)

    def run_game3(self):
        messagebox.showinfo("Juego", "Iniciando Matematicas...")

    def run_game4(self):
        messagebox.showinfo("Juego", "Iniciando TEAayuda...")

    def execute_game_and_wait(self, script_path):
        """Ejecuta un juego y restaura el menú al terminar."""
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Archivo no encontrado:\n{script_path}")
            return
        
        print(f"Ejecutando: {script_path}")
        self.master.withdraw()
        
        def wait_for_game():
            try:
                process = subprocess.Popen([sys.executable, script_path])
                process.wait()
                print(f"Juego terminado: {script_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error ejecutando juego: {e}")
            finally:
                self.master.after(0, self.restore_menu)
        
        threading.Thread(target=wait_for_game, daemon=True).start()
    
    def restore_menu(self):
        """Restaura el menú principal."""
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()
        print("Menú restaurado")

    def show_menu(self):
        messagebox.showinfo("Menú", "Abrir menú de opciones (ej. Ajustes, Acerca de...)")

    def exit_application(self):
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
            self.master.destroy()
            sys.exit()

    def position_corner_buttons(self):
        """Ajusta la posición de los botones de esquina ESCALADA."""
        button_padding = int(35 * self.scale)
        self.master.update_idletasks()
        
        if hasattr(self, 'menu_btn'):
            self.menu_btn.place(x=button_padding, y=button_padding)

        if hasattr(self, 'close_btn'):
            window_width = self.master.winfo_width()
            btn_width = self.close_btn.winfo_width()
            x_pos = window_width - btn_width - button_padding
            self.close_btn.place(x=x_pos, y=button_padding)


if __name__ == "__main__":
    root = tk.Tk()
    menu = GameMenu(root)
    root.mainloop()