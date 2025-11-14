import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import subprocess
import pygame.mixer
from gtts import gTTS
import threading

class PalabrasGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Palabras")
        
        # --- AÑADIDO: Lógica de escalado y fullscreen ---
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1000  # Tus dimensiones base originales
        base_height = 700
        self.scale = min(screen_width / base_width, screen_height / base_height)

        master.attributes("-fullscreen", True)
        master.configure(bg="#FF5757")

        # --- AÑADIDO: Atajo para salir de pantalla completa (Escape) ---
        master.bind("<Escape>", lambda e: master.attributes("-fullscreen", False))

        # --- AÑADIDO: Aplicar escalado a fuentes y widgets ---
        self._apply_scaling()
        
        # --- AÑADIDO: Definir el directorio actual para rutas relativas ---
        self.current_dir = os.path.dirname(__file__)

        # Lista de todas las palabras disponibles
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

        self.available_words = [] # Lista de palabras disponibles para la selección actual
        self.shuffle_available_words() # Llenar y barajar al inicio 
        
        # --- CORREGIDO: Inicialización de pygame mixer (ya está, pero reitero) ---
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
                print("pygame.mixer inicializado.")
            except pygame.error as e:
                print(f"Error pygame.mixer: {e}")
        
        # --- CORREGIDO: Ruta absoluta para audio_cache_words ---
        self.audio_cache_dir = os.path.join(self.current_dir, "audio_cache_words")
        if not os.path.exists(self.audio_cache_dir):
            os.makedirs(self.audio_cache_dir)

        self.current_word_index = 0
        self.recent_words_data = [] # Para almacenar las 3 últimas palabras mostradas individualmente
        self.game_state = "individual_word" # "individual_word" o "group_summary"
        self.individual_word_counter = 0 # Cuenta cuántas palabras individuales se han mostrado en el ciclo actual

        # --- CORREGIDO: Dimensiones del canvas escaladas ---
        self.canvas = tk.Canvas(master, bg="#FF5757", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=self.canvas_width, height=self.canvas_height)
        self.draw_rounded_rect(self.canvas, 0, 0, self.canvas_width, self.canvas_height, radius=int(20 * self.scale), fill="white", outline="white")
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Título "SIMÓN DICE" y su icono de sonido ---
        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")

        try:
            # --- CORREGIDO: Ruta absoluta para speaker_icon_path ---
            speaker_icon_path = os.path.join(self.current_dir, "sonido.jpg")
            speaker_icon_pil = Image.open(speaker_icon_path).resize((self.icon_size_title, self.icon_size_title), Image.Resampling.LANCZOS)
            self.speaker_title_photo = ImageTk.PhotoImage(speaker_icon_pil)
            self.speaker_title_label = tk.Label(self.title_container, image=self.speaker_title_photo, bg="white")
            self.speaker_title_label.pack(side=tk.LEFT, padx=int(5 * self.scale))
            self.title_label = tk.Label(self.title_container, text="SIMÓN DICE", font=self.title_font, bg="white")
            self.title_label.pack(side=tk.LEFT)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}'. Usando emoticono en el título.")
            self.title_label = tk.Label(self.title_container, text="🔊SIMÓN DICE", font=self.title_font, bg="white")
            self.title_label.pack(side=tk.LEFT)
        except Exception as e:
            print(f"Error al cargar el icono del título: {e}. Usando emoticono en el título.")
            self.title_label = tk.Label(self.title_container, text="🔊SIMÓN DICE", font=self.title_font, bg="white")
            self.title_label.pack(side=tk.LEFT)


        # --- Contenedor para UNA SOLA IMAGEN y PALABRA (para estado "individual_word") ---
        self.single_word_display_frame = tk.Frame(self.inner_frame, bg="white")
        # Este frame se place/unplace según el estado

        self.single_main_image_label = tk.Label(self.single_word_display_frame, bg="white")
        self.single_main_image_label.pack(pady=int(10 * self.scale))

        self.single_word_text_container = tk.Frame(self.single_word_display_frame, bg="white")
        self.single_word_text_container.pack(pady=int(5 * self.scale))

        try:
            # --- CORREGIDO: Ruta absoluta para speaker_icon_path ---
            speaker_icon_path = os.path.join(self.current_dir, "sonido.jpg")
            speaker_icon_pil = Image.open(speaker_icon_path).resize((self.icon_size_word, self.icon_size_word), Image.Resampling.LANCZOS)
            self.speaker_single_word_photo = ImageTk.PhotoImage(speaker_icon_pil)
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, image=self.speaker_single_word_photo, bg="white")
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=int(5 * self.scale))
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}' para la palabra individual. Usando emoticono.")
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, text="🔊", bg="white", font=self.word_font) # Usar self.word_font
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=int(5 * self.scale))
        except Exception as e:
            print(f"Error al cargar el icono de palabra individual: {e}. Usando emoticono.")
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, text="🔊", bg="white", font=self.word_font)
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=int(5 * self.scale))

        # --- CORREGIDO: Fuente escalada para single_word_label ---
        self.single_word_label = tk.Label(self.single_word_text_container, text="", font=self.word_font, bg="white")
        self.single_word_label.pack(side=tk.LEFT)


        # --- Contenedor para las TRES IMÁGENES y TRES PALABRAS (para estado "group_summary") ---
        self.group_summary_display_frame = tk.Frame(self.inner_frame, bg="white")
        # Este frame se place/unplace según el estado

        self.image_labels = []
        self.word_display_containers = []
        self.speaker_word_labels = []
        self.word_labels = []

        for i in range(3):
            # --- CORREGIDO: Padding escalado para item_frame ---
            item_frame = tk.Frame(self.group_summary_display_frame, bg="white", padx=int(10 * self.scale), pady=int(10 * self.scale))
            item_frame.pack(side=tk.LEFT, padx=int(15 * self.scale))

            img_label = tk.Label(item_frame, bg="white")
            img_label.pack(pady=int(5 * self.scale)) # Padding escalado
            self.image_labels.append(img_label)

            word_display_container = tk.Frame(item_frame, bg="white")
            word_display_container.pack(pady=int(5 * self.scale)) # Padding escalado
            self.word_display_containers.append(word_display_container)

            try:
                # --- CORREGIDO: Ruta absoluta para speaker_icon_path ---
                speaker_icon_path = os.path.join(self.current_dir, "sonido.jpg")
                speaker_icon_pil = Image.open(speaker_icon_path).resize((self.icon_size_summary, self.icon_size_summary), Image.Resampling.LANCZOS)
                setattr(self, f"speaker_group_word_photo_{i}", ImageTk.PhotoImage(speaker_icon_pil))
                speaker_word_label = tk.Label(word_display_container, image=getattr(self, f"speaker_group_word_photo_{i}"), bg="white")
            except FileNotFoundError:
                speaker_word_label = tk.Label(word_display_container, text="🔊", bg="white", font=self.summary_word_font) # Usar self.summary_word_font
            except Exception as e:
                speaker_word_label = tk.Label(word_display_container, text="🔊", bg="white", font=self.summary_word_font)

            speaker_word_label.pack(side=tk.LEFT, padx=int(3 * self.scale)) # Padding escalado
            self.speaker_word_labels.append(speaker_word_label)

            # ---- mismo empaquetado para todos ----
            # Enlazar el evento de clic en el loop, asegurándose de que la 'word' sea la correcta.
            # Esto se manejará mejor en update_display() después de que las palabras estén cargadas.
            # Por ahora, se crea un lambda sin la palabra, luego se actualiza su comando.

            word_label = tk.Label(word_display_container, text="", font=self.summary_word_font, bg="white") # Usar self.summary_word_font
            word_label.pack(side=tk.LEFT)
            self.word_labels.append(word_label)


        # --- Contenedor para los botones "Nivel 1" y "Volver al Menú" ---
        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.85, anchor="center")

        # Botón "Nivel 1" (ahora dentro del contenedor)
        self.level_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=self.level_button_width, height=self.level_button_height)
        self.draw_rounded_rect(self.level_button_canvas, 0, 0, self.level_button_width, self.level_button_height, radius=int(15 * self.scale), fill="#FF6B6B", outline="#FF6B6B")
        self.level_button_text = self.level_button_canvas.create_text(self.level_button_width / 2, self.level_button_height / 2, text="Nivel 2", font=self.button_font, fill="white")
        self.level_button_canvas.bind("<Button-1>", lambda e: self.next_step())
        self.level_button_canvas.pack(side=tk.LEFT, padx=int(10 * self.scale))

        # Botón "Volver al Menú"
        self.menu_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=self.menu_button_width, height=self.menu_button_height)
        self.draw_rounded_rect(self.menu_button_canvas, 0, 0, self.menu_button_width, self.menu_button_height, radius=int(15 * self.scale), fill="#5B84B1", outline="#5B84B1")
        self.menu_button_text = self.menu_button_canvas.create_text(self.menu_button_width / 2, self.menu_button_height / 2, text="Volver al Menú", font=self.button_font, fill="white")
        self.menu_button_canvas.bind("<Button-1>", self.go_to_menu)
        self.menu_button_canvas.pack(side=tk.LEFT, padx=int(10 * self.scale))

        # Botón "Siguiente" (flecha derecha)
        self.next_button = tk.Button(self.inner_frame, text=">", font=self.arrow_font,
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_step)
        self.next_button.place(relx=0.85, rely=0.5, anchor="center")

        # Botón "Anterior" (flecha izquierda)
        self.prev_button = tk.Button(self.inner_frame, text="<", font=self.arrow_font,
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_step)
        self.prev_button.place(relx=0.15, rely=0.5, anchor="center")

        # --- CORREGIDO: Fuente escalada para word_count_label ---
        self.word_count_label = tk.Label(self.inner_frame, text="", font=self.count_font, bg="white")
        self.word_count_label.place(relx=0.9, rely=0.9, anchor="e")

        # ---------- Botón REPETIR (circular, arriba-derecha) ----------
        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, width=self.repeat_button_size, height=self.repeat_button_size)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, self.repeat_button_size, self.repeat_button_size, radius=int(self.repeat_button_size / 2),
                            fill="#FFB347", outline="#FFB347")
        self.repeat_circle.create_text(self.repeat_button_size / 2, self.repeat_button_size / 2, text="🔊", font=self.repeat_font, fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.05, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_word())

        # Icono de oreja "escuchar.png"
        try:
            # --- CORREGIDO: Ruta absoluta para ear_icon_path ---
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
            self.ear_label = tk.Label(self.inner_frame, text="[Escuchar]", font=self.count_font, bg="white")
            self.ear_label.place(relx=0.08, rely=0.92, anchor="w")
        except Exception as e:
            print(f"Error al cargar el icono de oreja: {e}")

        self.update_display()

    # --- AÑADIDO: Método para aplicar escalado a todos los elementos ---
    def _apply_scaling(self):
        scale = self.scale

        # Tamaños principales
        self.canvas_width = int(900 * scale)
        self.canvas_height = int(600 * scale)
        self.image_width_single = int(250 * scale) # Para la palabra individual
        self.image_width_group = int(150 * scale)  # Para el resumen de grupo
        
        # Fuentes
        self.title_font = ("Arial", int(36 * scale), "bold")
        self.word_font = ("Arial", int(24 * scale), "bold") # Era 16, ahora 24
        self.summary_word_font = ("Arial", int(18 * scale), "bold") # Era 15, ahora 18
        self.button_font = ("Arial", int(16 * scale), "bold")
        self.small_button_font = ("Arial", int(12 * scale), "bold") # Para la pantalla de felicitación
        self.count_font = ("Arial", int(14 * scale)) # Era 10, ahora 14
        self.arrow_font = ("Arial", int(30 * scale), "bold")
        self.repeat_font = ("Arial", int(18 * scale))
        
        # Botones
        self.level_button_width = int(150 * scale)
        self.level_button_height = int(50 * scale)
        self.menu_button_width = int(200 * scale)
        self.menu_button_height = int(50 * scale)
        self.repeat_button_size = int(50 * scale)
        
        # Íconos
        self.icon_size_title = int(40 * scale)    # Para el título
        self.icon_size_word = int(45 * scale)     # Para palabra individual
        self.icon_size_summary = int(30 * scale)  # Para el resumen de grupo
        self.ear_height = int(80 * scale)


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

    def shuffle_available_words(self):
        """Baraja todas las palabras y las pone en la lista de disponibles."""
        self.available_words = self.all_words_data[:]
        random.shuffle(self.available_words)
        self.current_word_index = 0 # Reiniciar el índice para la nueva tanda

    def get_next_individual_word(self):
        """Obtiene la siguiente palabra individual de la lista disponible."""
        if not self.available_words:
            self.shuffle_available_words() # Si se acaban, baraja de nuevo
            if not self.available_words: # Caso borde si all_words_data está vacío
                return None

        # Asegurarse de que current_word_index no exceda el límite
        if self.current_word_index >= len(self.available_words):
            self.shuffle_available_words() # Si hemos mostrado todas las palabras, barajar de nuevo
            if not self.available_words:
                return None # No hay palabras disponibles

        word_data = self.available_words[self.current_word_index]
        self.current_word_index += 1
        return word_data

    def update_display(self):
        # Limpiar ambos frames antes de mostrar el correcto
        self.single_word_display_frame.place_forget()
        self.group_summary_display_frame.place_forget()

        if self.game_state == "individual_word":
            self.display_individual_word()
        elif self.game_state == "group_summary":
            self.display_group_summary()

    def display_individual_word(self):
        self.single_word_display_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.individual_word_counter < len(self.recent_words_data):
            # Si estamos retrocediendo, mostramos una palabra de recent_words_data
            word_data = self.recent_words_data[self.individual_word_counter]
        else:
            # Si estamos avanzando, obtenemos una nueva palabra
            word_data = self.get_next_individual_word()
            if word_data:
                self.recent_words_data.append(word_data) # Añadir a la lista de recientes
            else:
                self.single_word_label.config(text="No hay palabras disponibles.")
                self.load_image_for_single_slot(None)
                self.word_count_label.config(text="Juego Terminado")
                return

        self.single_word_label.config(text=word_data["word"])
        self.play_word_audio(word_data["word"])
        self.load_image_for_single_slot(word_data["image"])
        self.word_count_label.config(text=f"Palabra {self.individual_word_counter + 1} de 3")


    def display_group_summary(self):
        self.group_summary_display_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Reproduce el resumen de palabras después de un breve retraso para que la UI se actualice
        self.master.after(500, self.speak_summary_words) 

        if not self.recent_words_data:
            for i in range(3):
                self.word_labels[i].config(text="")
                self.image_labels[i].config(image="")
            self.word_count_label.config(text="No hay palabras recientes.")
            return

        for i in range(3):
            if i < len(self.recent_words_data):
                word_data = self.recent_words_data[i]
                self.word_labels[i].config(text=word_data["word"])
                self.load_image_for_group_slot(i, word_data["image"])
                
                # --- AÑADIDO: Actualizar el comando del botón del altavoz para el resumen ---
                # Usar lambda para capturar la palabra correcta para cada botón
                self.speaker_word_labels[i].bind("<Button-1>", lambda e, w=word_data["word"]: self.play_word_audio(w))
            else:
                self.word_labels[i].config(text="")
                self.image_labels[i].config(image="")
                self.speaker_word_labels[i].unbind("<Button-1>") # Desactivar si no hay palabra
        self.word_count_label.config(text="Resumen de palabras")

    def load_image_for_single_slot(self, image_filename):
        try:
            if not image_filename:
                self.single_main_image_label.config(image="", text="[Sin imagen]", font=self.word_font) # Usar self.word_font
                return
            # --- CORREGIDO: Ruta absoluta para la imagen de la palabra ---
            image_path = os.path.join(self.current_dir, image_filename)
            original_img_pil = Image.open(image_path)
            
            # --- CORREGIDO: Usar self.image_width_single para el redimensionamiento escalado ---
            desired_width = self.image_width_single 
            aspect_ratio = original_img_pil.width / original_img_pil.height
            desired_height = int(desired_width / aspect_ratio)

            img_pil_resized = original_img_pil.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            self.single_word_image_tk = ImageTk.PhotoImage(img_pil_resized)
            self.single_main_image_label.config(image=self.single_word_image_tk)
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{image_filename}'.")
            self.single_main_image_label.config(image="", text="[Imagen no encontrada]", font=self.word_font) # Usar self.word_font
        except Exception as e:
            print(f"Error al cargar la imagen {image_filename}: {e}")
            self.single_main_image_label.config(image="", text="[Error de imagen]", font=self.word_font) # Usar self.word_font

    def load_image_for_group_slot(self, slot_index, image_filename):
        try:
            if not image_filename:
                self.image_labels[slot_index].config(image="", text="[Sin imagen]", font=self.count_font) # Usar self.count_font
                return
            # --- CORREGIDO: Ruta absoluta para la imagen de la palabra ---
            image_path = os.path.join(self.current_dir, image_filename)
            original_img_pil = Image.open(image_path)
            
            # --- CORREGIDO: Usar self.image_width_group para el redimensionamiento escalado ---
            desired_width = self.image_width_group 
            aspect_ratio = original_img_pil.width / original_img_pil.height
            desired_height = int(desired_width / aspect_ratio)

            img_pil_resized = original_img_pil.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            setattr(self, f"group_word_image_tk_{slot_index}", ImageTk.PhotoImage(img_pil_resized))
            self.image_labels[slot_index].config(image=getattr(self, f"group_word_image_tk_{slot_index}"))
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{image_filename}'.")
            self.image_labels[slot_index].config(image="", text="[Imagen no encontrada]", font=self.count_font) # Usar self.count_font
        except Exception as e:
            print(f"Error al cargar la imagen {image_filename}: {e}")
            self.image_labels[slot_index].config(image="", text="[Error de imagen]", font=self.count_font) # Usar self.count_font


    def next_step(self):
        if self.game_state == "individual_word":
            self.individual_word_counter += 1
            if self.individual_word_counter == 3:
                self.game_state = "group_summary"
            elif self.individual_word_counter > 3: # Si se avanza más allá de 3 (solo ocurre si recent_words_data se reinicia antes)
                self.recent_words_data = [] # Esto no debería pasar con la nueva lógica de _show_cycle_complete_screen
                self.individual_word_counter = 0
                self.game_state = "individual_word"
                if len(self.available_words) - self.current_word_index < 3:
                     self.shuffle_available_words()
        elif self.game_state == "group_summary":
            # Mostramos la pantalla de felicitación, pero NO avanzamos el juego todavía
            self._show_cycle_complete_screen()
            return  # 🔹 Detiene la ejecución aquí hasta que el usuario presione "Siguiente Ciclo"

        self.update_display()


    def prev_step(self):
        if self.game_state == "group_summary":
            # Si estamos en el resumen, volvemos a la última palabra individual del ciclo actual
            self.game_state = "individual_word"
            self.individual_word_counter = len(self.recent_words_data) - 1
            # Si recent_words_data está vacío (no debería pasar si estamos en resumen), ir al inicio
            if self.individual_word_counter < 0:
                self.individual_word_counter = 0

        elif self.game_state == "individual_word":
            if self.individual_word_counter > 0:
                self.individual_word_counter -= 1
                # Si estamos retrocediendo desde una palabra que se acaba de añadir, la quitamos
                # Esto es importante para que al volver a avanzar no se dupliquen palabras
                if len(self.recent_words_data) > self.individual_word_counter: # Lógica ajustada para pop
                    self.recent_words_data.pop()
                # También retrocedemos el índice de palabras disponibles para que get_next_individual_word funcione bien si volvemos a avanzar
                if self.current_word_index > 0:
                    self.current_word_index -= 1
            else:
                messagebox.showinfo("Juego", "Estás en el inicio del juego o del ciclo actual.")
                return # No hay paso anterior

        self.update_display()

    # --- Nueva función para la pantalla de felicitación del ciclo ---
    def _show_cycle_complete_screen(self):
        win_screen = tk.Toplevel(self.master)
        win_screen.title("¡Ciclo Completado!")
        # --- CORREGIDO: Dimensiones de la ventana de felicitación escaladas ---
        win_width = int(400 * self.scale)
        win_height = int(250 * self.scale)
        win_screen.geometry(f"{win_width}x{win_height}") 
        win_screen.resizable(False, False)
        win_screen.attributes("-topmost", True) 
        win_screen.grab_set() 

        win_screen.protocol("WM_DELETE_WINDOW", lambda: self._on_cycle_complete_screen_close(win_screen))

        frame = tk.Frame(win_screen, bg="white", padx=int(20 * self.scale), pady=int(20 * self.scale)) 
        frame.pack(expand=True, fill="both")

        message_label = tk.Label(frame, text="¡Excelente Trabajo!",
                                 font=self.title_font, # Usar self.title_font para un mensaje principal impactante
                                 bg="white", fg="#FF5757") 
        message_label.pack(pady=(int(10 * self.scale), int(5 * self.scale)))

        sub_message_label = tk.Label(frame, text="¡Completaste un ciclo de 3 palabras! 🎉",
                                      font=self.count_font, # Usar self.count_font
                                      bg="white", fg="#FF5757")
        sub_message_label.pack(pady=(0, int(20 * self.scale)))

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=int(10 * self.scale))

        next_button = tk.Button(button_frame, text="Siguiente Ciclo",
                                font=self.small_button_font,
                                bg="#FF6B6B", fg="white", 
                                activebackground="#E04D4D",
                                relief="flat", bd=0, padx=int(15 * self.scale), pady=int(8 * self.scale),
                                command=lambda: self._handle_cycle_complete_action("next_cycle", win_screen))
        next_button.pack(side="left", padx=int(10 * self.scale))

        menu_button = tk.Button(button_frame, text="Volver al Menú",
                                font=self.small_button_font,
                                bg="#5B84B1", fg="white", 
                                activebackground="#4A6E94",
                                relief="flat", bd=0, padx=int(15 * self.scale), pady=int(8 * self.scale),
                                command=lambda: self._handle_cycle_complete_action("menu", win_screen))
        menu_button.pack(side="left", padx=int(10 * self.scale))

        win_screen.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (win_screen.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (win_screen.winfo_height() // 2)
        win_screen.geometry(f"+{x}+{y}")

    def _handle_cycle_complete_action(self, action, win_screen):
        win_screen.destroy()
        self.master.grab_release()

        if action == "next_cycle":
            # 🔹 Recién ahora reiniciamos el ciclo
            self.recent_words_data = []
            self.individual_word_counter = 0
            self.game_state = "individual_word"
            if len(self.available_words) - self.current_word_index < 3:
                self.shuffle_available_words()
            self.update_display()

        elif action == "menu":
            self.go_to_menu()


    def _on_cycle_complete_screen_close(self, win_screen):
        win_screen.destroy()
        self.master.grab_release()


    def go_to_menu(self, event=None):
        """Cierra la ventana actual y ejecuta el script del menú principal de Simón Dice."""
        self.master.destroy()

        try:
            current_script_dir = os.path.dirname(__file__)
            # current_script_dir ahora es 'simon dice/nivel1' si este archivo está ahí
            # Para llegar a 'simon dice', necesitamos el directorio padre de 'nivel1'
            simon_dice_root_dir = os.path.dirname(current_script_dir) # Esto sería 'simon dice' si este script está en 'simon dice/nivel2'
            # Asumiendo que 'nivel2.py' (este archivo) está en 'simon dice/nivel2'
            # y 'menu_simondice.py' está en 'simon dice/menu'
            menu_simondice_path = os.path.join(simon_dice_root_dir, "menu", "menu_simondice.py")

            if not os.path.exists(menu_simondice_path):
                messagebox.showerror("Error de Ruta",
                                     f"El archivo no existe en la ruta calculada: {menu_simondice_path}")
                return

            subprocess.Popen(["python", menu_simondice_path])
        except FileNotFoundError:
            messagebox.showerror("Error al iniciar el menú",
                                 f"No se pudo encontrar el ejecutable 'python' o el archivo del menú:\n'{menu_simondice_path}'\n"
                                 "Asegúrate de que Python esté configurado en tu PATH o revisa la ruta del script del menú.")
        except Exception as e:
            messagebox.showerror("Error al iniciar el menú", f"Ocurrió un error inesperado al intentar abrir el menú: {e}")

    def _generate_and_play_audio_word(self, word, audio_path):
        if not os.path.exists(audio_path):
            try:
                text_to_synthesize = word.lower()
                tts = gTTS(text=text_to_synthesize, lang='es', slow=True)
                tts.save(audio_path)
            except Exception as e:
                print(f"Error al generar audio para '{word}': {e}")
                return

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al reproducir '{audio_path}': {e}")

    def play_word_audio(self, word):
        clean = word.lower().replace(" ", "_").replace("ñ", "n")
        path = os.path.join(self.audio_cache_dir, f"{clean}.mp3")
        threading.Thread(target=self._generate_and_play_audio_word, args=(word, path)).start()

    def repeat_current_word(self):
        """Repite la palabra actual si estamos en modo individual,
        o las 3 palabras del resumen si estamos en group_summary."""
        if self.game_state == "individual_word" and self.recent_words_data and self.individual_word_counter < len(self.recent_words_data):
            current_word = self.recent_words_data[self.individual_word_counter]["word"]
            self.play_word_audio(current_word)
        elif self.game_state == "group_summary" and self.recent_words_data:
            self.speak_summary_words()  # 🔊 habla las 3 palabras seguidas

    def speak_summary_words(self):
        """Reproduce las 3 palabras del resumen con una pausa corta entre cada una."""
        if not self.recent_words_data:
            return

        def speak_one_by_one(index=0):
            if index >= len(self.recent_words_data):
                return
            word = self.recent_words_data[index]["word"]
            self.play_word_audio(word)
            # esperar 1.5 s y continuar con la siguiente
            self.master.after(1000, speak_one_by_one, index + 1) # Asegurarse de que el delay sea adecuado

        speak_one_by_one()

# Para ejecutar el juego de palabras
if __name__ == "__main__":
    root = tk.Tk()
    game = PalabrasGame(root)
    root.mainloop()