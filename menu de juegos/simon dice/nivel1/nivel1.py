import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import sys
import subprocess
import threading
import platform

# ========== INICIALIZACIÓN DE AUDIO Y RUTAS ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Intento de importar pygame y gTTS con manejo de errores para RPi
try:
    import pygame.mixer
    from gtts import gTTS
except ImportError as e:
    print(f"ERROR CRÍTICO: Falta librería de audio: {e}")
    print("En Raspberry Pi ejecuta: pip install pygame gTTS")

def get_system_font():
    return "Arial" if platform.system() == "Windows" else "DejaVu Sans"

SYSTEM_FONT = get_system_font()

class SilabasGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Sílabas")

        # ✅ Pantalla completa y escala
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 800
        base_height = 600
        self.scale = min(screen_width / base_width, screen_height / base_height)

        master.attributes("-fullscreen", True)
        master.configure(bg="#FF5757")

        # Salida de emergencia
        master.bind("<Escape>", lambda e: self.go_to_menu())

        self._apply_scaling()

        # Configuración de palabras (Revisa nombres de archivo en Linux!)
        self.all_words_data = [
            {"word": "ASUSTADO", "syllables": ["A", "SUS", "TA", "DO"], "image": "asustado.png"},
            {"word": "CAMINAR", "syllables": ["CA", "MI", "NAR"], "image": "caminar.png"},
            {"word": "COCINA", "syllables": ["CO", "CI", "NA"], "image": "cocina.png"},
            {"word": "COMER", "syllables": ["CO", "MER"], "image": "comer.png"},
            {"word": "DORMIR", "syllables": ["DOR", "MIR"], "image": "dormir.png"},
            {"word": "FELIZ", "syllables": ["FE", "LIZ"], "image": "feliz.png"},
            {"word": "NADAR", "syllables": ["NA", "DAR"], "image": "nadar.png"},
            {"word": "SALTAR", "syllables": ["SAL", "TAR"], "image": "saltar.png"},
            {"word": "TRISTE", "syllables": ["TRIS", "TE"], "image": "triste.png"},
            {"word": "QUIERO", "syllables": ["QUI","E", "RO"], "image": "yo quiero.png"},
            {"word": "APRENDER", "syllables": ["A", "PREN", "DER"], "image": "aprender.png"},
            {"word": "CANTAR", "syllables": ["CAN", "TAR"], "image": "cantar.png"},
            {"word": "ABRAZO", "syllables": ["A", "BRA", "ZO"], "image": "abrazo.png"},
        ]
        
        self.current_word_list = []
        self.current_word_index = 0
        self.current_syllable_index = 0
        self.previous_word_data = None

        self.shuffle_words()

        # --- Inicializar Audio ---
        self._init_audio()

        # --- Interfaz ---
        self.canvas = tk.Canvas(master, bg="#FAD4D4", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, radius=int(20 * self.scale), fill="white", outline="white")
        
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Título
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")

        self._load_icon("sonido.jpg", self.icon_size, self.title_container)
        
        self.title_label = tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white")
        self.title_label.pack(side=tk.LEFT)

        # Imagen Principal
        self.main_image_label = tk.Label(self.inner_frame, bg="white")
        self.main_image_label.place(relx=0.5, rely=0.4, anchor="center")

        # Sílaba
        self.syllable_container = tk.Frame(self.inner_frame, bg="white")
        self.syllable_container.place(relx=0.5, rely=0.65, anchor="center")

        self.speaker_label = self._load_icon("sonido.jpg", self.icon_size, self.syllable_container, clickable=True)
        
        self.syllable_label = tk.Label(self.syllable_container, text="", font=self.syllable_font, bg="white")
        self.syllable_label.pack(side=tk.LEFT)

        # Botones Inferiores
        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.85, anchor="center")

        # Botón Repetir (Circular)
        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, radius=int(self.repeat_button_size / 2), fill="#FFB347", outline="#FFB347")
        # Emoji de parlante es seguro en la mayoría de sistemas modernos
        self.repeat_circle.create_text(self.repeat_button_size / 2, self.repeat_button_size / 2, text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.05, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_syllable())

        # Botón Nivel 1 (Funcionalidad Siguiente)
        self._create_pill_button("Nivel 1", "#FF6B6B", self.next_word_or_syllable)
        
        # Botón Menú
        self._create_pill_button("Volver al Menú", "#5B84B1", self.go_to_menu)

        # Flechas Navegación
        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font, bg="white", fg="#FF6B6B", relief="flat", command=self.next_word_or_syllable)
        self.next_button.place(relx=0.75, rely=0.4, anchor="center")

        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font, bg="white", fg="#FF6B6B", relief="flat", command=self.prev_syllable)
        self.prev_button.place(relx=0.25, rely=0.4, anchor="center")

        self.syllable_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white")
        self.syllable_count_label.place(relx=0.9, rely=0.9, anchor="e")

        # Icono Oreja
        self._load_ear_icon()

        self.update_display()

    def _init_audio(self):
        try:
            # Frecuencia estándar 44100, 16bit, stereo, buffer 2048
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        except Exception as e:
            print(f"Error pygame: {e}")
        
        self.audio_cache_dir = os.path.join(SCRIPT_DIR, "audio_cache")
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)

    def _apply_scaling(self):
        scale = self.scale
        self.canvas_width = int(700 * scale)
        self.canvas_height = int(500 * scale)
        self.image_width = int(200 * scale)
        
        self.title_font = (SYSTEM_FONT, int(24 * scale), "bold")
        self.syllable_font = (SYSTEM_FONT, int(36 * scale), "bold")
        self.button_font = (SYSTEM_FONT, int(16 * scale), "bold")
        self.small_button_font = (SYSTEM_FONT, int(12 * scale), "bold")
        self.count_font = (SYSTEM_FONT, int(14 * scale))
        self.arrow_font = (SYSTEM_FONT, int(30 * scale), "bold")
        self.repeat_font = (SYSTEM_FONT, int(18 * scale))
        
        self.level_button_width = int(150 * scale)
        self.level_button_height = int(50 * scale)
        self.menu_button_width = int(200 * scale)
        self.menu_button_height = int(50 * scale)
        self.repeat_button_size = int(50 * scale)
        self.icon_size = int(30 * scale)
        self.ear_height = int(100 * scale)

    def _load_icon(self, filename, size, parent, clickable=False):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(parent, image=photo, bg="white")
                label.image = photo # Referencia para evitar GC
                label.pack(side=tk.LEFT, padx=5)
                if clickable:
                    label.bind("<Button-1>", self._on_syllable_speaker_click)
                return label
            except Exception as e:
                print(f"Error loading icon {filename}: {e}")
        return None

    def _load_ear_icon(self):
        path = os.path.join(SCRIPT_DIR, "escuchar.png")
        if os.path.exists(path):
            try:
                original = Image.open(path)
                aspect = original.width / original.height
                new_w = int(self.ear_height * aspect)
                img = original.resize((new_w, self.ear_height), Image.Resampling.LANCZOS)
                self.ear_photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.inner_frame, image=self.ear_photo, bg="white")
                lbl.place(relx=0.08, rely=0.85, anchor="w")
            except: pass
        else:
            lbl = tk.Label(self.inner_frame, text="[Escuchar]", font=self.count_font, bg="white")
            lbl.place(relx=0.08, rely=0.92, anchor="w")

    def _create_pill_button(self, text, color, command):
        w, h = self.menu_button_width, self.menu_button_height
        canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=w, height=h)
        self.draw_rounded_rect(canvas, 0, 0, w, h, radius=int(15 * self.scale), fill=color, outline=color)
        canvas.create_text(w / 2, h / 2, text=text, font=self.button_font, fill="white")
        canvas.bind("<Button-1>", lambda e: command())
        canvas.pack(side=tk.LEFT, padx=int(10 * self.scale))

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
                  x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def shuffle_words(self):
        shuffled_list = self.all_words_data[:]
        random.shuffle(shuffled_list)
        if self.previous_word_data and shuffled_list and shuffled_list[0] == self.previous_word_data:
            if len(shuffled_list) > 1:
                shuffled_list.append(shuffled_list.pop(0))
        self.current_word_list = shuffled_list
        self.current_word_index = 0
        self.current_syllable_index = 0

    def _generate_and_play_audio(self, text, path):
        try:
            if not os.path.exists(path):
                # Si es corto y raro, deletrear (simplificado)
                tts_text = text.lower()
                tts = gTTS(text=tts_text, lang='es', slow=True)
                tts.save(path)
            
            if pygame.mixer.get_init():
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Audio Error: {e}")

    def play_syllable_audio(self, syllable):
        clean_name = "".join(c for c in syllable.lower() if c.isalnum())
        path = os.path.join(self.audio_cache_dir, f"{clean_name}.mp3")
        threading.Thread(target=self._generate_and_play_audio, args=(syllable, path)).start()

    def _on_syllable_speaker_click(self, event):
        if self.current_word_list:
            syls = self.current_word_list[self.current_word_index]["syllables"]
            if self.current_syllable_index < len(syls):
                self.play_syllable_audio(syls[self.current_syllable_index])

    def update_display(self):
        if not self.current_word_list:
            self.shuffle_words()
        
        data = self.current_word_list[self.current_word_index]
        syls = data["syllables"]
        
        if self.current_syllable_index >= len(syls):
            self.current_syllable_index = 0

        txt = syls[self.current_syllable_index]
        self.syllable_label.config(text=txt)
        self.syllable_count_label.config(text=f"{self.current_syllable_index + 1}/{len(syls)}")

        self.load_word_image(data["image"])
        self.play_syllable_audio(txt)

    def load_word_image(self, filename):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                aspect = img.width / img.height
                new_h = int(self.image_width / aspect)
                img_tk = ImageTk.PhotoImage(img.resize((self.image_width, new_h), Image.Resampling.LANCZOS))
                self.main_image_label.config(image=img_tk, text="")
                self.main_image_label.image = img_tk
            except:
                self.main_image_label.config(image="", text="Error Img")
        else:
            self.main_image_label.config(image="", text="No Img")

    def next_word_or_syllable(self):
        syls = self.current_word_list[self.current_word_index]["syllables"]
        if self.current_syllable_index == len(syls) - 1:
            self._show_word_complete_screen(self.current_word_list[self.current_word_index]['word'])
        else:
            self.current_syllable_index += 1
            self.update_display()

    def prev_syllable(self):
        if self.current_syllable_index > 0:
            self.current_syllable_index -= 1
            self.update_display()

    def _show_word_complete_screen(self, word):
        win = tk.Toplevel(self.master)
        win.title("¡Bien!")
        w, h = int(400 * self.scale), int(250 * self.scale)
        win.geometry(f"{w}x{h}")
        win.attributes("-topmost", True)
        win.grab_set()
        
        frame = tk.Frame(win, bg="white", padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="¡Bien Hecho!", font=self.title_font, bg="white", fg="#FF5757").pack(pady=10)
        tk.Label(frame, text=f"Palabra: {word}", font=self.count_font, bg="white").pack(pady=5)
        
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=20)
        
        def action(act):
            win.destroy()
            if act == "next": self._advance_word()
            elif act == "menu": self.go_to_menu()
            
        tk.Button(btn_frame, text="Siguiente", bg="#FF6B6B", fg="white", font=self.small_button_font, 
                  command=lambda: action("next")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Menú", bg="#5B84B1", fg="white", font=self.small_button_font, 
                  command=lambda: action("menu")).pack(side=tk.LEFT, padx=10)
        
        # Centrar
        win.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        win.geometry(f"+{x}+{y}")

    def _advance_word(self):
        self.previous_word_data = self.current_word_list[self.current_word_index]
        self.current_word_index += 1
        if self.current_word_index >= len(self.current_word_list):
            self.shuffle_words()
        self.current_syllable_index = 0
        self.update_display()

    def repeat_current_syllable(self):
        syls = self.current_word_list[self.current_word_index]["syllables"]
        self.play_syllable_audio(syls[self.current_syllable_index])

    def go_to_menu(self):
        self.master.destroy()
        # Buscar el menú subiendo carpetas
        # Estructura esperada: .../simon dice/nivel1/nivel1.py -> .../simon dice/menu/menu_simondice.py
        path = os.path.join(SCRIPT_DIR, "..", "menu", "menu_simondice.py")
        path = os.path.normpath(path)
        
        if os.path.exists(path):
            subprocess.Popen([sys.executable, path])
        else:
            # Intento fallback
            path = os.path.join(SCRIPT_DIR, "..", "menu_simondice.py")
            if os.path.exists(path):
                subprocess.Popen([sys.executable, path])
            else:
                messagebox.showerror("Error", f"Menú no encontrado:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    game = SilabasGame(root)
    root.mainloop()