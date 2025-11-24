import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import platform # Necesario para detectar si es Raspberry o Windows
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ---------- Configuración de Fuente Multiplataforma ----------
def get_system_font():
    sistema = platform.system()
    if sistema == "Windows":
        return "Arial"
    else:
        # En Raspberry Pi/Linux, "DejaVu Sans" suele ser el estándar
        return "DejaVu Sans"

SYSTEM_FONT = get_system_font()

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
        
        # IMPORTANTE: En Linux, asegúrate de que las carpetas se llamen
        # exactamente 'nivel1', 'nivel2', etc. (minúsculas).
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
        # Sube un nivel (..) y entra a la carpeta del nivel
        path_to_level_script = os.path.join(current_menu_dir, '..', script_dir_name, script_to_run)
        
        # Normalizamos la ruta para evitar mezclas de / y \
        path_to_level_script = os.path.normpath(path_to_level_script)
        level_script_dir = os.path.dirname(path_to_level_script)

        if not os.path.exists(path_to_level_script):
            messagebox.showerror("Error", f"El archivo '{script_to_run}' no se encontró en:\n{path_to_level_script}\n\nVerifica mayúsculas/minúsculas en las carpetas.", parent=root)
            return

        # Ejecución compatible Windows/Linux
        subprocess.Popen([sys.executable, path_to_level_script], cwd=level_script_dir)
        root.destroy()
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al intentar abrir el nivel: {e}", parent=root)

def on_menu_click():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Sube dos niveles para encontrar el menú principal
    main_menu_path = os.path.join(current_script_dir, '..', '..', 'menu_de_juegos.py')
    main_menu_path = os.path.normpath(main_menu_path)

    if os.path.exists(main_menu_path):
        root.destroy()
        try:
            subprocess.Popen([sys.executable, main_menu_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el menú principal: {e}", parent=root)
    else:
        messagebox.showerror("Error", f"El archivo 'menu_de_juegos.py' no se encontró en:\n{main_menu_path}", parent=root)

# ---------- Ventana y escala ----------
root = tk.Tk()
root.title("Rompecabezas")
root.attributes("-fullscreen", True) 
root.resizable(False, False)

root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

root.update_idletasks() 
screen_width = root.winfo_width()
screen_height = root.winfo_height()

# --- Colores personalizados ---
main_color = "#FF69B4"       
hover_color = "#F06292"      
text_dark_color = "#333333"  
text_light_color = "#666666" 
menu_button_outline_color = "#4A6A80" 
menu_button_hover_bg = "#F8F8F8" 

# Calcular dimensiones
frame_width = int(screen_width * 0.9)
frame_height = int(screen_height * 0.9)
frame_x1 = (screen_width - frame_width) / 2
frame_y1 = (screen_height - frame_height) / 2
frame_x2 = frame_x1 + frame_width
frame_y2 = frame_y1 + frame_height
frame_radius = int(min(frame_width, frame_height) * 0.07) 

center_x = screen_width / 2
center_y = screen_height / 2

# Fuentes (Adaptadas dinámicamente según el sistema)
title_font = (SYSTEM_FONT, int(screen_height * 0.05), "bold")
subtitle_font = (SYSTEM_FONT, int(screen_height * 0.025))
button_text_font = (SYSTEM_FONT, int(screen_height * 0.022), "bold")

# Coordenadas
title_y    = frame_y1 + frame_height * 0.2
subtitle_y = frame_y1 + frame_height * 0.28
level_y    = center_y + frame_height * 0.05 
menu_y     = frame_y2 - frame_height * 0.15 

# Estilo de los botones
button_width = int(frame_width * 0.15)
button_height = int(frame_height * 0.08)
button_radius = int(min(button_width, button_height) * 0.3)

menu_button_width = int(frame_width * 0.25)
menu_button_height = int(frame_height * 0.12)
menu_button_radius = int(min(menu_button_width, menu_button_height) * 0.4)

level_spacing = int(frame_width * 0.25) 

# ---------- Función para crear botones ----------
def create_custom_button(canvas, x, y, text, command, is_menu=False):
    current_button_width = button_width
    current_button_height = button_height
    current_button_radius = button_radius
    
    if is_menu:
        current_bg_color = "white"
        current_fg_color = menu_button_outline_color
        current_outline_color = menu_button_outline_color
        current_outline_width = 2
        current_button_width = menu_button_width
        current_button_height = menu_button_height
        current_button_radius = menu_button_radius
        hover_fill_color = menu_button_hover_bg 
    else:
        current_bg_color = main_color
        current_fg_color = "white"
        current_outline_color = ""
        current_outline_width = 0
        hover_fill_color = hover_color 

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

create_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius, fill="white", outline="")

canvas.create_text(center_x, title_y,    text="Rompecabezas", font=title_font, fill=text_dark_color)
canvas.create_text(center_x, subtitle_y, text="¿Qué nivel quieres jugar?", font=subtitle_font, fill=text_light_color)

create_custom_button(canvas, center_x - level_spacing, level_y, "NIVEL 1", lambda: on_button_click(1))
create_custom_button(canvas, center_x,                  level_y, "NIVEL 2", lambda: on_button_click(2))
create_custom_button(canvas, center_x + level_spacing, level_y, "NIVEL 3", lambda: on_button_click(3))

create_custom_button(canvas, center_x,                  menu_y,  "MENÚ",    on_menu_click, is_menu=True)

root.mainloop()