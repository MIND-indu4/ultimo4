import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ---------- Funciones auxiliares ----------
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
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
    return canvas.create_polygon(points, smooth=True, **kwargs)

def on_button_click(level):
    try:
        current_menu_dir = os.path.dirname(os.path.abspath(__file__))
        script_to_run = ""
        script_dir_name = ""
        if level == 1:
            script_dir_name = 'nivel1'
            script_to_run = 'nivel1.py'
        elif level == 2:
            script_dir_name = 'nivel2'
            script_to_run = 'nivel2.py'
        elif level == 3:
            script_dir_name = 'nivel3'
            script_to_run = 'nivel3.py'
        else:
            messagebox.showerror("Error", f"Nivel {level} no implementado.", parent=root)
            return
        
        # Ajuste de la ruta para que sea relativa al directorio del script
        path_to_level_script = os.path.join(current_menu_dir, '..', script_dir_name, script_to_run)
        level_script_dir = os.path.dirname(path_to_level_script)

        # Puedes mantener estos prints para depuración, pero los quito para el código final limpio
        # print(f"DEBUG(menu): Directorio actual del script de menu: {current_menu_dir}")
        # print(f"DEBUG(menu): Ruta calculada para {script_to_run}: {path_to_level_script}")
        # print(f"DEBUG(menu): Directorio de {script_to_run} para cwd: {level_script_dir}")
        # print(f"DEBUG(menu): ¿Existe {script_to_run} en esta ruta? {os.path.exists(path_to_level_script)}")
        # print(f"DEBUG(menu): ¿Existe el directorio de {script_to_run}? {os.path.exists(level_script_dir)}")

        if not os.path.exists(path_to_level_script):
            messagebox.showerror("Error", f"El archivo '{script_to_run}' no se encontró en la ruta esperada: {path_to_level_script}. Asegúrate de que el archivo y la carpeta existen.", parent=root)
            return

        subprocess.Popen([sys.executable, path_to_level_script], cwd=level_script_dir)
        root.destroy()
    except FileNotFoundError:
        messagebox.showerror("Error", f"Uno de los archivos necesarios no se encontró. Revisa la consola para más detalles.", parent=root)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al intentar abrir el nivel: {e}. Revisa la consola para más detalles.", parent=root)

