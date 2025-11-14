import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont # Asegúrate de importar ImageFont

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
        # Ruta del directorio actual del script de menú (MIND/simondice/menu/)
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
            script_dir_name = 'nivel3' # Preparado para un futuro Nivel 3
            script_to_run = 'nivel3.py'
        else:
            messagebox.showerror("Error", f"Nivel {level} no implementado.", parent=root)
            return

        # Ajuste de la ruta para que sea relativa al directorio del script
        # Subimos un nivel (..) y luego entramos al directorio del nivel
        path_to_level_script = os.path.join(current_menu_dir, '..', script_dir_name, script_to_run)
        level_script_dir = os.path.dirname(path_to_level_script)

        print(f"DEBUG(menu): Directorio actual del script de menu: {current_menu_dir}")
        print(f"DEBUG(menu): Ruta calculada para {script_to_run}: {path_to_level_script}")
        print(f"DEBUG(menu): Directorio de {script_to_run} para cwd: {level_script_dir}")
        print(f"DEBUG(menu): ¿Existe {script_to_run} en esta ruta? {os.path.exists(path_to_level_script)}")
        print(f"DEBUG(menu): ¿Existe el directorio de {script_to_run}? {os.path.exists(level_script_dir)}")

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
    """
    Cierra la ventana actual (menú de Simon Dice) y abre el menú principal de juegos.
    Asume que 'menu_de_juegos.py' está en la carpeta 'MIND/'
    (el directorio padre del directorio 'simondice').
    """
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # La ruta esperada es: current_script_dir (menu/) -> .. (simondice/) -> .. (MIND/) -> menu_de_juegos.py
    main_menu_path = os.path.join(current_script_dir, '..', '..', 'menu_de_juegos.py')

    print(f"DEBUG (on_menu_click): Directorio actual: {current_script_dir}")
    print(f"DEBUG (on_menu_click): Ruta calculada para el menú principal: {main_menu_path}")

    if os.path.exists(main_menu_path):
        root.destroy() # Cierra la ventana actual (menú de Simon Dice)
        try:
            subprocess.Popen([sys.executable, main_menu_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el menú principal de juegos: {e}", parent=root)
    else:
        messagebox.showerror("Error", f"El archivo 'menu_de_juegos.py' no se encontró en la ruta esperada: {main_menu_path}", parent=root)

# Función para salir de pantalla completa
def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)


# Configuración de la ventana principal
root = tk.Tk()
root.title("Simon Dice")
root.attributes("-fullscreen", True) # Pone la ventana en pantalla completa
root.resizable(False, False)

# Vincular la tecla Escape para salir de pantalla completa
root.bind("<Escape>", exit_fullscreen)

# --- Colores personalizados ---
main_color = "#ff5757" # Rojo rosado vibrante como color principal
hover_color = "#ff7d7d" # Un tono más claro para el hover
menu_button_outline_color = "#cc4646" # Un tono más oscuro para el borde del botón de menú
menu_button_hover_bg = "#ffebeb" # Un tono muy claro para el hover del botón de menú

# Crear un canvas para el fondo y las formas personalizadas
canvas = tk.Canvas(root, bg=main_color, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Capturar las dimensiones de la pantalla después de que la ventana esté en pantalla completa
root.update_idletasks() # Asegura que winfo_width/height reflejen el tamaño real
screen_width = root.winfo_width()
screen_height = root.winfo_height()

# Calcular las dimensiones y posiciones del rectángulo redondeado principal
# Usaremos un 90% del ancho y un 90% del alto de la pantalla para el marco blanco
frame_width = int(screen_width * 0.9)
frame_height = int(screen_height * 0.9)
frame_x1 = (screen_width - frame_width) / 2
frame_y1 = (screen_height - frame_height) / 2
frame_x2 = frame_x1 + frame_width
frame_y2 = frame_y1 + frame_height
frame_radius = int(min(frame_width, frame_height) * 0.07) # Radio dinámico

# Crear la forma principal (rectángulo redondeado blanco)
create_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius, fill="white", outline="")

# Centro del marco blanco para posicionar elementos
center_x = screen_width / 2
center_y = screen_height / 2

# Título
canvas.create_text(center_x, frame_y1 + frame_height * 0.2, text="Simon Dice", font=("Georgia", 36, "bold"), fill="black")
canvas.create_text(center_x, frame_y1 + frame_height * 0.28, text="¿Qué nivel quieres jugar?", font=("Arial", 18), fill="black")

# Estilo de los botones (ajustados para coincidir con tu imagen)
button_font = ("Arial", 16, "bold")
# Dimensiones de los botones relativas al tamaño del marco
# HE REDUCIDO EL PORCENTAJE DEL ANCHO Y EL ALTO PARA HACERLOS MÁS PEQUEÑOS
button_width = int(frame_width * 0.15)  # Antes 0.2, ahora más pequeño
button_height = int(frame_height * 0.08) # Antes 0.1, ahora más pequeño
button_radius = int(min(button_width, button_height) * 0.3)

# Función para crear un botón con forma personalizada y asociar eventos
def create_custom_button(canvas, x, y, text, command, is_menu=False):
    # Definir el tamaño y radio del botón
    current_button_width = button_width
    current_button_height = button_height
    current_button_radius = button_radius

    if is_menu:
        # El botón de menú es un poco más grande
        current_button_width = int(frame_width * 0.25)
        current_button_height = int(frame_height * 0.12)
        current_button_radius = int(min(current_button_width, current_button_height) * 0.4) # Mayor radio para el botón de menú

    btn_x1 = x - current_button_width / 2
    btn_y1 = y - current_button_height / 2
    btn_x2 = x + current_button_width / 2
    btn_y2 = y + current_button_height / 2

    # Definir colores para el estado normal
    if is_menu:
        bg_color = "white"
        fg_color = menu_button_outline_color # Color de texto del menú
        outline_color = menu_button_outline_color
        outline_width = 2
    else:
        bg_color = main_color
        fg_color = "white" # Texto blanco para los botones de nivel
        outline_color = ""
        outline_width = 0

    button_shape = create_rounded_rectangle(canvas, btn_x1, btn_y1, btn_x2, btn_y2, current_button_radius,
                                            fill=bg_color, outline=outline_color, width=outline_width)

    button_text_id = canvas.create_text(x, y, text=text, font=button_font, fill=fg_color)

    def on_enter(event):
        if is_menu:
            canvas.itemconfig(button_shape, fill=menu_button_hover_bg)
        else:
            canvas.itemconfig(button_shape, fill=hover_color)

    def on_leave(event):
        canvas.itemconfig(button_shape, fill=bg_color)
        canvas.itemconfig(button_text_id, fill=fg_color) # Asegura que el texto vuelva a su color original

    canvas.tag_bind(button_shape, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_text_id, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_shape, "<Enter>", on_enter)
    canvas.tag_bind(button_text_id, "<Enter>", on_enter)
    canvas.tag_bind(button_shape, "<Leave>", on_leave)
    canvas.tag_bind(button_text_id, "<Leave>", on_leave)

# Coordenadas y espaciado de los botones de Nivel
# Posicionamos los botones de nivel en el centro vertical del marco blanco
# y horizontalmente distribuidos
level_button_y = center_y + frame_height * 0.05 # Ligeramente por debajo del centro vertical
# HE AUMENTADO EL PORCENTAJE DEL ESPACIADO PARA SEPARAR MÁS LOS BOTONES
level_spacing = int(frame_width * 0.25) # Antes 0.2, ahora más separado

create_custom_button(canvas, center_x - level_spacing, level_button_y, "NIVEL 1", lambda: on_button_click(1))
create_custom_button(canvas, center_x, level_button_y, "NIVEL 2", lambda: on_button_click(2))
create_custom_button(canvas, center_x + level_spacing, level_button_y, "NIVEL 3", lambda: on_button_click(3))

# Botón de Menú
menu_button_y = frame_y2 - frame_height * 0.15 # Posición Y ajustada, más cerca del final del marco
create_custom_button(canvas, center_x, menu_button_y, "MENÚ", on_menu_click, is_menu=True)

root.mainloop()