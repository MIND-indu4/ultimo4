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

try:
    import pygame.mixer
    from gtts import gTTS
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("ERROR: Falta pygame o gTTS.")

def get_system_font():
    return "Arial" if SYSTEM_OS == "Windows" else "DejaVu Sans"

SYSTEM_FONT = get_system_font()

class PalabrasGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Palabras")
        
        # --- PANTALLA COMPLETA ---
        master.attributes("-fullscreen", True)
        master.bind("<Escape>", lambda e: self.go_to_menu())
        master.configure(bg="#FF5757") 
        
        master.update_idletasks()

        # Escala
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1024  
        base_height = 768
        self.scale = min(screen_width / base_width, screen_height / base_height)

        self._apply_scaling()

        # Datos
        self.all_words_data = [
            {"word": "ASUSTADO", "image": "asustado.png"},
            {"word": "BAÑO", "image": "baño.png"},
            {"word": "CAMINAR", "image": "caminar.png"},
            {"word": "COCINA", "image": "cocina.png"},
            {"word": "COMER", "image": "comer.png"},
            {"word": "CORRER", "image": "correr.png"},
            {"word": "DORMIR", "image": "dormir.png"},
            {"word": "ESCUCHAR", "image": "escuchar1.png"},
            {"word": "FELIZ", "image": "feliz.png"},
            {"word": "NADAR", "image": "nadar.png"},
            {"word": "OBSERVAR", "image": "observar.png"},
            {"word": "SALTAR", "image": "saltar.png"},
            {"word": "TENER", "image": "tener.png"},
            {"word": "TRISTE", "image": "triste.png"},
            {"word": "YO QUIERO", "image": "yo quiero.png"}
        ]

        self.available_words = [] 
        self.shuffle_available_words()
        self._init_audio()

        self.current_word_index = 0
        self.recent_words_data = [] 
        self.game_state = "individual_word" 
        self.individual_word_counter = 0 

        # --- INTERFAZ PRINCIPAL (CORREGIDA: Esquinas Redondeadas Visibles) ---
        
        # 1. Canvas de fondo (Tarjeta Blanca Principal)
        self.canvas = tk.Canvas(master, bg="#FF5757", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        
        # Dibujamos el rectángulo blanco con radio 30
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, 
                               radius=int(30 * self.scale), fill="white", outline="white")
        
        # 2. Frame Interior (Con Padding para no tapar las esquinas)
        self.inner_frame = tk.Frame(self.master, bg="white")
        pad = int(20 * self.scale) # Margen para que se vea la curva del canvas
        self.inner_frame.place(
            x=(screen_width - self.canvas_width)/2 + pad, 
            y=(screen_height - self.canvas_height)/2 + pad, 
            width=self.canvas_width - (pad*2), 
            height=self.canvas_height - (pad*2)
        )

        # --- ELEMENTOS ---
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")
        self._load_icon("sonido.jpg", self.icon_size_title, self.title_container)
        tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white").pack(side=tk.LEFT)

        # --- FRAMES DINÁMICOS ---
        self.single_word_display_frame = tk.Frame(self.inner_frame, bg="white")
        self.single_main_image_label = tk.Label(self.single_word_display_frame, bg="white")
        self.single_main_image_label.pack(pady=int(10 * self.scale))

        self.single_word_text_container = tk.Frame(self.single_word_display_frame, bg="white")
        self.single_word_text_container.pack(pady=int(5 * self.scale))
        
        self._load_icon("sonido.jpg", self.icon_size_word, self.single_word_text_container, clickable=False)
        self.single_word_label = tk.Label(self.single_word_text_container, text="", font=self.word_font, bg="white")
        self.single_word_label.pack(side=tk.LEFT)

        self.group_summary_display_frame = tk.Frame(self.inner_frame, bg="white")
        self.image_labels = []
        self.speaker_word_labels = []
        self.word_labels = []

        for i in range(3):
            item_frame = tk.Frame(self.group_summary_display_frame, bg="white", padx=int(10 * self.scale), pady=int(10 * self.scale))
            item_frame.pack(side=tk.LEFT, padx=int(15 * self.scale))

            img_lbl = tk.Label(item_frame, bg="white")
            img_lbl.pack(pady=int(5 * self.scale))
            self.image_labels.append(img_lbl)

            word_cont = tk.Frame(item_frame, bg="white")
            word_cont.pack(pady=int(5 * self.scale))

            spk_lbl = self._load_icon_return_label("sonido.jpg", self.icon_size_summary, word_cont)
            self.speaker_word_labels.append(spk_lbl)

            wd_lbl = tk.Label(word_cont, text="", font=self.summary_word_font, bg="white")
            wd_lbl.pack(side=tk.LEFT)
            self.word_labels.append(wd_lbl)

        # --- CONTROLES ---
        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.88, anchor="center")

        self._create_pill_button("Siguiente", "#FF6B6B", self.next_step, self.bottom_buttons_container)
        self._create_pill_button("Salir", "#5B84B1", self.go_to_menu, self.bottom_buttons_container)

        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font, 
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_step)
        self.next_button.place(relx=0.88, rely=0.5, anchor="center")

        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font, 
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_step)
        self.prev_button.place(relx=0.12, rely=0.5, anchor="center")

        self.word_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white", fg="#999")
        self.word_count_label.place(relx=0.95, rely=0.95, anchor="se")

        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, 
                                       width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, 
                               radius=int(self.repeat_button_size / 2), fill="#FFB347", outline="#FFB347")
        self.repeat_circle.create_text(self.repeat_button_size / 2, self.repeat_button_size / 2, 
                                       text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.08, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_word())

        self.update_display()

    def _init_audio(self):
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            except Exception as e:
                print(f"Error Mixer: {e}")
        
        self.audio_cache_dir = os.path.join(SCRIPT_DIR, "audio_cache_words")
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)

    def _apply_scaling(self):
        scale = self.scale
        self.canvas_width = int(1000 * scale) # Ancho igual al Nivel 1
        self.canvas_height = int(700 * scale)
        self.image_width_single = int(250 * scale)
        self.image_width_group = int(120 * scale)
        
        self.title_font = (SYSTEM_FONT, int(28 * scale), "bold")
        self.word_font = (SYSTEM_FONT, int(24 * scale), "bold")
        self.summary_word_font = (SYSTEM_FONT, int(16 * scale), "bold")
        self.button_font = (SYSTEM_FONT, int(14 * scale), "bold")
        self.small_button_font = (SYSTEM_FONT, int(12 * scale), "bold")
        self.count_font = (SYSTEM_FONT, int(12 * scale))
        self.arrow_font = (SYSTEM_FONT, int(40 * scale), "bold")
        self.repeat_font = (SYSTEM_FONT, int(20 * scale))
        
        self.menu_button_width = int(160 * scale)
        self.menu_button_height = int(45 * scale)
        self.repeat_button_size = int(60 * scale)
        self.icon_size_title = int(40 * scale)
        self.icon_size_word = int(45 * scale)
        self.icon_size_summary = int(30 * scale)

    def _load_icon(self, filename, size, parent, clickable=False):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(parent, image=photo, bg="white")
                label.image = photo
                label.pack(side=tk.LEFT, padx=int(5 * self.scale))
                return label
            except: pass
        return None
    
    def _load_icon_return_label(self, filename, size, parent):
        label = self._load_icon(filename, size, parent)
        if not label:
            label = tk.Label(parent, text="🔊", bg="white", font=self.summary_word_font)
            label.pack(side=tk.LEFT, padx=3)
        return label

    def _create_pill_button(self, text, color, command, parent_frame):
        w, h = self.menu_button_width, self.menu_button_height
        # highlightthickness=0 y bd=0 es crucial para evitar cortes
        canvas = tk.Canvas(parent_frame, bg="white", highlightthickness=0, bd=0, width=w, height=h)
        
        # Margen interno de 3px para que no se corte el dibujo
        self.draw_rounded_rect(canvas, 3, 3, w-3, h-3, radius=int(20 * self.scale), fill=color, outline=color)
        
        canvas.create_text(w / 2, h / 2, text=text, font=self.button_font, fill="white")
        canvas.bind("<Button-1>", lambda e: command())
        canvas.pack(side=tk.LEFT, padx=int(15 * self.scale))

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
                  x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def shuffle_available_words(self):
        self.available_words = self.all_words_data[:]
        random.shuffle(self.available_words)
        self.current_word_index = 0

    def get_next_individual_word(self):
        if not self.available_words or self.current_word_index >= len(self.available_words):
            self.shuffle_available_words()
            if not self.available_words: return None
        
        word_data = self.available_words[self.current_word_index]
        self.current_word_index += 1
        return word_data

    def update_display(self):
        self.single_word_display_frame.place_forget()
        self.group_summary_display_frame.place_forget()

        if self.game_state == "individual_word":
            self.display_individual_word()
        elif self.game_state == "group_summary":
            self.display_group_summary()

    def display_individual_word(self):
        self.single_word_display_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.individual_word_counter < len(self.recent_words_data):
            word_data = self.recent_words_data[self.individual_word_counter]
        else:
            word_data = self.get_next_individual_word()
            if word_data:
                self.recent_words_data.append(word_data)
            else:
                self.single_word_label.config(text="Fin")
                return

        self.single_word_label.config(text=word_data["word"])
        self.play_word_audio(word_data["word"])
        self.load_image(word_data["image"], self.single_main_image_label, self.image_width_single)
        self.word_count_label.config(text=f"Palabra {self.individual_word_counter + 1} de 3")

    def display_group_summary(self):
        self.group_summary_display_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.master.after(500, self.speak_summary_words)

        if not self.recent_words_data: return

        for i in range(3):
            if i < len(self.recent_words_data):
                wd = self.recent_words_data[i]
                self.word_labels[i].config(text=wd["word"])
                self.load_image(wd["image"], self.image_labels[i], self.image_width_group)
                self.speaker_word_labels[i].bind("<Button-1>", lambda e, w=wd["word"]: self.play_word_audio(w))
            else:
                self.word_labels[i].config(text="")
                self.image_labels[i].config(image="")
                self.speaker_word_labels[i].unbind("<Button-1>")
        
        self.word_count_label.config(text="Resumen de palabras")

    def load_image(self, filename, label_widget, width):
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
                    new_h = int(width / aspect)
                    photo = ImageTk.PhotoImage(img.resize((width, new_h), Image.Resampling.LANCZOS))
                    label_widget.config(image=photo, text="")
                    label_widget.image = photo
                    found = True
                    break
                except: pass
        if not found:
            label_widget.config(image="", text=f"Img: {filename}")

    def next_step(self):
        if self.game_state == "individual_word":
            self.individual_word_counter += 1
            if self.individual_word_counter == 3:
                self.game_state = "group_summary"
            elif self.individual_word_counter > 3:
                self.recent_words_data = []
                self.individual_word_counter = 0
                self.game_state = "individual_word"
        elif self.game_state == "group_summary":
            self._show_cycle_complete_screen()
            return
        self.update_display()

    def prev_step(self):
        if self.game_state == "group_summary":
            self.game_state = "individual_word"
            self.individual_word_counter = len(self.recent_words_data) - 1
        elif self.game_state == "individual_word":
            if self.individual_word_counter > 0:
                self.individual_word_counter -= 1
                if len(self.recent_words_data) > self.individual_word_counter:
                    self.recent_words_data.pop()
                if self.current_word_index > 0:
                    self.current_word_index -= 1
        self.update_display()

    # =================================================================
    # --- POPUP: TARJETA LIMPIA, REDONDEADA Y BOTONES PERFECTOS ---
    # =================================================================
    def _show_cycle_complete_screen(self):
        win = tk.Toplevel(self.master)
        win.overrideredirect(True)
        win.configure(bg="#FF5757") 
        
        # Tamaño
        w_popup = int(600 * self.scale)
        h_popup = int(450 * self.scale)
        
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw - w_popup) // 2
        y = (sh - h_popup) // 2
        
        win.geometry(f"{w_popup}x{h_popup}+{x}+{y}")
        win.attributes("-topmost", True)
        win.grab_set()
        
        # Fondo Blanco con esquinas MUY redondeadas (Radius 60)
        popup_canvas = tk.Canvas(win, bg="#FF5757", highlightthickness=0, bd=0)
        popup_canvas.pack(fill="both", expand=True)
        
        margin = 5
        self.draw_rounded_rect(popup_canvas, margin, margin, w_popup-margin, h_popup-margin, 
                               radius=int(60 * self.scale), fill="white", outline="white")
        
        # Contenido (con padding grande para evitar las esquinas)
        content_frame = tk.Frame(win, bg="white")
        pad_inner = int(40 * self.scale)
        content_frame.place(x=pad_inner, y=pad_inner, width=w_popup-(pad_inner*2), height=h_popup-(pad_inner*2))
        
        tk.Label(content_frame, text="¡Excelente Trabajo!", font=(SYSTEM_FONT, int(32 * self.scale), "bold"), 
                 bg="white", fg="#FF6B6B").pack(pady=(10, 5))
        
        tk.Label(content_frame, text="⭐", font=(SYSTEM_FONT, int(80 * self.scale)), 
                 bg="white", fg="#FBC02D").pack(pady=5)
        
        tk.Label(content_frame, text="¡Has completado un ciclo de 3 palabras!", 
                 font=(SYSTEM_FONT, int(16 * self.scale)), bg="white", fg="#757575").pack(pady=5)
        
        tk.Label(content_frame, text="¿Qué quieres hacer?", 
                 font=self.count_font, bg="white", fg="#999").pack(pady=5)
        
        # Botones
        btn_frame = tk.Frame(content_frame, bg="white")
        btn_frame.pack(pady=15)
        
        def action(act):
            win.destroy()
            if act == "next":
                self.recent_words_data = []
                self.individual_word_counter = 0
                self.game_state = "individual_word"
                if len(self.available_words) - self.current_word_index < 3:
                    self.shuffle_available_words()
                self.update_display()
            elif act == "menu": self.go_to_menu()
            
        w_btn, h_btn = int(150 * self.scale), int(50 * self.scale)
        
        # Botón Siguiente (Margen de seguridad 5px para no cortar)
        cv_next = tk.Canvas(btn_frame, bg="white", highlightthickness=0, bd=0, width=w_btn, height=h_btn)
        self.draw_rounded_rect(cv_next, 5, 5, w_btn-5, h_btn-5, radius=20, fill="#FF6B6B", outline="#FF6B6B")
        cv_next.create_text(w_btn/2, h_btn/2, text="Siguiente", font=self.button_font, fill="white")
        cv_next.bind("<Button-1>", lambda e: action("next"))
        cv_next.pack(side=tk.LEFT, padx=15)
        
        # Botón Salir (Margen de seguridad 5px)
        cv_menu = tk.Canvas(btn_frame, bg="white", highlightthickness=0, bd=0, width=w_btn, height=h_btn)
        self.draw_rounded_rect(cv_menu, 5, 5, w_btn-5, h_btn-5, radius=20, fill="#5B84B1", outline="#5B84B1")
        cv_menu.create_text(w_btn/2, h_btn/2, text="Salir", font=self.button_font, fill="white")
        cv_menu.bind("<Button-1>", lambda e: action("menu"))
        cv_menu.pack(side=tk.LEFT, padx=15)

    def go_to_menu(self):
        self.master.destroy()
        path = os.path.join(SCRIPT_DIR, "..", "menu", "menu_simondice.py")
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            path = os.path.join(SCRIPT_DIR, "..", "menu_simondice.py")
            
        if os.path.exists(path):
            if SYSTEM_OS == "Windows":
                subprocess.Popen([sys.executable, path], creationflags=subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable, path])
        else:
            messagebox.showerror("Error", f"Menú no encontrado en:\n{path}")

    def _generate_audio(self, text, path):
        if not AUDIO_AVAILABLE: return
        if not os.path.exists(path):
            try:
                tts = gTTS(text=text.lower(), lang='es', slow=True)
                tts.save(path)
            except: return
        
        try:
            if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except: pass

    def play_word_audio(self, word):
        clean = word.lower().replace(" ", "_").replace("ñ", "n")
        path = os.path.join(self.audio_cache_dir, f"{clean}.mp3")
        threading.Thread(target=self._generate_audio, args=(word, path)).start()

    def repeat_current_word(self):
        if self.game_state == "individual_word" and self.recent_words_data:
            self.play_word_audio(self.recent_words_data[self.individual_word_counter]["word"])
        elif self.game_state == "group_summary":
            self.speak_summary_words()

    def speak_summary_words(self):
        if not self.recent_words_data: return
        def speak(idx=0):
            if idx >= len(self.recent_words_data): return
            self.play_word_audio(self.recent_words_data[idx]["word"])
            self.master.after(1500, speak, idx + 1)
        speak()

if __name__ == "__main__":
    root = tk.Tk()
    game = PalabrasGame(root)
    root.mainloop()
