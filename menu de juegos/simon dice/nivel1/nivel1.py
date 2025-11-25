import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import sys
import subprocess
import threading
import platform

# ========== CONFIGURACIÓN DE SISTEMA ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_OS = platform.system()

# Intento de importar audio
try:
    import pygame.mixer
    from gtts import gTTS
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("AVISO: Librerías de audio no encontradas.")

def get_system_font():
    return "Arial" if SYSTEM_OS == "Windows" else "DejaVu Sans"

SYSTEM_FONT = get_system_font()

class SilabasGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Sílabas")

        # --- PANTALLA COMPLETA ---
        master.attributes("-fullscreen", True)
        master.bind("<Escape>", lambda e: self.go_to_menu())
        master.configure(bg="#FF5757") 
        
        master.update_idletasks()

        # Escala dinámica
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1024
        base_height = 768
        self.scale = min(screen_width / base_width, screen_height / base_height)

        self._apply_scaling()

        # Datos del Nivel 1
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
        self._init_audio()

        # --- INTERFAZ PRINCIPAL ---
        self.canvas = tk.Canvas(master, bg="#FF5757", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, 
                               radius=int(30 * self.scale), fill="white", outline="white")
        
        self.inner_frame = tk.Frame(self.master, bg="white")
        pad = int(20 * self.scale)
        self.inner_frame.place(
            x=(screen_width - self.canvas_width)/2 + pad, 
            y=(screen_height - self.canvas_height)/2 + pad, 
            width=self.canvas_width - (pad*2), 
            height=self.canvas_height - (pad*2)
        )

        # --- ELEMENTOS DEL JUEGO ---
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")
        self._load_icon("sonido.jpg", self.icon_size, self.title_container)
        self.title_label = tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white")
        self.title_label.pack(side=tk.LEFT)

        self.main_image_label = tk.Label(self.inner_frame, bg="white")
        self.main_image_label.place(relx=0.5, rely=0.4, anchor="center")

        self.syllable_container = tk.Frame(self.inner_frame, bg="white")
        self.syllable_container.place(relx=0.5, rely=0.68, anchor="center")
        self.speaker_label = self._load_icon("sonido.jpg", self.icon_size, self.syllable_container, clickable=True)
        self.syllable_label = tk.Label(self.syllable_container, text="", font=self.syllable_font, bg="white")
        self.syllable_label.pack(side=tk.LEFT)

        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.88, anchor="center")

        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, 
                                       width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, 
                               radius=int(self.repeat_button_size / 2), fill="#FFB347", outline="#FFB347")
        self.repeat_circle.create_text(self.repeat_button_size / 2, self.repeat_button_size / 2, 
                                       text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.92, rely=0.08, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_syllable())

        self._create_pill_button("Siguiente", "#FF6B6B", self.next_word_or_syllable, self.bottom_buttons_container)
        self._create_pill_button("Salir", "#5B84B1", self.go_to_menu, self.bottom_buttons_container)

        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font, 
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_word_or_syllable)
        self.next_button.place(relx=0.88, rely=0.5, anchor="center")

        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font, 
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_syllable)
        self.prev_button.place(relx=0.12, rely=0.5, anchor="center")

        self.syllable_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white", fg="#999")
        self.syllable_count_label.place(relx=0.95, rely=0.95, anchor="se")

        self.update_display()

    def _init_audio(self):
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            except Exception as e:
                print(f"Error iniciando mixer: {e}")
        
        self.audio_cache_dir = os.path.join(SCRIPT_DIR, "audio_cache")
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)

    def _apply_scaling(self):
        scale = self.scale
        self.canvas_width = int(1000 * scale)
        self.canvas_height = int(700 * scale)
        self.image_width = int(250 * scale)
        
        self.title_font = (SYSTEM_FONT, int(28 * scale), "bold")
        self.syllable_font = (SYSTEM_FONT, int(48 * scale), "bold")
        self.button_font = (SYSTEM_FONT, int(14 * scale), "bold")
        self.count_font = (SYSTEM_FONT, int(12 * scale))
        self.arrow_font = (SYSTEM_FONT, int(40 * scale), "bold")
        self.repeat_font = (SYSTEM_FONT, int(24 * scale))
        
        self.menu_button_width = int(160 * scale)
        self.menu_button_height = int(45 * scale)
        self.repeat_button_size = int(60 * scale)
        self.icon_size = int(40 * scale)

    def _load_icon(self, filename, size, parent, clickable=False):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(parent, image=photo, bg="white")
                label.image = photo 
                label.pack(side=tk.LEFT, padx=10)
                if clickable:
                    label.bind("<Button-1>", self._on_syllable_speaker_click)
                return label
            except: pass
        return None

    def _create_pill_button(self, text, color, command, parent_widget):
        w, h = self.menu_button_width, self.menu_button_height
        canvas = tk.Canvas(parent_widget, bg="white", highlightthickness=0, bd=0, width=w, height=h)
        
        # Margen interno de seguridad para evitar cortes
        self.draw_rounded_rect(canvas, 3, 3, w-3, h-3, radius=int(20 * self.scale), fill=color, outline=color)
        
        canvas.create_text(w / 2, h / 2, text=text, font=self.button_font, fill="white")
        canvas.bind("<Button-1>", lambda e: command())
        canvas.pack(side=tk.LEFT, padx=int(20 * self.scale))

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
        if not AUDIO_AVAILABLE: return
        try:
            if not os.path.exists(path):
                tts = gTTS(text=text.lower(), lang='es', slow=True)
                tts.save(path)
            if pygame.mixer.get_init():
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
        except: pass

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
        self.syllable_count_label.config(text=f"Sílaba {self.current_syllable_index + 1} de {len(syls)}")
        self.load_word_image(data["image"])
        self.play_syllable_audio(txt)

    def load_word_image(self, filename):
        rutas = [
            os.path.join(SCRIPT_DIR, filename),
            os.path.join(SCRIPT_DIR, "imagenes", filename),
            os.path.join(SCRIPT_DIR, "..", "assets", filename)
        ]
        found = False
        for path in rutas:
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    aspect = img.width / img.height
                    new_h = int(self.image_width / aspect)
                    img_tk = ImageTk.PhotoImage(img.resize((self.image_width, new_h), Image.Resampling.LANCZOS))
                    self.main_image_label.config(image=img_tk, text="")
                    self.main_image_label.image = img_tk
                    found = True
                    break
                except: pass
        if not found:
            self.main_image_label.config(image="", text=f"[Img: {filename}]")

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

    # =================================================================
    # --- VENTANA DE FELICITACIONES (BOTONES MÁS ARRIBA) ---
    # =================================================================
    def _show_word_complete_screen(self, word):
        win = tk.Toplevel(self.master)
        win.overrideredirect(True)
        win.configure(bg="#FF5757") 
        
        w_popup = int(600 * self.scale)
        h_popup = int(450 * self.scale)
        
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw - w_popup) // 2
        y = (sh - h_popup) // 2
        
        win.geometry(f"{w_popup}x{h_popup}+{x}+{y}")
        win.attributes("-topmost", True)
        win.grab_set()
        
        # 1. Fondo Blanco Redondeado
        popup_canvas = tk.Canvas(win, bg="#FF5757", highlightthickness=0, bd=0)
        popup_canvas.pack(fill="both", expand=True)
        
        # Margen para el dibujo (para evitar cortes en el borde blanco)
        margin = 5
        self.draw_rounded_rect(popup_canvas, margin, margin, w_popup-margin, h_popup-margin, 
                               radius=int(60 * self.scale), fill="white", outline="white")
        
        # 2. Contenido
        content_frame = tk.Frame(win, bg="white")
        pad_inner = int(40 * self.scale)
        content_frame.place(x=pad_inner, y=pad_inner, width=w_popup-(pad_inner*2), height=h_popup-(pad_inner*2))
        
        # Título
        tk.Label(content_frame, text="¡Felicidades!", font=(SYSTEM_FONT, int(32 * self.scale), "bold"), 
                 bg="white", fg="#FF6B6B").pack(pady=(5, 5)) # Menos padding arriba
        
        # Estrella
        tk.Label(content_frame, text="⭐", font=(SYSTEM_FONT, int(80 * self.scale)), 
                 bg="white", fg="#FBC02D").pack(pady=5)
        
        # Texto descriptivo
        tk.Label(content_frame, text="¡Has completado la palabra!", 
                 font=(SYSTEM_FONT, int(16 * self.scale)), bg="white", fg="#757575").pack(pady=5)
        
        # Palabra (REDUJE EL PADDING DE ABAJO PARA SUBIR LOS BOTONES)
        tk.Label(content_frame, text=word, font=(SYSTEM_FONT, int(40 * self.scale), "bold"), 
                 bg="white", fg="#FF5757").pack(pady=(10, 5)) 
        
        # 3. Botones (REDUJE EL PADDING DEL FRAME PARA SUBIRLOS MÁS)
        btn_frame = tk.Frame(content_frame, bg="white")
        btn_frame.pack(pady=5)
        
        def action(act):
            win.destroy()
            if act == "next": self._advance_word()
            elif act == "menu": self.go_to_menu()
            
        w_btn, h_btn = int(150 * self.scale), int(50 * self.scale)
        
        # Botón Siguiente
        cv_next = tk.Canvas(btn_frame, bg="white", highlightthickness=0, bd=0, width=w_btn, height=h_btn)
        self.draw_rounded_rect(cv_next, 5, 5, w_btn-5, h_btn-5, radius=20, fill="#FF6B6B", outline="#FF6B6B")
        cv_next.create_text(w_btn/2, h_btn/2, text="Siguiente", font=self.button_font, fill="white")
        cv_next.bind("<Button-1>", lambda e: action("next"))
        cv_next.pack(side=tk.LEFT, padx=15)
        
        # Botón Salir
        cv_menu = tk.Canvas(btn_frame, bg="white", highlightthickness=0, bd=0, width=w_btn, height=h_btn)
        self.draw_rounded_rect(cv_menu, 5, 5, w_btn-5, h_btn-5, radius=20, fill="#5B84B1", outline="#5B84B1")
        cv_menu.create_text(w_btn/2, h_btn/2, text="Salir", font=self.button_font, fill="white")
        cv_menu.bind("<Button-1>", lambda e: action("menu"))
        cv_menu.pack(side=tk.LEFT, padx=15)

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
        path = os.path.join(SCRIPT_DIR, "..", "menu", "menu_simondice.py")
        path = os.path.normpath(path)
        if os.path.exists(path):
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, path], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, path])
        else:
            messagebox.showerror("Error", f"Menú no encontrado:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    game = SilabasGame(root)
    root.mainloop()
