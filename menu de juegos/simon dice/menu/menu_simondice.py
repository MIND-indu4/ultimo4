import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ========== CONFIGURACIÓN DE RUTAS SEGURA (VERSIÓN CORREGIDA PARA SIMON DICE) ==========
def get_project_root_simondice():
    """
    Obtiene la ruta de la carpeta 'mind' que es la raíz del proyecto.
    Asume que menu_simondice.py está en 'mind/simon dice/menu/menu_simondice.py'
    """
    try:
        script_path = os.path.abspath(__file__)
        # script_path = C:\...\mind\simon dice\menu\menu_simondice.py
        
        # Subir 1 nivel: C:\...\mind\simon dice\menu
        current_menu_dir = os.path.dirname(script_path)
        
        # Subir 1 nivel: C:\...\mind\simon dice
        simon_dice_dir = os.path.dirname(current_menu_dir)
        
        # Subir 1 nivel: C:\...\mind\
        project_root = os.path.dirname(simon_dice_dir)
        
        return project_root
    except Exception as e:
        print(f"❌ ERROR en get_project_root_simondice: {e}")
        # En caso de error, puedes poner una ruta de fallback o re-lanzar la excepción
        messagebox.showerror("Error de Ruta", f"No se pudo determinar la raíz del proyecto para Simon Dice: {e}")
        sys.exit(1)


PROJECT_ROOT_SD = get_project_root_simondice()
print(f"✅ PROJECT_ROOT_SD (para Simon Dice): {PROJECT_ROOT_SD}")  # DEBUG

def get_safe_path_from_project_root(*path_parts):
    """Construye rutas seguras desde PROJECT_ROOT_SD (la carpeta 'mind')"""
    try:
        safe_path = os.path.join(PROJECT_ROOT_SD, *path_parts)
        safe_path = os.path.normpath(safe_path)
        safe_path = os.path.abspath(safe_path)
        return safe_path
    except Exception as e:
        print(f"❌ ERROR construyendo ruta: {e}")
        raise

# ========== FUNCIONES BÁSICAS ==========
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
    """Abre un nivel y cierra el menú"""
    try:
        # Asegúrate de que los niveles también se construyen desde la raíz del proyecto
        # y no desde PROJECT_ROOT_SD si este ya apunta a 'mind'.
        # Es decir, 'simon dice' debe ser parte de path_parts.
        
        levels = {
        1: ('simon dice', 'nivel1', 'nivel1.py'),
        2: ('simon dice', 'nivel2', 'nivel2.py'),
        3: ('simon dice', 'nivel3', 'nivel3.py')
        }
        
        if level not in levels:
            messagebox.showerror("Error", f"Nivel {level} no implementado.", parent=root)
            return
            
        # Usamos get_safe_path_from_project_root
        path_segments_to_level_script = levels[level]
        path_to_level_script = get_safe_path_from_project_root(*path_segments_to_level_script)
        level_script_dir = os.path.dirname(path_to_level_script)

        if not os.path.exists(path_to_level_script):
            messagebox.showerror("Error", f"Archivo de nivel no encontrado:\n{path_to_level_script}", parent=root)
            return

        # DESTRUIR ventana y lanzar nivel
        root.destroy()
        subprocess.Popen([sys.executable, path_to_level_script], cwd=level_script_dir)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir nivel: {e}", parent=root)

def on_menu_click():
    """Vuelve al menú principal y cierra este menú"""
    try:
        # Construye la ruta al menú principal desde la raíz del proyecto (la carpeta 'mind')
        # La ruta que queremos es: C:\...\mind\menu_de_juegos.py
        main_menu_path = get_safe_path_from_project_root('menu_de_juegos.py')
        print(f"DEBUG: Ruta al menú principal: {main_menu_path}") # Añadir este print

        main_menu_dir = os.path.dirname(main_menu_path) # <-- MUEVE ESTA LÍNEA AQUÍ

        if not os.path.exists(main_menu_path):
            messagebox.showerror("Error", f"Menú principal no encontrado:\n{main_menu_path}")
            print(f"DEBUG: Archivo no existe en: {main_menu_path}") # Añadir este print
            return

        # DESTRUIR ventana y lanzar menú principal
        root.destroy()
        flags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
        subprocess.Popen([sys.executable, main_menu_path], cwd=main_menu_dir, creationflags=flags)
        
    except Exception as e:
        messagebox.showerror("Error Fatal", f"No se pudo volver al menú:\n{e}")
        
