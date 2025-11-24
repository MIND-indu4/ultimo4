import tkinter as tk
from tkinter import messagebox
import sys
import math
from tkinter import Canvas, Frame, Label, Button
import subprocess
import os
import platform

# ========== CONFIGURACIÓN DE SISTEMA ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_OS = platform.system()

def get_system_font():
    return "Arial" if SYSTEM_OS == "Windows" else "DejaVu Sans"

def get_digital_font():
    # Intenta usar una fuente monoespaciada estándar en Linux si Digital-7 no está
    return "Courier" if SYSTEM_OS != "Windows" else "Consolas"

SYSTEM_FONT = get_system_font()
DIGITAL_FONT = get_digital_font()

class RoundedButton(tk.Canvas):
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

        # --- CORRECCIÓN PANTALLA COMPLETA ---
        self.root.update_idletasks()  # Importante para que Linux calcule bien
        
        if SYSTEM_OS == "Windows":
            self.root.attributes('-fullscreen', True)
        else:
            # Lógica para Raspberry Pi / Linux
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")
            # Esperamos 100ms para aplicar fullscreen
            self.root.after(100, lambda: self.root.attributes('-fullscreen', True))
            
        self.root.configure(bg='white')
        self.root.bind('<Escape>', lambda e: self.exit_app())

        # --- ESTADO DEL SISTEMA ---
        self.time_running = False
        self.current_time = 0
        self.initial_time = 0 
        self.cycle_count = 0
        self.scheduled_update_id = None

        # --- CONFIGURACIONES DE TIEMPOS ---
        self.phase_configs = {
            60: {"green": 30, "yellow": 10, "red": 20},
            600: {"green": 5 * 60, "yellow": 2 * 60, "red": 3 * 60},
            1200: {"green": 10 * 60, "yellow": 4 * 60, "red": 6 * 60},
            1800: {"green": 15 * 60, "yellow": 6 * 60, "red": 9 * 60}
        }

        self.current_phase_config = self.phase_configs.get(600, {"green": 300, "yellow": 120, "red": 180})
        self.green_time = self.current_phase_config["green"]
        self.yellow_time = self.current_phase_config["yellow"]
        self.red_time = self.current_phase_config["red"]

        # Estado LEDs físicos
        self.led_state = {"red": False, "yellow": False, "green": False}
        self.use_physical_leds = self.detect_physical_leds()

        # Colores Arcoíris
        self.rainbow_color_ranges = [
            (0, 15, '#FF0000'),
            (15, 20, '#FFD700'),
            (20, 40, '#008000'),
            (40, 45, '#FFD700'),
            (45, 55, '#0000CD'),
            (55, 60, '#1E90FF')
        ]

        self.create_widgets()
        self.update_display()

    def detect_physical_leds(self):
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
            print(f"✗ Error GPIO: {e}")
            return False

    def set_physical_led(self, color, state):
        if self.use_physical_leds:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.GPIO_PINS[color], state)
            except Exception: pass

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.root['bg'])
        main_frame.pack(fill='both', expand=True)

        # --- RELOJ ANALÓGICO ---
        # Ajustamos el tamaño del canvas para que entre bien en pantallas chicas también
        self.clock_canvas = tk.Canvas(main_frame, width=600, height=600, bg=self.root['bg'], highlightthickness=0)
        self.clock_canvas.place(relx=0.5, rely=0.35, anchor='center')
        self.draw_clock_background()

        # --- DISPLAY DIGITAL ---
        self.time_label = tk.Label(main_frame, text="00:00", font=(DIGITAL_FONT, 70, 'bold'), bg=self.root['bg'], fg='#00AA00')
        self.time_label.place(relx=0.5, rely=0.70, anchor='center')

        # --- SEMÁFORO VISUAL ---
        semaphore_frame = tk.Frame(main_frame, bg='#E0E0E0', bd=2, relief='ridge')
        semaphore_frame.place(relx=0.98, rely=0.02, anchor='ne')

        self.semaphore_canvas = tk.Canvas(semaphore_frame, width=80, height=200, bg='#E0E0E0', highlightthickness=0)
        self.semaphore_canvas.pack(padx=5, pady=5)

        self.led_visual = {
            "red": self.semaphore_canvas.create_oval(10, 10, 70, 60, fill='#FFAAAA', outline=''),
            "yellow": self.semaphore_canvas.create_oval(10, 75, 70, 125, fill='#FFFFAA', outline=''),
            "green": self.semaphore_canvas.create_oval(10, 140, 70, 190, fill='#AAFFAA', outline='')
        }

        # --- BOTONES ---
        buttons_center_frame = tk.Frame(main_frame, bg=self.root['bg'])
        buttons_center_frame.place(relx=0.5, rely=0.88, anchor='center')

        btn_width = 180
        btn_height = 60
        btn_rad = 20
        btn_pad = 8
        btn_font = (SYSTEM_FONT, 16, 'bold')

        self.btn_10min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#4CAF50', fg='white', activebackground='#66BB6A', text='⏱ 10 MINUTOS', command=lambda: self.set_quick_time(600), font=btn_font)
        self.btn_10min.grid(row=0, column=0, padx=10, pady=10)

        self.btn_20min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#FF9800', fg='white', activebackground='#FFB74D', text='⏱ 20 MINUTOS', command=lambda: self.set_quick_time(1200), font=btn_font)
        self.btn_20min.grid(row=0, column=1, padx=10, pady=10)

        self.btn_30min = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#F44336', fg='white', activebackground='#EF5350', text='⏱ 30 MINUTOS', command=lambda: self.set_quick_time(1800), font=btn_font)
        self.btn_30min.grid(row=0, column=2, padx=10, pady=10)
        
        self.start_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#2196F3', fg='white', activebackground='#42A5F5', text='▶ INICIAR', command=self.start_timer, font=btn_font)
        self.start_btn.grid(row=1, column=0, padx=10, pady=10)

        self.stop_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#9C27B0', fg='white', activebackground='#AB47BC', text='⏸ DETENER', command=self.stop_timer, font=btn_font)
        self.stop_btn.grid(row=1, column=1, padx=10, pady=10)

        self.reset_btn = RoundedButton(buttons_center_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#607D8B', fg='white', activebackground='#78909C', text='⟲ REINICIAR', command=self.reset_timer, font=btn_font)
        self.reset_btn.grid(row=1, column=2, padx=10, pady=10)

        self.btn_1min_corner = RoundedButton(main_frame, btn_width, btn_height, btn_rad, btn_pad, bg='#00BCD4', fg='white', activebackground='#26C6DA', text='⏱ 1 MINUTO', command=lambda: self.set_quick_time(60), font=btn_font)
        self.btn_1min_corner.place(relx=0.02, rely=0.98, anchor='sw')

        self.back_btn = RoundedButton(main_frame, 100, 40, 15, 5, bg='#757575', fg='white', activebackground='#9E9E9E', text='↩ VOLVER', command=self.go_back_to_main_menu, font=(SYSTEM_FONT, 14, 'bold'))
        self.back_btn.place(relx=0.98, rely=0.98, anchor='se')

    def draw_clock_background(self):
        center_x, center_y = 300, 300
        outer_radius = 250
        inner_circle_radius = 50

        self.clock_canvas.create_oval(center_x - outer_radius - 5, center_y - outer_radius - 5,
                                      center_x + outer_radius + 5, center_y + outer_radius + 5,
                                      outline='#CCCCCC', width=2)
        self.clock_canvas.create_oval(center_x - outer_radius, center_y - outer_radius,
                                      center_x + outer_radius, center_y + outer_radius,
                                      outline='#333333', width=10, tags="outer_border")

        self.clock_canvas.create_oval(center_x - inner_circle_radius, center_y - inner_circle_radius,
                                      center_x + inner_circle_radius, center_y + inner_circle_radius,
                                      fill='white', outline='#333333', width=5, tags="inner_circle")

        for i in range(0, 60, 5):
            angle = math.radians(90 - (i * 6))
            x_inner = center_x + (outer_radius - 40) * math.cos(angle)
            y_inner = center_y - (outer_radius - 40) * math.sin(angle)
            x_outer = center_x + (outer_radius - 10) * math.cos(angle)
            y_outer = center_y - (outer_radius - 10) * math.sin(angle)

            self.clock_canvas.create_line(x_inner, y_inner, x_outer, y_outer, width=6, capstyle='round', fill='#444444')

            x_num = center_x + (outer_radius - 70) * math.cos(angle)
            y_num = center_y - (outer_radius - 70) * math.sin(angle)

            num_color = '#222222'
            for start, end, color in self.rainbow_color_ranges:
                if start <= i < end or (end == 60 and i == 0):
                     num_color = color
                     break

            self.clock_canvas.create_text(x_num, y_num, text=str(i), font=(SYSTEM_FONT, 28, 'bold'), fill=num_color)

    def update_clock_visuals(self):
        self.clock_canvas.delete("dynamic_arc")
        if self.initial_time <= 0: return

        center_x, center_y = 300, 300
        outer_radius = 250
        bbox_arcs = (center_x - outer_radius, center_y - outer_radius, center_x + outer_radius, center_y + outer_radius)

        time_elapsed = self.initial_time - self.current_time
        progress_ratio = time_elapsed / self.initial_time if self.initial_time > 0 else 0
        degrees_to_cover = progress_ratio * 360

        current_phase, _ = self.get_current_phase()
        arc_color = {'green': '#33FF33', 'yellow': '#FFFF33', 'red': '#FF3333'}.get(current_phase, 'gray')

        self.clock_canvas.create_arc(bbox_arcs, start=90, extent=-degrees_to_cover, fill=arc_color, outline='', width=0, style='pieslice', tags="dynamic_arc")

    def update_semaphore_visual(self, active_color):
        colors_on = {"red": "#FF3333", "yellow": "#FFFF33", "green": "#33FF33"}
        colors_off = {"red": "#FFE0E0", "yellow": "#FFFFE0", "green": "#E0FFE0"}

        for color, led_id in self.led_visual.items():
            target = colors_on[color] if color == active_color else colors_off[color]
            self.semaphore_canvas.itemconfig(led_id, fill=target)
            self.set_physical_led(color, (color == active_color))

    def get_current_phase(self):
        total_cycle = self.green_time + self.yellow_time + self.red_time
        if total_cycle == 0 or self.current_time == 0: return None, 0

        elapsed = self.initial_time - self.current_time
        if elapsed < self.green_time: return "green", self.green_time - elapsed
        elif elapsed < self.green_time + self.yellow_time: return "yellow", (self.green_time + self.yellow_time) - elapsed
        else: return "red", self.initial_time - elapsed

    def update_display(self):
        if self.time_running and self.current_time > 0:
            self.current_time -= 1
            phase, _ = self.get_current_phase()
            self.update_semaphore_visual(phase)
            self.update_clock_visuals()

            if self.scheduled_update_id: self.root.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = self.root.after(1000, self.update_display)

        elif self.current_time == 0 and self.time_running:
            self.stop_timer()
            self.update_semaphore_visual(None)
            self.update_clock_visuals()
            return
        elif not self.time_running and self.scheduled_update_id:
            self.root.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = None

        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def set_quick_time(self, seconds):
        if not self.time_running:
            self.reset_timer_state()
            self.current_phase_config = self.phase_configs.get(seconds, self.phase_configs[60])
            self.current_time = seconds
            self.initial_time = seconds
            
            self.green_time = self.current_phase_config["green"]
            self.yellow_time = self.current_phase_config["yellow"]
            self.red_time = self.current_phase_config["red"]
            
            self.start_timer()

    def start_timer(self):
        if not self.time_running:
            if self.current_time == 0:
                total = self.current_phase_config["green"] + self.current_phase_config["yellow"] + self.current_phase_config["red"]
                self.current_time = total
                self.initial_time = total

            self.time_running = True
            self._toggle_buttons(running=True)
            self.update_display()

    def stop_timer(self):
        self.time_running = False
        if self.scheduled_update_id:
            self.root.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = None
        self._toggle_buttons(running=False)

    def _toggle_buttons(self, running):
        state_active = "normal" if not running else "disabled"
        color_active = lambda c: c if not running else "#BDBDBD"
        
        # Helper para configurar botones
        def config_btn(btn, color):
            btn.itemconfig(1, fill=color_active(color))
            if running:
                btn.unbind("<ButtonPress-1>")
                btn.unbind("<ButtonRelease-1>")
            else:
                btn.bind("<ButtonPress-1>", btn._on_press)
                btn.bind("<ButtonRelease-1>", btn._on_release)

        config_btn(self.btn_10min, "#4CAF50")
        config_btn(self.btn_20min, "#FF9800")
        config_btn(self.btn_30min, "#F44336")
        config_btn(self.btn_1min_corner, "#00BCD4")
        config_btn(self.reset_btn, "#607D8B")
        config_btn(self.start_btn, "#2196F3")
        
        # Boton detener es inverso
        stop_col = "#9C27B0" if running else "#BDBDBD"
        self.stop_btn.itemconfig(1, fill=stop_col)
        if running:
            self.stop_btn.bind("<ButtonPress-1>", self.stop_btn._on_press)
            self.stop_btn.bind("<ButtonRelease-1>", self.stop_btn._on_release)
        else:
            self.stop_btn.unbind("<ButtonPress-1>")
            self.stop_btn.unbind("<ButtonRelease-1>")

    def reset_timer_state(self):
        self.stop_timer()
        self.current_time = 0
        self.initial_time = 0
        self.update_display()
        self.update_semaphore_visual(None)
        self.update_clock_visuals()

    def reset_timer(self):
        self.reset_timer_state()

    def go_back_to_main_menu(self):
        if messagebox.askyesno("Volver", "¿Volver al menú de juegos?"):
            if self.scheduled_update_id: self.root.after_cancel(self.scheduled_update_id)
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except: pass
            
            self.root.destroy()
            
            # Búsqueda robusta del menú (en carpeta actual o arriba)
            path = os.path.join(SCRIPT_DIR, "menu_de_juegos.py")
            if not os.path.exists(path):
                 path = os.path.join(SCRIPT_DIR, "..", "menu_de_juegos.py")
            
            if os.path.exists(path):
                subprocess.Popen([sys.executable, path])
            else:
                messagebox.showerror("Error", f"Menú no encontrado:\n{path}")
            sys.exit(0)

    def exit_app(self):
        if messagebox.askyesno("Salir", "¿Cerrar aplicación?"):
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except: pass
            self.root.destroy()
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = SemaphoreClock(root)
    root.mainloop()