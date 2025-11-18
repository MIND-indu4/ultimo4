import tkinter as tk
from tkinter import messagebox
import sys
import math
from tkinter import Canvas, Frame, Label, Button
from tkinter.ttk import Style
import subprocess # <--- ¡Nueva línea para importar subprocess!
import os # <--- ¡Nueva línea para importar os!

# Eliminamos la línea: import menu_de_juegos


class RoundedButton(tk.Canvas):
    # ... (tu código RoundedButton permanece igual) ...
    def __init__(self, parent, width, height, corner_radius, padding, bg, fg, activebackground, text, command, font, **kwargs):
        super().__init__(parent, width=width + 2 * padding, height=height + 2 * padding, highlightthickness=0, bg=parent['bg'], **kwargs)
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.padding = padding
        self.bg = bg
        self.fg = fg
        self.activebackground = activebackground
        self.text = text
        self.command = command
        self.font = font

        self.create_rounded_rectangle(padding, padding, width + padding, height + padding,
                                      corner_radius=corner_radius, fill=bg, outline="")
        self.text_id = self.create_text(width/2 + padding, height/2 + padding, text=text, fill=fg, font=font)

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def create_rounded_rectangle(self, x1, y1, x2, y2, corner_radius, **kwargs):
        points = [x1 + corner_radius, y1,
                  x2 - corner_radius, y1,
                  x2, y1 + corner_radius,
                  x2, y2 - corner_radius,
                  x2 - corner_radius, y2,
                  x1 + corner_radius, y2,
                  x1, y2 - corner_radius,
                  x1, y1 + corner_radius]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_press(self, event):
        self.itemconfig(1, fill=self.activebackground)

    def _on_release(self, event):
        self.itemconfig(1, fill=self.bg)
        if self.command:
            self.command()

class SemaphoreClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Semáforo Fullscreen")

        # --- PANTALLA COMPLETA ---
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='white')  # Fondo blanco
        self.root.bind('<Escape>', lambda e: self.exit_app())

        # --- ESTADO DEL SISTEMA ---
        self.time_running = False
        self.current_time = 0
        self.initial_time = 0 # Guarda el tiempo inicial para el cálculo de progreso
        self.cycle_count = 0
        self.scheduled_update_id = None # ID para after_cancel

        # --- CONFIGURACIONES DE TIMINGS POR FASE PARA CADA BOTÓN ---
        self.phase_configs = {
            60: {"green": 30, "yellow": 10, "red": 20},            # 1 minuto: 30V, 10A, 20R
            600: {"green": 5 * 60, "yellow": 2 * 60, "red": 3 * 60},    # 10 minutos: 5V, 2A, 3R
            1200: {"green": 10 * 60, "yellow": 4 * 60, "red": 6 * 60},  # 20 minutos: 10V, 4A, 6R
            1800: {"green": 15 * 60, "yellow": 6 * 60, "red": 9 * 60}   # 30 minutos: 15V, 6A, 9R
        }

        # Establecer la configuración de fase actual (se inicializa con la de 10 minutos por defecto)
        self.current_phase_config = self.phase_configs.get(600, {"green": 5 * 60, "yellow": 2 * 60, "red": 3 * 60}) # Configuración por defecto si no se encuentra 600

        # Acceso a los tiempos de fase a través de la configuración actual
        self.green_time = self.current_phase_config["green"]
        self.yellow_time = self.current_phase_config["yellow"]
        self.red_time = self.current_phase_config["red"]


        # Estado LEDs físicos (si están conectados)
        self.led_state = {"red": False, "yellow": False, "green": False}
        self.use_physical_leds = self.detect_physical_leds()

        # --- COLORES DEL ARCOÍRIS (para el reloj dinámico) ---
        self.rainbow_color_ranges = [
            (0, 15, '#FF0000'),    # Rojo
            (15, 20, '#FFD700'),   # Dorado (Amarillo)
            (20, 40, '#008000'),   # Verde
            (40, 45, '#FFD700'),   # Dorado (Amarillo)
            (45, 55, '#0000CD'),   # Azul Medio
            (55, 60, '#1E90FF')    # Azul Dodger
        ]

        # --- CREAR INTERFAZ ---
        self.create_widgets()
        # Llamamos a update_display una vez al inicio para configurar el estado inicial
        self.update_display()

    def detect_physical_leds(self):
        """Detecta LEDs físicos en Raspberry Pi"""
        try:
            import RPi.GPIO as GPIO
            self.GPIO_PINS = {"red": 17, "yellow": 27, "green": 22}
            GPIO.setmode(GPIO.BCM)
            for pin in self.GPIO_PINS.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, False)
            print("✓ LEDs físicos detectados")
            return True
        except ImportError:
            print("✗ Modo simulación (RPi.GPIO no encontrado)")
            return False
        except Exception as e:
            print(f"✗ Modo simulación (Error al configurar GPIO: {e})")
            return False

    def set_physical_led(self, color, state):
        """Controla LEDs físicos"""
        if self.use_physical_leds:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.GPIO_PINS[color], state)
            except Exception as e:
                pass

    def create_widgets(self):
        # --- FRAME PRINCIPAL ---
        main_frame = tk.Frame(self.root, bg=self.root['bg'])
        main_frame.pack(fill='both', expand=True)

        # --- RELOJ ANALÓGICO (Centro superior) ---
        self.clock_canvas = tk.Canvas(main_frame, width=600, height=600, bg=self.root['bg'], highlightthickness=0)
        self.clock_canvas.place(relx=0.5, rely=0.35, anchor='center') # Más arriba
        self.draw_clock_background()

        # ELIMINADO: Puntero del reloj

        # --- DISPLAY DIGITAL (Debajo del reloj analógico) ---
        self.time_label = tk.Label(main_frame, text="00:00", font=('Digital-7 Mono', 70, 'bold'), bg=self.root['bg'], fg='#00AA00') # Fuente más grande
        self.time_label.place(relx=0.5, rely=0.70, anchor='center') # Ajustado para que quede debajo del reloj

        # --- SEMÁFORO VISUAL (Esquina superior derecha) ---
        semaphore_frame = tk.Frame(main_frame, bg='#E0E0E0', bd=2, relief='ridge')
        semaphore_frame.place(relx=0.98, rely=0.02, anchor='ne')

        self.semaphore_canvas = tk.Canvas(semaphore_frame, width=80, height=200, bg='#E0E0E0', highlightthickness=0)
        self.semaphore_canvas.pack(padx=5, pady=5)

        self.led_visual = {
            "red": self.semaphore_canvas.create_oval(10, 10, 70, 60, fill='#FFAAAA', outline=''),
            "yellow": self.semaphore_canvas.create_oval(10, 75, 70, 125, fill='#FFFFAA', outline=''),
            "green": self.semaphore_canvas.create_oval(10, 140, 70, 190, fill='#AAFFAA', outline='')
        }

        # --- PANEL DE BOTONES PRINCIPAL (Parte inferior central) ---
        buttons_center_frame = tk.Frame(main_frame, bg=self.root['bg'])
        # Ajustamos la posición vertical para que tenga espacio para dos filas
        buttons_center_frame.place(relx=0.5, rely=0.88, anchor='center') 

        btn_width = 180 # Ancho aún más aumentado
        btn_height = 60 # Alto aún más aumentado
        btn_corner_radius = 20
        btn_padding = 8
        btn_font = ('Arial', 16, 'bold') # Fuente de botón más grande

        # FILA 0: BOTONES DE TIEMPO RÁPIDO (10, 20, 30 minutos)
        self.btn_10min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#4CAF50', fg='white', activebackground='#66BB6A', text='⏱ 10 MINUTOS', command=lambda: self.set_quick_time(600), font=btn_font)
        self.btn_10min.grid(row=0, column=0, padx=10, pady=10)

        self.btn_20min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#FF9800', fg='white', activebackground='#FFB74D', text='⏱ 20 MINUTOS', command=lambda: self.set_quick_time(1200), font=btn_font)
        self.btn_20min.grid(row=0, column=1, padx=10, pady=10)

        self.btn_30min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#F44336', fg='white', activebackground='#EF5350', text='⏱ 30 MINUTOS', command=lambda: self.set_quick_time(1800), font=btn_font)
        self.btn_30min.grid(row=0, column=2, padx=10, pady=10)
        
        # FILA 1: BOTONES DE CONTROL (1 Minuto, Iniciar, Detener, Reiniciar)
        if hasattr(self, 'btn_1min_placeholder'):
            self.btn_1min_placeholder.destroy()
        
        self.start_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#2196F3', fg='white', activebackground='#42A5F5', text='▶ INICIAR', command=self.start_timer, font=btn_font)
        self.start_btn.grid(row=1, column=0, padx=10, pady=10)

        self.stop_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#9C27B0', fg='white', activebackground='#AB47BC', text='⏸ DETENER', command=self.stop_timer, font=btn_font)
        self.stop_btn.grid(row=1, column=1, padx=10, pady=10)

        self.reset_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#607D8B', fg='white', activebackground='#78909C', text='⟲ REINICIAR', command=self.reset_timer, font=btn_font)
        self.reset_btn.grid(row=1, column=2, padx=10, pady=10) # Reiniciar en la fila 1, columna 2

        # El botón de "1 Minuto" sigue en su posición abajo a la izquierda, fuera de este grupo central.
        self.btn_1min_corner = RoundedButton(main_frame, btn_width, btn_height, btn_corner_radius, btn_padding, bg='#00BCD4', fg='white', activebackground='#26C6DA', text='⏱ 1 MINUTO', command=lambda: self.set_quick_time(60), font=btn_font)
        self.btn_1min_corner.place(relx=0.02, rely=0.98, anchor='sw') # Abajo izquierda

        # --- BOTÓN VOLVER (Abajo a la derecha) ---
        self.back_btn = RoundedButton(main_frame, 100, 40, 15, 5, bg='#757575', fg='white', activebackground='#9E9E9E', text='↩ VOLVER', command=self.go_back_to_main_menu, font=('Arial', 14, 'bold'))
        self.back_btn.place(relx=0.98, rely=0.98, anchor='se')


    def draw_clock_background(self):
        """Dibuja los elementos estáticos del reloj: borde, números, etc."""
        center_x, center_y = 300, 300
        outer_radius = 250
        inner_circle_radius = 50

        # Círculo exterior (borde)
        self.clock_canvas.create_oval(center_x - outer_radius - 5, center_y - outer_radius - 5,
                                      center_x + outer_radius + 5, center_y + outer_radius + 5,
                                      outline='#CCCCCC', width=2)
        self.clock_canvas.create_oval(center_x - outer_radius, center_y - outer_radius,
                                      center_x + outer_radius, center_y + outer_radius,
                                      outline='#333333', width=10, tags="outer_border")

        # Círculo blanco central
        self.clock_canvas.create_oval(center_x - inner_circle_radius, center_y - inner_circle_radius,
                                      center_x + inner_circle_radius, center_y + inner_circle_radius,
                                      fill='white', outline='#333333', width=5, tags="inner_circle")

        # Números y marcas cada 5 minutos
        for i in range(0, 60, 5):
            angle = math.radians(90 - (i * 6))

            # Línea de marca
            x_inner_mark = center_x + (outer_radius - 40) * math.cos(angle)
            y_inner_mark = center_y - (outer_radius - 40) * math.sin(angle)
            x_outer_mark = center_x + (outer_radius - 10) * math.cos(angle)
            y_outer_mark = center_y - (outer_radius - 10) * math.sin(angle)

            self.clock_canvas.create_line(x_inner_mark, y_inner_mark, x_outer_mark, y_outer_mark,
                                           width=6, capstyle='round', fill='#444444', tags="marks")

            # Número
            x_num = center_x + (outer_radius - 70) * math.cos(angle)
            y_num = center_y - (outer_radius - 70) * math.sin(angle)

            # Colores de los números (ajustado para que coincida con la imagen)
            num_color = '#222222'
            for start, end, color in self.rainbow_color_ranges:
                if start <= i < end or (end == 60 and i == 0): # El 0 es 60
                     num_color = color
                     break # Encontramos el color para este rango

            self.clock_canvas.create_text(x_num, y_num, text=str(i), font=('Arial', 28, 'bold'), fill=num_color, tags="numbers")

    def update_clock_visuals(self):
        """
        Actualiza el arco dinámico (segmento de tiempo transcurrido)
        y su color según la fase.
        """
        self.clock_canvas.delete("dynamic_arc") # Borrar el arco anterior

        if self.initial_time <= 0: # Si no hay tiempo establecido o ya terminó
            return

        center_x, center_y = 300, 300
        outer_radius = 250

        bbox_arcs = (center_x - outer_radius, center_y - outer_radius,
                     center_x + outer_radius, center_y + outer_radius)

        time_elapsed = self.initial_time - self.current_time

        # --- CÁLCULO PARA UNA SOLA VUELTA ---
        progress_ratio = time_elapsed / self.initial_time if self.initial_time > 0 else 0
        degrees_to_cover = progress_ratio * 360

        # Determinar el color del arco según la fase
        current_phase, _ = self.get_current_phase()
        arc_color = 'gray' # Color por defecto si no hay fase activa
        if current_phase == "green":
            arc_color = '#33FF33' # Verde vibrante
        elif current_phase == "yellow":
            arc_color = '#FFFF33' # Amarillo vibrante
        elif current_phase == "red":
            arc_color = '#FF3333' # Rojo vibrante

        self.clock_canvas.create_arc(bbox_arcs,
                                      start=90, # Empieza arriba (0 minutos en el dial, o el inicio del conteo)
                                      extent=-degrees_to_cover, # Extent negativo para sentido horario
                                      fill=arc_color, # Color dinámico del arco
                                      outline='',
                                      width=0,
                                      style='pieslice', # Para que sea un segmento desde el centro
                                      tags="dynamic_arc")

    def update_semaphore_visual(self, active_color):
        """Actualiza colores del semáforo visual (en la esquina)"""
        colors_on = {
            "red": "#FF3333",
            "yellow": "#FFFF33",
            "green": "#33FF33"
        }
        colors_off = {
            "red": "#FFE0E0",
            "yellow": "#FFFFE0",
            "green": "#E0FFE0"
        }

        for color, led_id in self.led_visual.items():
            current_fill = self.semaphore_canvas.itemcget(led_id, "fill")
            target_fill = colors_on[color] if color == active_color else colors_off[color]

            if current_fill != target_fill:
                self.semaphore_canvas.itemconfig(led_id, fill=target_fill)
                self.led_state[color] = (color == active_color)
                self.set_physical_led(color, (color == active_color))

    def get_current_phase(self):
        """Determina fase actual del semáforo (para LEDs físicos/visual)"""
        # Usamos las variables de tiempo de fase actuales
        total_cycle_time = self.green_time + self.yellow_time + self.red_time
        if total_cycle_time == 0 or self.current_time == 0:
            return None, 0

        # Calcular el tiempo transcurrido desde el inicio del temporizador actual
        time_elapsed_from_start = self.initial_time - self.current_time

        remaining_in_phase = 0
        current_phase = None

        # Determinar la fase en base al tiempo transcurrido
        if time_elapsed_from_start < self.green_time:
            current_phase = "green"
            remaining_in_phase = self.green_time - time_elapsed_from_start
        elif time_elapsed_from_start < self.green_time + self.yellow_time:
            current_phase = "yellow"
            remaining_in_phase = (self.green_time + self.yellow_time) - time_elapsed_from_start
        else: # Si el tiempo transcurrido es mayor o igual al verde + amarillo, estamos en rojo
            current_phase = "red"
            remaining_in_phase = self.initial_time - time_elapsed_from_start # Tiempo restante hasta el final

        return current_phase, remaining_in_phase

    def update_display(self):
        """Actualiza todos los displays y el reloj"""
        # print(f"DEBUG: update_display llamado. time_running={self.time_running}, current_time={self.current_time}")

        if self.time_running and self.current_time > 0:
            self.current_time -= 1
            # print(f"DEBUG: Tiempo actual decrementado a: {self.current_time}")

            phase, _ = self.get_current_phase()
            self.update_semaphore_visual(phase)
            self.update_clock_visuals()

            # Cancelar cualquier 'after' pendiente antes de programar uno nuevo
            if self.scheduled_update_id:
                self.root.after_cancel(self.scheduled_update_id)
                # print("DEBUG: after_cancel ejecutado.")
            
            self.scheduled_update_id = self.root.after(1000, self.update_display)
            # print(f"DEBUG: Programado próximo update_display (ID: {self.scheduled_update_id}) en 1000 ms.")

        elif self.current_time == 0 and self.time_running:
            print("DEBUG: Tiempo llegó a 0. Deteniendo temporizador.")
            self.stop_timer() # stop_timer ya llama a after_cancel
            self.update_semaphore_visual(None) # Apagar semáforo al finalizar
            self.update_clock_visuals() # Mostrar el reloj en estado final (vacío)
            return
        elif not self.time_running and self.scheduled_update_id:
            # Si no está corriendo pero hay un after pendiente, cancelarlo
            self.root.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = None
            # print("DEBUG: Cancelado after pendiente porque time_running es False.")


        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.time_label.config(text=time_str)

    def set_quick_time(self, seconds):
        """
        Establece tiempo rápido y comienza automáticamente,
        cargando la configuración de fase correspondiente.
        """
        print(f"DEBUG: set_quick_time llamado con {seconds} segundos.")
        if not self.time_running:
            self.reset_timer_state() # Resetear el estado interno (esto ya cancelará cualquier after)

            # Cargar la configuración de fases para el tiempo total seleccionado
            self.current_phase_config = self.phase_configs.get(seconds, self.phase_configs[60]) # Usar 1 min como fallback si se añadió
            
            # Asegurarse de que el tiempo total de las fases sume los 'seconds' elegidos
            # Esto es importante para el progreso del arco y el cálculo de fases
            total_config_time = self.current_phase_config["green"] + self.current_phase_config["yellow"] + self.current_phase_config["red"]
            if total_config_time != seconds:
                print(f"Advertencia: La suma de fases para {seconds} segundos no coincide con el total. Usando la suma de fases: {total_config_time}")
                self.current_time = total_config_time
            else:
                self.current_time = seconds

            self.green_time = self.current_phase_config["green"]
            self.yellow_time = self.current_phase_config["yellow"]
            self.red_time = self.current_phase_config["red"]
            
            self.initial_time = self.current_time
            self.cycle_count = 0 # Reiniciar el contador de ciclos

            minutes = self.current_time // 60
            seconds_disp = self.current_time % 60
            self.time_label.config(text=f"{minutes:02d}:{seconds_disp:02d}")

            self.update_clock_visuals() # Dibujar el arco en posición inicial
            phase, _ = self.get_current_phase()
            self.update_semaphore_visual(phase)

            self.start_timer()
        else:
            print("DEBUG: set_quick_time ignorado, el temporizador ya está corriendo.")

    def start_timer(self):
        """Inicia el temporizador"""
        print("DEBUG: start_timer llamado.")
        if not self.time_running:
            print("DEBUG: Temporizador NO está corriendo. Iniciando.")
            if self.current_time == 0:
                # Si no se ha seleccionado un tiempo rápido, usar la configuración actual (por defecto 10 min)
                # Esto es importante si el usuario presiona START sin antes elegir un tiempo rápido.
                total_default_time = self.current_phase_config["green"] + self.current_phase_config["yellow"] + self.current_phase_config["red"]
                self.current_time = total_default_time
                self.initial_time = total_default_time
                print(f"DEBUG: current_time era 0. Establecido a default de {total_default_time} segundos.")

            self.time_running = True
            
            # Desactivar botones de tiempo rápido y reiniciar
            self.btn_10min.itemconfig(1, fill="#BDBDBD")
            self.btn_10min.unbind("<ButtonPress-1>")
            self.btn_10min.unbind("<ButtonRelease-1>")

            self.btn_20min.itemconfig(1, fill="#BDBDBD")
            self.btn_20min.unbind("<ButtonPress-1>")
            self.btn_20min.unbind("<ButtonRelease-1>")

            self.btn_30min.itemconfig(1, fill="#BDBDBD")
            self.btn_30min.unbind("<ButtonPress-1>")
            self.btn_30min.unbind("<ButtonRelease-1>")
            
            # Desactivar el botón de 1 minuto de la esquina
            self.btn_1min_corner.itemconfig(1, fill="#BDBDBD")
            self.btn_1min_corner.unbind("<ButtonPress-1>")
            self.btn_1min_corner.unbind("<ButtonRelease-1>")

            self.reset_btn.itemconfig(1, fill="#BDBDBD")
            self.reset_btn.unbind("<ButtonPress-1>")
            self.reset_btn.unbind("<ButtonRelease-1>")

            self.start_btn.itemconfig(1, fill="#BDBDBD")
            self.start_btn.unbind("<ButtonPress-1>")
            self.start_btn.unbind("<ButtonRelease-1>")

            # Activar botón de detener
            self.stop_btn.itemconfig(1, fill="#9C27B0")
            self.stop_btn.bind("<ButtonPress-1>", self.stop_btn._on_press)
            self.stop_btn.bind("<ButtonRelease-1>", self.stop_btn._on_release)

            # Iniciar el ciclo de actualización
            self.update_display()
        else:
            print("DEBUG: Temporizador YA está corriendo. No se inicia de nuevo.")

    def stop_timer(self):
        """Detiene el temporizador"""
        print("DEBUG: stop_timer llamado.")
        self.time_running = False
        if self.scheduled_update_id:
            self.root.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = None
            print("DEBUG: after_cancel ejecutado en stop_timer.")

        # Activar botones de tiempo rápido y reiniciar
        self.btn_10min.itemconfig(1, fill="#4CAF50")
        self.btn_10min.bind("<ButtonPress-1>", self.btn_10min._on_press)
        self.btn_10min.bind("<ButtonRelease-1>", self.btn_10min._on_release)

        self.btn_20min.itemconfig(1, fill="#FF9800")
        self.btn_20min.bind("<ButtonPress-1>", self.btn_20min._on_press)
        self.btn_20min.bind("<ButtonRelease-1>", self.btn_20min._on_release)

        self.btn_30min.itemconfig(1, fill="#F44336")
        self.btn_30min.bind("<ButtonPress-1>", self.btn_30min._on_press)
        self.btn_30min.bind("<ButtonRelease-1>", self.btn_30min._on_release)
        
        # Activar el botón de 1 minuto de la esquina
        self.btn_1min_corner.itemconfig(1, fill="#00BCD4")
        self.btn_1min_corner.bind("<ButtonPress-1>", self.btn_1min_corner._on_press)
        self.btn_1min_corner.bind("<ButtonRelease-1>", self.btn_1min_corner._on_release)

        self.reset_btn.itemconfig(1, fill="#607D8B")
        self.reset_btn.bind("<ButtonPress-1>", self.reset_btn._on_press)
        self.reset_btn.bind("<ButtonRelease-1>", self.reset_btn._on_release)

        self.start_btn.itemconfig(1, fill="#2196F3")
        self.start_btn.bind("<ButtonPress-1>", self.start_btn._on_press)
        self.start_btn.bind("<ButtonRelease-1>", self.start_btn._on_release)

        # Desactivar botón de detener
        self.stop_btn.itemconfig(1, fill="#BDBDBD")
        self.stop_btn.unbind("<ButtonPress-1>")
        self.stop_btn.unbind("<ButtonRelease-1>")

    def reset_timer_state(self):
        """Resetea el estado interno del temporizador y actualiza visuales a estado inicial"""
        print("DEBUG: reset_timer_state llamado.")
        self.stop_timer() # Esto ya se encarga de cancelar cualquier after y resetear botones
        self.current_time = 0
        self.initial_time = 0
        self.cycle_count = 0
        self.update_display() # Actualizar display una vez para mostrar "00:00"
        self.update_semaphore_visual(None) # Apagar todos los LEDs del semáforo
        self.update_clock_visuals() # Asegura que el arcoíris se vacíe al reiniciar

        # Reestablecer la configuración de fase a un valor por defecto (ej. el de 10 min, o 1 min si se prefiere)
        self.current_phase_config = self.phase_configs.get(600, {"green": 5 * 60, "yellow": 2 * 60, "red": 3 * 60})
        self.green_time = self.current_phase_config["green"]
        self.yellow_time = self.current_phase_config["yellow"]
        self.red_time = self.current_phase_config["red"]

    def reset_timer(self):
        """Reinicia todo el sistema (llamando a reset_timer_state)"""
        print("DEBUG: reset_timer llamado.")
        self.reset_timer_state()

    def go_back_to_main_menu(self):
        """Cierra la ventana actual y abre el menu_de_juegos.py como un nuevo proceso."""
        print("DEBUG: Botón VOLVER presionado.")
        if messagebox.askyesno("Volver al Menú", "¿Deseas volver al menú de juegos?"):
            print("DEBUG: Usuario confirmó volver al menú.")
            if self.scheduled_update_id:
                self.root.after_cancel(self.scheduled_update_id)
                print("DEBUG: after_cancel ejecutado al volver al menú.")
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except ImportError:
                pass
            except Exception as e:
                print(f"Error al limpiar GPIO: {e}")
            
            self.root.destroy()  # Cierra la ventana actual del reloj
            print("DEBUG: Ventana del reloj destruida.")

            try:
                # Obtener la ruta del directorio actual donde está reloj_semaforo.py
                current_script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # LA MODIFICACIÓN ES AQUÍ:
                # Asumimos que 'menu_de_juegos.py' está en el mismo directorio que 'reloj_semaforo.py'
                main_menu_script_path = os.path.join(current_script_dir, 'menu_de_juegos.py')
                
                print(f"DEBUG: Intentando lanzar menu_de_juegos.py desde: {main_menu_script_path}")
                
                if not os.path.exists(main_menu_script_path):
                    messagebox.showerror("Error", f"El archivo menu_de_juegos.py no se encontró en la ruta esperada:\n{main_menu_script_path}")
                    sys.exit(1)

                # Lanza el menú principal como un nuevo proceso.
                # El directorio de trabajo actual (cwd) será el mismo donde está el script.
                cmd = [sys.executable, "-u", main_menu_script_path]
                flags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
                subprocess.Popen(cmd, cwd=current_script_dir, creationflags=flags) # Usar current_script_dir como cwd
                print("DEBUG: menu_de_juegos.py lanzado exitosamente.")
                
                sys.exit(0) # Salir limpiamente del proceso actual del reloj

            except Exception as e:
                print(f"ERROR: Fallo al intentar lanzar menu_de_juegos.py: {e}")
                messagebox.showerror("Error de Lanzamiento", f"No se pudo volver al menú de juegos:\n{e}")
                sys.exit(1) # Salir si falla el relanzamiento
        else:
            print("DEBUG: Usuario canceló volver al menú.")

    def exit_app(self):
        """Cierra la aplicación por completo (usada por Escape key y la 'X' de la ventana)"""
        print("DEBUG: exit_app llamado.")
        if messagebox.askyesno("Salir", "¿Deseas cerrar la aplicación completamente?"):
            if self.scheduled_update_id:
                self.root.after_cancel(self.scheduled_update_id)
                print("DEBUG: after_cancel ejecutado al salir.")
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except ImportError:
                pass
            except Exception as e:
                print(f"Error al limpiar GPIO: {e}")
            self.root.destroy()
            sys.exit(0) # Asegurar una salida limpia del script

def main():
    try:
        import tkinter as tk
    except ImportError:
        print("Error: Tkinter no está instalado")
        sys.exit(1)

    root = tk.Tk()
    root.configure(bg='white')
    app = SemaphoreClock(root)

    root.protocol("WM_DELETE_WINDOW", app.exit_app) 

    root.mainloop()

if __name__ == "__main__":
    main()