def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)

# ========== INTERFAZ GRÁFICA ==========
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simon Dice")
    root.attributes("-fullscreen", True)
    root.resizable(False, False)
    root.bind("<Escape>", exit_fullscreen)

    # COLORES
    main_color = "#ff5757"
    hover_color = "#ff7d7d"
    menu_button_outline_color = "#cc4646"
    menu_button_hover_bg = "#ffebeb"

    # Canvas
    canvas = tk.Canvas(root, bg=main_color, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Dimensiones
    root.update_idletasks()
    screen_width = root.winfo_width()
    screen_height = root.winfo_height()

    frame_width = int(screen_width * 0.9)
    frame_height = int(screen_height * 0.9)
    frame_x1 = (screen_width - frame_width) / 2
    frame_y1 = (screen_height - frame_height) / 2
    frame_x2 = frame_x1 + frame_width
    frame_y2 = frame_y1 + frame_height
    frame_radius = int(min(frame_width, frame_height) * 0.07) 

    # Forma principal
    create_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius, fill="white", outline="")

    # Título
    center_x = screen_width / 2
    center_y = screen_height / 2
    canvas.create_text(center_x, frame_y1 + frame_height * 0.2, text="Simon Dice", font=("Georgia", 36, "bold"), fill="black")
    canvas.create_text(center_x, frame_y1 + frame_height * 0.28, text="¿Qué nivel quieres jugar?", font=("Arial", 18), fill="black")

    # Estilo de botones
    button_font = ("Arial", 16, "bold")
    button_width = int(frame_width * 0.15) 
    button_height = int(frame_height * 0.08) 
    button_radius = int(min(button_width, button_height) * 0.3)

    # Función para crear botón con forma personalizada
    def create_custom_button(canvas, x, y, text, command, is_menu=False):
        current_button_width = button_width
        current_button_height = button_height
        current_button_radius = button_radius

        if is_menu:
            current_button_width = int(frame_width * 0.25)
            current_button_height = int(frame_height * 0.12)
            current_button_radius = int(min(current_button_width, current_button_height) * 0.4) 

        btn_x1 = x - current_button_width / 2
        btn_y1 = y - current_button_height / 2
        btn_x2 = x + current_button_width / 2
        btn_y2 = y + current_button_height / 2

        bg_color = "white" if is_menu else main_color
        fg_color = menu_button_outline_color if is_menu else "white"
        outline_color = menu_button_outline_color if is_menu else ""
        outline_width = 2 if is_menu else 0

        button_shape = create_rounded_rectangle(canvas, btn_x1, btn_y1, btn_x2, btn_y2, current_button_radius,
                                                fill=bg_color, outline=outline_color, width=outline_width)
        button_text_id = canvas.create_text(x, y, text=text, font=button_font, fill=fg_color)

        def on_enter(event):
            canvas.itemconfig(button_shape, fill=menu_button_hover_bg if is_menu else hover_color)

        def on_leave(event):
            canvas.itemconfig(button_shape, fill=bg_color)
            canvas.itemconfig(button_text_id, fill=fg_color) 

        canvas.tag_bind(button_shape, "<Button-1>", lambda e: command())
        canvas.tag_bind(button_text_id, "<Button-1>", lambda e: command())
        canvas.tag_bind(button_shape, "<Enter>", on_enter)
        canvas.tag_bind(button_text_id, "<Enter>", on_enter)
        canvas.tag_bind(button_shape, "<Leave>", on_leave)
        canvas.tag_bind(button_text_id, "<Leave>", on_leave)

    # Botones de nivel
    level_button_y = center_y + frame_height * 0.05 
    level_spacing = int(frame_width * 0.25) 

    create_custom_button(canvas, center_x - level_spacing, level_button_y, "NIVEL 1", lambda: on_button_click(1))
    create_custom_button(canvas, center_x, level_button_y, "NIVEL 2", lambda: on_button_click(2))
    create_custom_button(canvas, center_x + level_spacing, level_button_y, "NIVEL 3", lambda: on_button_click(3))

    # Botón Menú
    menu_button_y = frame_y2 - frame_height * 0.15 
    create_custom_button(canvas, center_x, menu_button_y, "MENÚ", on_menu_click, is_menu=True)

    root.mainloop()