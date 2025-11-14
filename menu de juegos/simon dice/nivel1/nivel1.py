import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import subprocess
import pygame.mixer
from gtts import gTTS
import threading

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

        # --- AÑADIDO: Atajo para salir de pantalla completa (Escape) ---
        master.bind("<Escape>", lambda e: master.attributes("-fullscreen", False))

        # ✅ Aplicar escala
        self._apply_scaling()

        # --- AÑADIDO: Definir el directorio actual para rutas relativas ---
        self.current_dir = os.path.dirname(__file__)

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
            # {"word": "BANANA", "syllables": ["BA", "NA", "NA"], "image": "banana.png"}, # Si añades banana, recuerda la imagen
        ]
        
        self.current_word_list = []
        self.current_word_index = 0
        self.current_syllable_index = 0
        self.previous_word_data = None

        self.shuffle_words()

        # --- Inicializar pygame mixer ---
        try:
            pygame.mixer.init()
            print("pygame.mixer inicializado correctamente.")
        except pygame.error as e:
            print(f"Error al inicializar pygame.mixer: {e}")
            messagebox.showerror("Error de Audio", f"No se pudo inicializar el sistema de audio. {e}")

        # --- Carpeta para guardar los audios generados ---
        self.audio_cache_dir = os.path.join(self.current_dir, "audio_cache") # Usa self.current_dir
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)
            print(f"Carpeta '{self.audio_cache_dir}' creada para audios generados.")

        self.canvas = tk.Canvas(master, bg="#FAD4D4", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, radius=int(20 * self.scale), fill="white", outline="white")
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Título "SIMÓN DICE" y su icono de sonido ---
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")

        try:
            # --- CORREGIDO: Ruta absoluta y coma extra en resize ---
            speaker_icon_path = os.path.join(self.current_dir, "sonido.jpg")
            speaker_icon_pil = Image.open(speaker_icon_path).resize((self.icon_size, self.icon_size), Image.Resampling.LANCZOS)
            self.speaker_title_photo = ImageTk.PhotoImage(speaker_icon_pil) 
            self.speaker_title_label = tk.Label(self.title_container, image=self.speaker_title_photo, bg="white")
            self.speaker_title_label.pack(side=tk.LEFT, padx=5)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}'.")
        except Exception as e:
            print(f"Error al cargar el icono de sonido del título: {e}")
        
        self.title_label = tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white")
        self.title_label.pack(side=tk.LEFT)

        self.main_image_label = tk.Label(self.inner_frame, bg="white")
        self.main_image_label.place(relx=0.5, rely=0.4, anchor="center")

        # --- Contenedor para la sílaba y su icono de sonido ---
        self.syllable_container = tk.Frame(self.inner_frame, bg="white")
        self.syllable_container.place(relx=0.5, rely=0.65, anchor="center")

        try:
            # --- CORREGIDO: Ruta absoluta para el icono de sonido de la sílaba ---
            speaker_icon_path = os.path.join(self.current_dir, "sonido.jpg")
            speaker_icon_pil = Image.open(speaker_icon_path).resize((self.icon_size, self.icon_size), Image.Resampling.LANCZOS) # Usa self.icon_size para escalar
            self.speaker_syllable_photo = ImageTk.PhotoImage(speaker_icon_pil) 
            self.speaker_syllable_label = tk.Label(self.syllable_container, image=self.speaker_syllable_photo, bg="white")
            self.speaker_syllable_label.pack(side=tk.LEFT, padx=5)
            # Enlazar el evento de clic para reproducir el audio de la sílaba
            self.speaker_syllable_label.bind("<Button-1>", self._on_syllable_speaker_click)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}' para la sílaba.")
        except Exception as e:
            print(f"Error al cargar el icono de sonido de la sílaba: {e}")
        
        self.syllable_label = tk.Label(self.syllable_container, text="", font=self.syllable_font, bg="white")
        self.syllable_label.pack(side=tk.LEFT)

        # --- Contenedor para los botones "Nivel 1" y "Volver al Menú" ---
        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.85, anchor="center")

        # ---------- Botón REPETIR (circular, arriba-derecha) ----------
        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, radius=int(self.repeat_button_size / 2), # Usa self.repeat_button_size
                            fill="#FFB347", outline="#FFB347")
        # --- CORREGIDO: Fuente escalada ---
        self.repeat_circle.create_text(self.repeat_button_size / 2, self.repeat_button_size / 2, text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.05, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_syllable())

        # Botón "Nivel 1" (ahora dentro del contenedor)
        self.level_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=self.level_button_width, height=self.level_button_height)
        self.draw_rounded_rect(self.level_button_canvas, 0, 0, self.level_button_width, self.level_button_height, radius=int(15 * self.scale), fill="#FF6B6B", outline="#FF6B6B") # Usa medidas escaladas
        self.level_button_text = self.level_button_canvas.create_text(self.level_button_width / 2, self.level_button_height / 2, text="Nivel 1", font=self.button_font, fill="white") # Usa medidas escaladas
        self.level_button_canvas.bind("<Button-1>", lambda e: self.next_word_or_syllable()) # Mantiene la funcionalidad
        self.level_button_canvas.pack(side=tk.LEFT, padx=int(10 * self.scale)) # Empaqueta a la izquierda con padding escalado

        # NUEVO Botón "Volver al Menú"
        self.menu_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=self.menu_button_width, height=self.menu_button_height)
        self.draw_rounded_rect(self.menu_button_canvas, 0, 0, self.menu_button_width, self.menu_button_height, radius=int(15 * self.scale), fill="#5B84B1", outline="#5B84B1") # Usa medidas escaladas
        self.menu_button_text = self.menu_button_canvas.create_text(self.menu_button_width / 2, self.menu_button_height / 2, text="Volver al Menú", font=self.button_font, fill="white") # Usa self.button_font para consistencia
        self.menu_button_canvas.bind("<Button-1>", self.go_to_menu) # Enlaza a una nueva función
        self.menu_button_canvas.pack(side=tk.LEFT, padx=int(10 * self.scale)) # Empaqueta a la izquierda con padding escalado

        # Botón "Siguiente" (flecha derecha)
        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font, # Usa self.arrow_font
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_word_or_syllable)
        self.next_button.place(relx=0.75, rely=0.4, anchor="center")

        # Botón "Anterior" (flecha izquierda)
        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font, # Usa self.arrow_font
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_syllable)
        self.prev_button.place(relx=0.25, rely=0.4, anchor="center")

        self.syllable_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white") # Usa self.count_font
        self.syllable_count_label.place(relx=0.9, rely=0.9, anchor="e")

        # Icono de oreja "escuchar.png"
        try:
            # --- CORREGIDO: Ruta absoluta para el icono de oreja ---
            ear_icon_path = os.path.join(self.current_dir, "escuchar.png")
            original_ear_img_pil = Image.open(ear_icon_path)
            desired_ear_height = self.ear_height
            aspect_ratio_ear = original_ear_img_pil.width / original_ear_img_pil.height
            desired_ear_width = int(desired_ear_height * aspect_ratio_ear)

            self.ear_img_pil = original_ear_img_pil.resize((desired_ear_width, desired_ear_height), Image.Resampling.LANCZOS)
            self.ear_photo = ImageTk.PhotoImage(self.ear_img_pil)
            self.ear_label = tk.Label(self.inner_frame, image=self.ear_photo, bg="white")
            self.ear_label.place(relx=0.08, rely=0.85, anchor="w")
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{ear_icon_path}'. Asegúrate de que esté en la misma carpeta.")
            self.ear_label = tk.Label(self.inner_frame, text="[Escuchar]", font=self.count_font, bg="white") # Usa self.count_font
            self.ear_label.place(relx=0.08, rely=0.92, anchor="w")
        except Exception as e:
            print(f"Error al cargar el icono de oreja: {e}")


        self.update_display()

    def _apply_scaling(self):
        scale = self.scale

        # Tamaños principales
        self.canvas_width = int(700 * scale)
        self.canvas_height = int(500 * scale)
        self.image_width = int(200 * scale) # Se usará en load_word_image
        
        # Fuentes
        self.title_font = ("Arial", int(24 * scale), "bold")
        self.syllable_font = ("Arial", int(36 * scale), "bold")
        self.button_font = ("Arial", int(16 * scale), "bold")
        self.small_button_font = ("Arial", int(12 * scale), "bold")
        self.count_font = ("Arial", int(14 * scale))
        self.arrow_font = ("Arial", int(30 * scale), "bold")
        self.repeat_font = ("Arial", int(18 * scale))
        
        # Botones
        self.level_button_width = int(150 * scale)
        self.level_button_height = int(50 * scale)
        self.menu_button_width = int(200 * scale)
        self.menu_button_height = int(50 * scale)
        self.repeat_button_size = int(50 * scale)
        
        # Íconos
        self.icon_size = int(30 * scale)
        self.ear_height = int(100 * scale)

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
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

    def shuffle_words(self):
        """Baraja la lista de palabras asegurando que no se repita la anterior."""
        shuffled_list = self.all_words_data[:]
        random.shuffle(shuffled_list)

        if self.previous_word_data and shuffled_list[0] == self.previous_word_data:
            if len(shuffled_list) > 1:
                first_word = shuffled_list.pop(0)
                shuffled_list.append(first_word)
            else:
                pass
        
        self.current_word_list = shuffled_list
        self.current_word_index = 0
        self.current_syllable_index = 0
        self.previous_word_data = None

    def _generate_and_play_audio(self, syllable_text, audio_path):
        """Genera el audio con gTTS y lo reproduce, guarda el archivo si no existe."""
        if not os.path.exists(audio_path):
            try:
                print(f"Generando audio para: {syllable_text} -> {audio_path}")

                if len(syllable_text) <= 4 and not self.is_known_good_syllable(syllable_text):
                    text_to_synthesize = " ".join(list(syllable_text.lower()))
                else:
                    text_to_synthesize = syllable_text.lower()

                tts = gTTS(text=text_to_synthesize, lang='es', slow=True)
                tts.save(audio_path)
            except Exception as e:
                print(f"Error al generar el audio para '{syllable_text}': {e}")
                return

        # ---- reproducir ----
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            print(f"Reproduciendo lento: {audio_path}")
        except Exception as e:
            print(f"Error al reproducir '{audio_path}': {e}")

    def is_known_good_syllable(self, syllable):
        # La línea completa con las sílabas que gTTS debería pronunciar bien.
        good_syllables = [
            "A", "SUS", "TA", "DO", "CA", "MI", "NAR", "CO", "CI", "NA", "COMER",
            "MO", "VER", "SE", "DOR", "MIR", "O", "IR", "FE", "LIZ", "NA", "DAR",
            "MIRAR", "OBSERVAR", "SAL", "TAR", "A", "GA", "RRAR", 
            "TE", "NER", "TRIS", "TE", "QUI", "E", "RO",
            # --- SÍLABAS DE LAS NUEVAS PALABRAS ---
            "A", "BRA", "ZO", "BA", "NA"
        ]
        return syllable.upper() in good_syllables
        
    def play_syllable_audio(self, syllable):
        """Gestiona la reproducción de audio, generando con gTTS si es necesario."""
        # Limpiar la sílaba para el nombre del archivo (ej. "BAÑO" -> "bano.mp3")
        clean_syllable_for_filename = syllable.lower().replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        audio_path = os.path.join(self.audio_cache_dir, f"{clean_syllable_for_filename}.mp3")

        # Usar un hilo para generar el audio para no bloquear la interfaz
        # El audio se generará y se reproducirá en el hilo.
        # Si el archivo ya existe, solo se reproducirá.
        threading.Thread(target=self._generate_and_play_audio, args=(syllable, audio_path)).start()


    def _on_syllable_speaker_click(self, event):
        """Maneja el clic en el icono del parlante de la sílaba para reproducir su audio."""
        if not self.current_word_list:
            return
        current_word_data = self.current_word_list[self.current_word_index]
        current_syllables = current_word_data["syllables"]
        if self.current_syllable_index < len(current_syllables):
            current_syllable_text = current_syllables[self.current_syllable_index]
            self.play_syllable_audio(current_syllable_text)


    def update_display(self):
        if not self.current_word_list:
            self.shuffle_words()
            if not self.current_word_list:
                self.syllable_label.config(text="No hay palabras")
                self.syllable_count_label.config(text="")
                self.main_image_label.config(image="", text="[Sin imagen]", font=("Arial", 12))
                return

        current_word_data = self.current_word_list[self.current_word_index]
        current_syllables = current_word_data["syllables"]
        
        if self.current_syllable_index >= len(current_syllables):
            self.current_syllable_index = 0

        current_syllable_text = current_syllables[self.current_syllable_index]
        total_syllables_word = len(current_syllables)

        self.syllable_label.config(text=current_syllable_text)
        self.syllable_count_label.config(text=f"{self.current_syllable_index + 1}/{total_syllables_word}")

        self.load_word_image(current_word_data["image"])
        
        # Reproducir el audio de la sílaba actual al actualizar la pantalla
        self.play_syllable_audio(current_syllable_text)


    def load_word_image(self, image_filename):
        try:
            # --- CORREGIDO: Usar self.current_dir para la ruta de la imagen de la palabra ---
            image_path = os.path.join(self.current_dir, image_filename)
            original_img_pil = Image.open(image_path)
            
            # --- CORREGIDO: Usar self.image_width para el redimensionamiento escalado ---
            desired_width = self.image_width 
            aspect_ratio = original_img_pil.width / original_img_pil.height
            desired_height = int(desired_width / aspect_ratio)

            img_pil_resized = original_img_pil.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            self.word_image_tk = ImageTk.PhotoImage(img_pil_resized)
            self.main_image_label.config(image=self.word_image_tk)
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{image_filename}'.")
            self.main_image_label.config(image="", text="[Imagen no encontrada]", font=("Arial", 12))
        except Exception as e:
            print(f"Error al cargar la imagen {image_filename}: {e}")
            self.main_image_label.config(image="", text="[Error de imagen]", font=("Arial", 12))

    def next_word_or_syllable(self):
        current_word_data = self.current_word_list[self.current_word_index]
        current_syllables = current_word_data["syllables"]

        # ¿Estoy en la última sílaba?
        if self.current_syllable_index == len(current_syllables) - 1:
            self._show_word_complete_screen(current_word_data['word'])
            return  # No pasamos solo; esperamos al botón

        # Si todavía quedan sílabas
        self.current_syllable_index += 1
        self.update_display()

    def prev_syllable(self):
        if not self.current_word_list: 
            messagebox.showinfo("Juego", "No hay palabras para retroceder.")
            return

        # La condición self.current_word_index < 0 nunca se cumplirá aquí si se inicializa a 0 o más
        # Esta parte se puede simplificar o mover si realmente quieres un bucle completo.
        # Por ahora, la mantengo ya que no causa un error y tiene un messagebox informativo.
        if self.current_word_index < 0: 
            self.current_word_index = 0 
            self.current_syllable_index = 0
            self.update_display()
            return

        current_word_data = self.current_word_list[self.current_word_index]
        current_syllables = current_word_data["syllables"]

        if self.current_syllable_index > 0:
            self.current_syllable_index -= 1
        else:
            if self.current_word_index > 0:
                self.current_word_index -= 1
                current_word_data_prev = self.current_word_list[self.current_word_index]
                self.current_syllable_index = len(current_word_data_prev["syllables"]) - 1
            else:
                messagebox.showinfo("Juego", "¡Estás en la primera sílaba de la primera palabra!")

        self.update_display()

    def _show_word_complete_screen(self, completed_word):
        win_screen = tk.Toplevel(self.master)
        win_screen.title("¡Palabra Completada!")
        win_width = int(400 * self.scale)
        win_height = int(250 * self.scale)
        win_screen.geometry(f"{win_width}x{win_height}")
        win_screen.resizable(False, False)
        win_screen.attributes("-topmost", True) 
        win_screen.grab_set() 

        win_screen.protocol("WM_DELETE_WINDOW", lambda: self._on_complete_screen_close(win_screen))

        frame = tk.Frame(win_screen, bg="white", padx=int(20 * self.scale), pady=int(20 * self.scale)) # Escalado de padding
        frame.pack(expand=True, fill="both")

        message_label = tk.Label(frame, text="¡Felicidades!",
                                 font=("Arial", int(24 * self.scale), "bold"), # Escalado de fuente
                                 bg="white", fg="#FF5757") 
        message_label.pack(pady=(int(10 * self.scale), int(5 * self.scale))) # Escalado de padding

        sub_message_label = tk.Label(frame, text=f"¡Completaste la palabra '{completed_word}'! 🎉",
                                      font=("Arial", int(14 * self.scale)), # Escalado de fuente
                                      bg="white", fg="#FF5757")
        sub_message_label.pack(pady=(0, int(20 * self.scale))) # Escalado de padding

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=int(10 * self.scale)) # Escalado de padding

        next_button = tk.Button(button_frame, text="Siguiente Palabra",
                                font=self.small_button_font,
                                bg="#FF6B6B", fg="white", 
                                activebackground="#E04D4D",
                                relief="flat", bd=0, padx=int(15 * self.scale), pady=int(8 * self.scale), # Escalado de padding
                                command=lambda: self._handle_complete_action("next", win_screen))
        next_button.pack(side="left", padx=int(10 * self.scale)) # Escalado de padding

        menu_button = tk.Button(button_frame, text="Volver al Menú",
                                font=self.small_button_font, # Usar small_button_font para consistencia
                                bg="#5B84B1", fg="white", 
                                activebackground="#4A6E94",
                                relief="flat", bd=0, padx=int(15 * self.scale), pady=int(8 * self.scale), # Escalado de padding
                                command=lambda: self._handle_complete_action("menu", win_screen))
        menu_button.pack(side="left", padx=int(10 * self.scale)) # Escalado de padding

        win_screen.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (win_screen.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (win_screen.winfo_height() // 2)
        win_screen.geometry(f"+{x}+{y}")

    def _handle_complete_action(self, action, win_screen):
        win_screen.destroy()
        self.master.grab_release()
        if action == "next":
            self._advance_to_next_word()   # ⬅️ avanzamos solo ahora
        elif action == "menu":
            self.go_to_menu() 
    
    def _on_complete_screen_close(self, win_screen):
        win_screen.destroy()
        self.master.grab_release()
    
    def _advance_to_next_word(self):
        # Guardamos la palabra que acaba de terminar
        self.previous_word_data = self.current_word_list[self.current_word_index]

        # Pasamos a la siguiente (con bucle si llegamos al final)
        self.current_word_index += 1
        if self.current_word_index >= len(self.current_word_list):
            self.shuffle_words()

        # Reiniciamos sílabas y refrescamos
        self.current_syllable_index = 0
        self.update_display()
    
    def repeat_current_syllable(self):
        """Vuelve a decir la sílaba que está en pantalla."""
        if not self.current_word_list:
            return
        syllable = self.current_word_list[self.current_word_index]["syllables"][self.current_syllable_index]
        self.play_syllable_audio(syllable)

    def go_to_menu(self, event=None):
        self.master.destroy() 

        try:
            current_script_dir = os.path.dirname(__file__)
            print(f"DEBUG: current_script_dir = {current_script_dir}") 
            # current_script_dir ahora es 'simon dice/nivel1'

            # Para llegar a 'simon dice', necesitamos el directorio padre de 'nivel1'
            simon_dice_root_dir = os.path.dirname(current_script_dir)
            print(f"DEBUG: simon_dice_root_dir = {simon_dice_root_dir}") 
            # simon_dice_root_dir ahora es 'simon dice'

            # Ahora, desde 'simon dice', podemos ir a la carpeta 'menu'
            menu_simondice_path = os.path.join(simon_dice_root_dir, "menu", "menu_simondice.py")
            print(f"DEBUG: menu_simondice_path construida = {menu_simondice_path}") 

            if not os.path.exists(menu_simondice_path):
                messagebox.showerror("Error de Ruta",
                                     f"El archivo no existe en la ruta calculada: {menu_simondice_path}")
                print(f"DEBUG: ¡ERROR! El archivo no se encontró en: {menu_simondice_path}") 
                return 

            subprocess.Popen(["python", menu_simondice_path])
        except FileNotFoundError:
            messagebox.showerror("Error al iniciar el menú",
                                 f"No se pudo encontrar el ejecutable 'python' o el archivo del menú:\n'{menu_simondice_path}'\n"
                                 "Asegúrate de que Python esté configurado en tu PATH o revisa la ruta del script del menú.")
            print(f"DEBUG: Error FileNotFoundError. Ruta intentada: {menu_simondice_path}")
        except Exception as e:
            messagebox.showerror("Error al iniciar el menú", f"Ocurrió un error inesperado al intentar abrir el menú: {e}")
            print(f"DEBUG: Error inesperado: {e}. Ruta intentada: {menu_simondice_path}")


# Para ejecutar el juego
root = tk.Tk()
game = SilabasGame(root)
root.mainloop()