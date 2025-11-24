import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import sys
import subprocess
import threading
import platform

# ========== CONFIGURACIÓN DEL SISTEMA ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Intentar importar librerías de audio de forma segura
try:
    import pygame.mixer
    from gtts import gTTS
except ImportError:
    print("ERROR: Falta pygame o gTTS. Instálalos con pip.")

def get_system_font():
    return "Arial" if platform.system() == "Windows" else "DejaVu Sans"

SYSTEM_FONT = get_system_font()

class FrasesGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Frases")
        
        # Configuración Pantalla Completa y Escala
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1000
        base_height = 700
        self.scale = min(screen_width / base_width, screen_height / base_height)

        master.attributes("-fullscreen", True)
        master.configure(bg="#FF5757")
        
        # Salir con Escape
        master.bind("<Escape>", lambda e: self.go_to_menu())

        # Inicializar Audio
        self._init_audio()

        # Configuración de Estilos (Fuentes y Tamaños)
        self._apply_scaling()

        # --- DATOS DE LAS FRASES ---
        # IMPORTANTE: En Linux, revisa que las imágenes se llamen EXACTAMENTE así (minúsculas)
        self.all_phrases_data = [
            {
                "phrase_text": "Mamá yo quiero comer comida",
                "words": [
                    {"word": "Mamá", "image": "mama.png"},
                    {"word": "yo", "image": "yo.png"},
                    {"word": "quiero", "image": "quiero.png"},
                    {"word": "comer", "image": "comer.png"},
                    {"word": "comida", "image": "comida.png"}
                ]
            },
            {
                "phrase_text": "Papá yo quiero tomar agua",
                "words": [
                    {"word": "Papá", "image": "papa.png"},
                    {"word": "yo", "image": "yo.png"},
                    {"word": "quiero", "image": "quiero.png"},
                    {"word": "tomar", "image": "tomar.png"},
                    {"word": "agua", "image": "agua.png"}
                ]
            },
            {
                "phrase_text": "Yo quiero jugar con amigos",
                "words": [
                    {"word": "Yo", "image": "yo.png"},
                    {"word": "quiero", "image": "quiero.png"},
                    {"word": "jugar", "image": "jugar.png"},
                    {"word": "con", "image": "con.png"},
                    {"word": "amigos", "image": "amigos.png"}
                ]
            },
            {
                "phrase_text": "Yo escucho música con mis amigos",
                "words": [
                    {"word": "Yo", "image": "yo.png"},
                    {"word": "escucho", "image": "escuchar.png"},
                    {"word": "música", "image": "musica.png"},
                    {"word": "con", "image": "con.png"},
                    {"word": "mis", "image": "mis.png"},
                    {"word": "amigos", "image": "amigos.png"}
                ]
            },
            {
                "phrase_text": "Primero vamos a la escuela y después al parque",
                "words": [
                    {"word": "Primero", "image": "primero.png"},
                    {"word": "vamos", "image": "vamos.png"},
                    {"word": "a", "image": "a.png"},
                    {"word": "la", "image": "la.png"},
                    {"word": "escuela", "image": "escuela.png"},
                    {"word": "y", "image": "y.png"},
                    {"word": "después", "image": "despues.png"},
                    {"word": "al", "image": "al.png"},
                    {"word": "parque", "image": "parque.png"}
                ]
            },
            {
                "phrase_text": "Compartimos las galletas con los amigos",
                "words": [
                    {"word": "Compartimos", "image": "compartimos.png"},
                    {"word": "las", "image": "las.png"},
                    {"word": "galletas", "image": "galletas.png"},
                    {"word": "con", "image": "con.png"},
                    {"word": "los", "image": "los.png"},
                    {"word": "amigos", "image": "amigos.png"}
                ]
            },
            {
                "phrase_text": "Yo quiero ir al baño",
                "words": [
                    {"word": "Yo", "image": "yo.png"},
                    {"word": "quiero", "image": "quiero.png"},
                    {"word": "ir", "image": "ir.png"},
                    {"word": "al", "image": "al.png"},
                    {"word": "baño", "image": "baño.png"}
                ]
            },
            {
                "phrase_text": "Yo ordeno mi habitación",
                "words": [
                    {"word": "Yo", "image": "yo.png"},
                    {"word": "ordeno", "image": "ordeno.png"},
                    {"word": "mi", "image": "yo.png"},
                    {"word": "habitación", "image": "habitacion.png"}
                ]
            },
            {
                "phrase_text": "Esperamos nuestro turno",
                "words": [
                    {"word": "Esperamos", "image": "esperamos.png"},
                    {"word": "nuestro", "image": "nuestro.png"},
                    {"word": "turno", "image": "turno.png"}
                ]
            },
            {
                "phrase_text": "Yo me lavo los dientes y la cara para ir a dormir",
                "words": [
                    {"word": "Yo", "image": "yo.png"},
                    {"word": "me", "image": "me.png"},
                    {"word": "lavo", "image": "lavo.png"},
                    {"word": "los", "image": "los.png"},
                    {"word": "dientes", "image": "dientes.png"},
                    {"word": "y", "image": "y.png"},
                    {"word": "la", "image": "la.png"},
                    {"word": "cara", "image": "cara.png"},
                    {"word": "para", "image": "para.png"},
                    {"word": "ir", "image": "ir.png"},
                    {"word": "a", "image": "a.png"},
                    {"word": "dormir", "image": "dormir.png"}
                ]
            }
        ]

        self.current_phrase_index = 0
        self.current_word_in_phrase_index = 0
        self.available_phrases = []
        self.shuffle_available_phrases()

        self.game_state = "individual_word"

        # --- INTERFAZ ---
        self.canvas = tk.Canvas(master, bg="#FF5757", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, radius=int(20*self.scale), fill="white", outline="white")
        
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Título
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")
        self._load_icon("sonido.jpg", self.icon_size_title, self.title_container)
        tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white").pack(side=tk.LEFT)

        # Frame Central (Palabra e Imagen)
        self.single_word_display_frame = tk.Frame(self.inner_frame, bg="white")
        self.single_word_display_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.single_main_image_label = tk.Label(self.single_word_display_frame, bg="white")
        self.single_main_image_label.pack(pady=int(10*self.scale))

        self.single_word_text_container = tk.Frame(self.single_word_display_frame, bg="white")
        self.single_word_text_container.pack(pady=int(5*self.scale))

        # Icono sonido palabra
        self._load_icon("sonido.jpg", self.icon_size_word, self.single_word_text_container)
        self.single_word_label = tk.Label(self.single_word_text_container, text="", font=self.word_font, bg="white")
        self.single_word_label.pack(side=tk.LEFT)

        # --- BOTONES INFERIORES ---
        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.85, anchor="center")

        self._create_pill_button("Nivel 3", "#FF6B6B", self.next_phrase)
        self._create_pill_button("Volver al Menú", "#5B84B1", self.go_to_menu)

        # Flechas
        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font,
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_word_in_phrase)
        self.next_button.place(relx=0.85, rely=0.5, anchor="center")

        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font,
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_word_in_phrase)
        self.prev_button.place(relx=0.15, rely=0.5, anchor="center")

        self.word_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white")
        self.word_count_label.place(relx=0.9, rely=0.9, anchor="e")

        # Botón Repetir
        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, radius=int(self.repeat_button_size/2), fill="#FFB347", outline="#FFB347")
        self.repeat_circle.create_text(self.repeat_button_size/2, self.repeat_button_size/2, text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.05, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_word())

        # Icono Oreja
        self._load_ear_icon()

        self.update_display()

    def _init_audio(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        except Exception as e:
            print(f"Error Mixer: {e}")
        
        # Creamos carpeta caché para no re-generar audios siempre (más rápido en RPi)
        self.audio_cache_dir = os.path.join(SCRIPT_DIR, "audio_cache_phrases")
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)

    def _apply_scaling(self):
        scale = self.scale
        self.canvas_width = int(900 * scale)
        self.canvas_height = int(600 * scale)
        self.image_max_size = int(300 * scale)
        
        self.title_font = (SYSTEM_FONT, int(36 * scale), "bold")
        self.word_font = (SYSTEM_FONT, int(24 * scale), "bold")
        self.button_font = (SYSTEM_FONT, int(14 * scale), "bold")
        self.small_button_font = (SYSTEM_FONT, int(12 * scale), "bold")
        self.count_font = (SYSTEM_FONT, int(12 * scale))
        self.arrow_font = (SYSTEM_FONT, int(30 * scale), "bold")
        self.repeat_font = (SYSTEM_FONT, int(18 * scale))
        
        self.menu_button_width = int(180 * scale)
        self.menu_button_height = int(50 * scale)
        self.repeat_button_size = int(50 * scale)
        
        self.icon_size_title = int(40 * scale)
        self.icon_size_word = int(45 * scale)
        self.ear_height = int(100 * scale)

    def _load_icon(self, filename, size, parent):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(parent, image=photo, bg="white")
                lbl.image = photo
                lbl.pack(side=tk.LEFT, padx=5)
                return lbl
            except: pass
        return None

    def _load_ear_icon(self):
        path = os.path.join(SCRIPT_DIR, "escuchar.png")
        if os.path.exists(path):
            try:
                original = Image.open(path)
                aspect = original.width / original.height
                new_w = int(self.ear_height * aspect)
                photo = ImageTk.PhotoImage(original.resize((new_w, self.ear_height), Image.Resampling.LANCZOS))
                lbl = tk.Label(self.inner_frame, image=photo, bg="white")
                lbl.image = photo
                lbl.place(relx=0.08, rely=0.85, anchor="w")
            except: pass
        else:
            tk.Label(self.inner_frame, text="[Escuchar]", font=self.count_font, bg="white").place(relx=0.08, rely=0.92, anchor="w")

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

    def shuffle_available_phrases(self):
        self.available_phrases = self.all_phrases_data[:]
        random.shuffle(self.available_phrases)
        self.current_phrase_index = 0
        self.current_word_in_phrase_index = 0

    def get_current_phrase_data(self):
        if not self.available_phrases: return None
        return self.available_phrases[self.current_phrase_index]

    def update_display(self):
        self.display_current_word_of_phrase()

    def display_current_word_of_phrase(self):
        phrase_data = self.get_current_phrase_data()
        if not phrase_data or not phrase_data["words"]:
            self.single_word_label.config(text="Fin")
            return

        words_in_phrase = phrase_data["words"]
        total = len(words_in_phrase)

        if self.current_word_in_phrase_index >= total:
            self.current_word_in_phrase_index = total - 1

        word_data = words_in_phrase[self.current_word_in_phrase_index]

        self.single_word_label.config(text=word_data["word"])
        self.load_image_for_single_slot(word_data["image"])
        self.word_count_label.config(text=f"Palabra {self.current_word_in_phrase_index + 1} de {total}")

        self.play_word_audio(word_data["word"])

    def load_image_for_single_slot(self, filename):
        path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                # Escalado inteligente
                max_w = self.image_max_size
                max_h = self.image_max_size
                ratio = min(max_w / img.width, max_h / img.height)
                new_w = int(img.width * ratio)
                new_h = int(img.height * ratio)
                
                photo = ImageTk.PhotoImage(img.resize((new_w, new_h), Image.Resampling.LANCZOS))
                self.single_main_image_label.config(image=photo, text="")
                self.single_main_image_label.image = photo
            except:
                self.single_main_image_label.config(image="", text="Error Img")
        else:
            self.single_main_image_label.config(image="", text="No Img")

    def _generate_audio(self, text, path):
        if not os.path.exists(path):
            try:
                tts = gTTS(text=text, lang="es", slow=False)
                tts.save(path)
            except Exception as e: print(e); return
        
        try:
            if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e: print(e)

    def play_word_audio(self, text):
        # Limpiar texto para nombre de archivo
        clean = "".join(c for c in text.lower() if c.isalnum())
        path = os.path.join(self.audio_cache_dir, f"{clean}.mp3")
        threading.Thread(target=self._generate_audio, args=(text, path)).start()

    def repeat_current_word(self):
        phrase_data = self.get_current_phrase_data()
        if phrase_data:
            word = phrase_data["words"][self.current_word_in_phrase_index]["word"]
            self.play_word_audio(word)

    def next_word_in_phrase(self):
        phrase_data = self.get_current_phrase_data()
        if not phrase_data: return

        if self.current_word_in_phrase_index < len(phrase_data["words"]) - 1:
            self.current_word_in_phrase_index += 1
            self.update_display()
        else:
            self._show_phrase_complete_screen()

    def prev_word_in_phrase(self):
        if self.current_word_in_phrase_index > 0:
            self.current_word_in_phrase_index -= 1
            self.update_display()

    def next_phrase(self):
        if self.current_phrase_index < len(self.available_phrases) - 1:
            self.current_phrase_index += 1
        else:
            self.shuffle_available_phrases()
        self.current_word_in_phrase_index = 0
        self.update_display()

    def _show_phrase_complete_screen(self):
        win = tk.Toplevel(self.master)
        win.title("¡Bien!")
        w, h = int(400 * self.scale), int(250 * self.scale)
        win.geometry(f"{w}x{h}")
        win.attributes("-topmost", True)
        win.grab_set()
        
        frame = tk.Frame(win, bg="white", padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="¡Muy Bien!", font=self.title_font, bg="white", fg="#FF5757").pack(pady=5)
        
        phrase = self.get_current_phrase_data()["phrase_text"]
        tk.Label(frame, text=f"Frase: {phrase}", font=self.count_font, bg="white", wraplength=w-40).pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=10)
        
        def action(act):
            win.destroy()
            if act == "next": self.next_phrase()
            elif act == "menu": self.go_to_menu()

        tk.Button(btn_frame, text="Siguiente", bg="#FF6B6B", fg="white", font=self.small_button_font,
                  command=lambda: action("next")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Menú", bg="#5B84B1", fg="white", font=self.small_button_font,
                  command=lambda: action("menu")).pack(side=tk.LEFT, padx=10)

        win.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        win.geometry(f"+{x}+{y}")

    def go_to_menu(self):
        self.master.destroy()
        path = os.path.join(SCRIPT_DIR, "..", "menu", "menu_simondice.py")
        if not os.path.exists(path):
             path = os.path.join(SCRIPT_DIR, "..", "menu_simondice.py")
        
        if os.path.exists(path):
            subprocess.Popen([sys.executable, path])
        else:
            messagebox.showerror("Error", f"Menú no encontrado:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    game = FrasesGame(root)
    root.mainloop()