def on_menu_click():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    main_menu_path = os.path.join(current_script_dir, '..', '..', 'menu_de_juegos.py')
    
    # print(f"DEBUG (on_menu_click): Directorio actual: {current_script_dir}")
    # print(f"DEBUG (on_menu_click): Ruta calculada para el menú principal: {main_menu_path}")

    if os.path.exists(main_menu_path):
        root.destroy()
        try:
            subprocess.Popen([sys.executable, main_menu_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el menú principal de juegos: {e}", parent=root)
    else:
        messagebox.showerror("Error", f"El archivo 'menu_de_juegos.py' no se encontró en la ruta esperada: {main_menu_path}", parent=root)

# ---------- Ventana y escala ----------
root = tk.Tk()
root.title("Rompecabezas")
root.attributes("-fullscreen", True) # Pone la ventana en pantalla completa
root.resizable(False, False)

# Vincular la tecla Escape para salir de pantalla completa
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# Asegurar que las dimensiones de la pantalla se capturen correctamente
root.update_idletasks() 
screen_width = root.winfo_width()
screen_height = root.winfo_height()

# --- Colores personalizados (NUEVOS para Rompecabezas) ---
main_color = "#FF69B4"       # Rosa Fucsia Profundo
hover_color = "#F06292"      # Rosa ligeramente más claro para el hover de los botones de nivel
text_dark_color = "#333333"  # Gris oscuro para títulos y textos principales
text_light_color = "#666666" # Gris medio para subtítulos
menu_button_outline_color = "#4A6A80" # Gris azulado oscuro para borde y texto del botón de menú
menu_button_hover_bg = "#F8F8F8" # Gris muy claro para el hover del botón de menú

# Calcular dimensiones y posiciones dinámicamente
# Usaremos un porcentaje de la pantalla en lugar de un escalado fijo para mayor flexibilidad
frame_width = int(screen_width * 0.9)
frame_height = int(screen_height * 0.9)
frame_x1 = (screen_width - frame_width) / 2
frame_y1 = (screen_height - frame_height) / 2
frame_x2 = frame_x1 + frame_width
frame_y2 = frame_y1 + frame_height
frame_radius = int(min(frame_width, frame_height) * 0.07) # Radio dinámico

center_x = screen_width / 2
center_y = screen_height / 2

# Título y subtítulo
# Fuentes (usando Arial como sustituto, considera instalar fuentes como Montserrat o Poppins)
title_font = ("Arial", int(screen_height * 0.05), "bold") # Tamaño de fuente adaptativo
subtitle_font = ("Arial", int(screen_height * 0.025))
button_text_font = ("Arial", int(screen_height * 0.022), "bold")

# Coordenadas y espaciado basados en el frame blanco
title_y    = frame_y1 + frame_height * 0.2
subtitle_y = frame_y1 + frame_height * 0.28
level_y    = center_y + frame_height * 0.05 # Ligeramente por debajo del centro vertical
menu_y     = frame_y2 - frame_height * 0.15 # Posición Y ajustada, más cerca del final del marco

# Estilo de los botones
button_width = int(frame_width * 0.15)
button_height = int(frame_height * 0.08)
button_radius = int(min(button_width, button_height) * 0.3)

menu_button_width = int(frame_width * 0.25)
menu_button_height = int(frame_height * 0.12)
menu_button_radius = int(min(menu_button_width, menu_button_height) * 0.4)

level_spacing = int(frame_width * 0.25) # Espaciado entre botones de nivel

# ---------- Función para crear botones (actualizada con los nuevos colores y lógica) ----------
def create_custom_button(canvas, x, y, text, command, is_menu=False):
    current_button_width = button_width
    current_button_height = button_height
    current_button_radius = button_radius
    
    # Definir colores para el estado normal
    if is_menu:
        current_bg_color = "white"
        current_fg_color = menu_button_outline_color
        current_outline_color = menu_button_outline_color
        current_outline_width = 2
        current_button_width = menu_button_width
        current_button_height = menu_button_height
        current_button_radius = menu_button_radius
        hover_fill_color = menu_button_hover_bg # Color de hover específico para menú
    else:
        current_bg_color = main_color
        current_fg_color = "white"
        current_outline_color = ""
        current_outline_width = 0
        hover_fill_color = hover_color # Color de hover específico para niveles

    btn_x1 = x - current_button_width / 2
    btn_y1 = y - current_button_height / 2
    btn_x2 = x + current_button_width / 2
    btn_y2 = y + current_button_height / 2

    button_shape = create_rounded_rectangle(canvas, btn_x1, btn_y1, btn_x2, btn_y2, current_button_radius,
                                            fill=current_bg_color, outline=current_outline_color, width=current_outline_width)
    button_text_id = canvas.create_text(x, y, text=text, font=button_text_font, fill=current_fg_color)

    def on_enter(event):
        canvas.itemconfig(button_shape, fill=hover_fill_color)

    def on_leave(event):
        canvas.itemconfig(button_shape, fill=current_bg_color)

    canvas.tag_bind(button_shape, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_text_id, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_shape, "<Enter>", on_enter)
    canvas.tag_bind(button_text_id, "<Enter>", on_enter)
    canvas.tag_bind(button_shape, "<Leave>", on_leave)
    canvas.tag_bind(button_text_id, "<Leave>", on_leave)

# ---------- Crear interfaz ----------
canvas = tk.Canvas(root, bg=main_color, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Crear la forma principal (rectángulo redondeado blanco)
create_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius, fill="white", outline="")

# Textos centrados
canvas.create_text(center_x, title_y,    text="Rompecabezas", font=title_font, fill=text_dark_color)
canvas.create_text(center_x, subtitle_y, text="¿Qué nivel quieres jugar?", font=subtitle_font, fill=text_light_color)

# Botones de nivel
create_custom_button(canvas, center_x - level_spacing, level_y, "NIVEL 1", lambda: on_button_click(1))
create_custom_button(canvas, center_x,                  level_y, "NIVEL 2", lambda: on_button_click(2))
create_custom_button(canvas, center_x + level_spacing, level_y, "NIVEL 3", lambda: on_button_click(3))

# Botón de Menú
create_custom_button(canvas, center_x,                  menu_y,  "MENÚ",    on_menu_click, is_menu=True)

root.mainloop()