import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import subprocess
from gtts import gTTS
from playsound import playsound
import tempfile
import threading

class FrasesGame:
    def __init__(self, master):
        self.master = master
        master.title("Simón Dice: Las Frases")
        master.geometry("1000x700")
        master.configure(bg="#FF5757")

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

        self.game_state = "individual_word" # Este estado se mantiene, pero la lógica de felicitación es distinta

        self.canvas = tk.Canvas(master, bg="#FF5757", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)
        self.draw_rounded_rect(self.canvas, 0, 0, 900, 600, radius=20, fill="white", outline="white")
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.title_container = tk.Frame(self.inner_frame, bg="white")
        self.title_container.place(relx=0.5, rely=0.1, anchor="center")

        try:
            speaker_icon_path = "sonido.jpg"
            speaker_icon_pil = Image.open(speaker_icon_path).resize((40, 40), Image.Resampling.LANCZOS)
            self.speaker_title_photo = ImageTk.PhotoImage(speaker_icon_pil)
            self.speaker_title_label = tk.Label(self.title_container, image=self.speaker_title_photo, bg="white")
            self.speaker_title_label.pack(side=tk.LEFT, padx=5)
            self.title_label = tk.Label(self.title_container, text="SIMÓN DICE", font=("Arial", 36, "bold"), bg="white")
            self.title_label.pack(side=tk.LEFT)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}'. Usando emoticono en el título.")
            self.title_label = tk.Label(self.title_container, text="🔊SIMÓN DICE", font=("Arial", 36, "bold"), bg="white")
            self.title_label.pack(side=tk.LEFT)
        except Exception as e:
            print(f"Error al cargar el icono del título: {e}. Usando emoticono en el título.")
            self.title_label = tk.Label(self.title_container, text="🔊SIMÓN DICE", font=("Arial", 36, "bold"), bg="white")
            self.title_label.pack(side=tk.LEFT)

        self.single_word_display_frame = tk.Frame(self.inner_frame, bg="white")
        self.single_word_display_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.single_main_image_label = tk.Label(self.single_word_display_frame, bg="white")
        self.single_main_image_label.pack(pady=10)

        self.single_word_text_container = tk.Frame(self.single_word_display_frame, bg="white")
        self.single_word_text_container.pack(pady=5)

        try:
            speaker_icon_path = "sonido.jpg"
            speaker_icon_pil = Image.open(speaker_icon_path).resize((45, 45), Image.Resampling.LANCZOS)
            self.speaker_single_word_photo = ImageTk.PhotoImage(speaker_icon_pil)
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, image=self.speaker_single_word_photo, bg="white")
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=5)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen '{speaker_icon_path}' para la palabra individual. Usando emoticono.")
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, text="🔊", bg="white", font=("Arial", 40, "bold"))
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error al cargar el icono de palabra individual: {e}. Usando emoticono.")
            self.speaker_single_word_label = tk.Label(self.single_word_text_container, text="🔊", bg="white", font=("Arial", 40, "bold"))
            self.speaker_single_word_label.pack(side=tk.LEFT, padx=5)

        self.single_word_label = tk.Label(self.single_word_text_container, text="", font=("Arial", 16, "bold"), bg="white")
        self.single_word_label.pack(side=tk.LEFT)

        self.bottom_buttons_container = tk.Frame(self.inner_frame, bg="white")
        self.bottom_buttons_container.place(relx=0.5, rely=0.85, anchor="center")

        # Botón "Nivel 3" - Siempre visible y con texto más pequeño
        self.level_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=150, height=50)
        self.draw_rounded_rect(self.level_button_canvas, 0, 0, 150, 50, radius=15, fill="#FF6B6B", outline="#FF6B6B")
        self.level_button_text = self.level_button_canvas.create_text(75, 25, text="Nivel 3", font=("Arial", 12, "bold"), fill="white") # Texto a Nivel 3
        self.level_button_canvas.bind("<Button-1>", lambda e: self.next_phrase())
        self.level_button_canvas.pack(side=tk.LEFT, padx=10)

        # Botón "Volver al Menú"
        self.menu_button_canvas = tk.Canvas(self.bottom_buttons_container, bg="white", highlightthickness=0, width=200, height=50)
        self.draw_rounded_rect(self.menu_button_canvas, 0, 0, 200, 50, radius=15, fill="#5B84B1", outline="#5B84B1")
        self.menu_button_text = self.menu_button_canvas.create_text(100, 25, text="Volver al Menú", font=("Arial", 16, "bold"), fill="white")
        self.menu_button_canvas.bind("<Button-1>", self.go_to_menu)
        self.menu_button_canvas.pack(side=tk.LEFT, padx=10)

        # Botón "Siguiente" (flecha derecha)
        self.next_button = tk.Button(self.inner_frame, text=">", font=("Arial", 30, "bold"),
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.next_word_in_phrase)
        self.next_button.place(relx=0.85, rely=0.5, anchor="center")

        # Botón "Anterior" (flecha izquierda)
        self.prev_button = tk.Button(self.inner_frame, text="<", font=("Arial", 30, "bold"),
                                     bg="white", fg="#FF6B6B", relief="flat", command=self.prev_word_in_phrase)
        self.prev_button.place(relx=0.15, rely=0.5, anchor="center")

        self.word_count_label = tk.Label(self.inner_frame, text="", font=("Arial", 10), bg="white")
        self.word_count_label.place(relx=0.9, rely=0.9, anchor="e")

        # ---------- Botón REPETIR (arriba a la derecha, circular) ----------
        self.repeat_circle = tk.Canvas(self.inner_frame, bg="white", highlightthickness=0, width=50, height=50)
        self.draw_rounded_rect(self.repeat_circle, 0, 0, 50, 50, radius=25,
                            fill="#FFB347", outline="#FFB347")
        self.repeat_circle.create_text(25, 25, text="🔊", font=("Arial", 18), fill="white")
        self.repeat_circle.place(relx=0.95, rely=0.05, anchor="ne")
        self.repeat_circle.bind("<Button-1>", lambda e: self.repeat_current_word())

        # Icono de oreja "escuchar.png" - Ahora más grande
        try:
            ear_icon_path = "escuchar.png"
            original_ear_img_pil = Image.open(ear_icon_path)
            desired_ear_height = 120  # Aumentado el tamaño
            aspect_ratio_ear = original_ear_img_pil.width / original_ear_img_pil.height
            desired_ear_width = int(desired_ear_height * aspect_ratio_ear)

            self.ear_img_pil = original_ear_img_pil.resize((desired_ear_width, desired_ear_height), Image.Resampling.LANCZOS)
            self.ear_photo = ImageTk.PhotoImage(self.ear_img_pil)
            self.ear_label = tk.Label(self.inner_frame, image=self.ear_photo, bg="white")
            self.ear_label.place(relx=0.08, rely=0.85, anchor="w")
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{ear_icon_path}'. Asegúrate de que esté en la misma carpeta.")
            self.ear_label = tk.Label(self.inner_frame, text="[Escuchar]", font=("Arial", 14), bg="white")
            self.ear_label.place(relx=0.08, rely=0.92, anchor="w")

        self.update_display()

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

    def shuffle_available_phrases(self):
        self.available_phrases = self.all_phrases_data[:]
        random.shuffle(self.available_phrases)
        self.current_phrase_index = 0
        self.current_word_in_phrase_index = 0

    def get_current_phrase_data(self):
        if not self.available_phrases:
            return None
        return self.available_phrases[self.current_phrase_index]

    def update_display(self):
        self.display_current_word_of_phrase()

    def display_current_word_of_phrase(self):
        phrase_data = self.get_current_phrase_data()
        if not phrase_data or not phrase_data["words"]:
            self.single_word_label.config(text="No hay frases disponibles.")
            self.load_image_for_single_slot(None)
            self.word_count_label.config(text="Juego Terminado")
            return

        words_in_current_phrase = phrase_data["words"]
        total_words_in_phrase = len(words_in_current_phrase)

        if self.current_word_in_phrase_index >= total_words_in_phrase:
            self.current_word_in_phrase_index = total_words_in_phrase - 1
        if self.current_word_in_phrase_index < 0:
            self.current_word_in_phrase_index = 0

        word_data = words_in_current_phrase[self.current_word_in_phrase_index]

        # --- Mostrar palabra e imagen ---
        self.single_word_label.config(text=word_data["word"])
        self.load_image_for_single_slot(word_data["image"])
        self.word_count_label.config(
            text=f"Palabra {self.current_word_in_phrase_index + 1} de {total_words_in_phrase}"
        )

        # --- Voz automática de la palabra actual ---
        try:
            current_word_text = word_data["word"]
            tts = gTTS(text=current_word_text, lang="es", slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
                tts.save(temp_path)
            threading.Thread(target=lambda: (playsound(temp_path), os.remove(temp_path))).start()

        except Exception as e:
            print(f"Error al reproducir la voz: {e}")

    def repeat_current_word(self):
        """Vuelve a decir la palabra que está en pantalla."""
        try:
            phrase_data = self.get_current_phrase_data()
            if not phrase_data or not phrase_data["words"]:
                return

            word_data = phrase_data["words"][self.current_word_in_phrase_index]
            current_word_text = word_data["word"]

            threading.Thread(target=self._speak_word, args=(current_word_text,)).start()
        except Exception as e:
            print(f"Error al repetir palabra: {e}")

    def _speak_word(self, text):
        """Genera y reproduce el audio de la palabra."""
        try:
            tts = gTTS(text=text, lang="es", slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
                tts.save(temp_path)
            playsound(temp_path)
            os.remove(temp_path)
        except Exception as e:
            print(f"Error al reproducir voz: {e}")

    def load_image_for_single_slot(self, image_filename):
        try:
            if not image_filename:
                self.single_main_image_label.config(image="", text="[Sin pictograma]", font=("Arial", 18))
                return
            image_path = image_filename
            original_img_pil = Image.open(image_path)
            desired_width = 250
            aspect_ratio = original_img_pil.width / original_img_pil.height
            desired_height = int(desired_width / aspect_ratio)

            img_pil_resized = original_img_pil.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            self.single_word_image_tk = ImageTk.PhotoImage(img_pil_resized)
            self.single_main_image_label.config(image=self.single_word_image_tk, text="")
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen '{image_filename}'.")
            self.single_main_image_label.config(image="", text="[Pictograma no encontrado]", font=("Arial", 18))
        except Exception as e:
            print(f"Error al cargar la imagen {image_filename}: {e}")
            self.single_main_image_label.config(image="", text="[Error al cargar pictograma]", font=("Arial", 18))

    def next_word_in_phrase(self):
        phrase_data = self.get_current_phrase_data()
        if not phrase_data:
            return

        total_words_in_phrase = len(phrase_data["words"])
        if self.current_word_in_phrase_index < total_words_in_phrase - 1:
            self.current_word_in_phrase_index += 1
            self.update_display()
        else:
            # Si es la última palabra de la frase, mostramos la pantalla de felicitación
            self._show_phrase_complete_screen()

    def prev_word_in_phrase(self):
        if self.current_word_in_phrase_index > 0:
            self.current_word_in_phrase_index -= 1
            self.update_display()
        else:
            messagebox.showinfo("Inicio de Frase", "Ya estás en la primera palabra de esta frase.")

    def next_phrase(self):
        if self.current_phrase_index < len(self.available_phrases) - 1:
            self.current_phrase_index += 1
            self.current_word_in_phrase_index = 0
            self.update_display()
        else:
            # Si ya no hay más frases disponibles, barajamos y reiniciamos
            self.shuffle_available_phrases()
            self.current_phrase_index = 0
            self.current_word_in_phrase_index = 0
            self.update_display()
            messagebox.showinfo("Juego Completado", "¡Has completado todas las frases! Reiniciando el juego.")


    # --- Nueva función para la pantalla de felicitación de la frase ---
    def _show_phrase_complete_screen(self):
        win_screen = tk.Toplevel(self.master)
        win_screen.title("¡Frase Completada!")
        win_screen.geometry("400x250")
        win_screen.resizable(False, False)
        win_screen.attributes("-topmost", True)
        win_screen.grab_set()

        win_screen.protocol("WM_DELETE_WINDOW", lambda: self._on_phrase_complete_screen_close(win_screen))

        frame = tk.Frame(win_screen, bg="white", padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        message_label = tk.Label(frame, text="¡Excelente Trabajo!",
                                 font=("Arial", 24, "bold"),
                                 bg="white", fg="#FF5757")
        message_label.pack(pady=(10, 5))

        # Mostramos la frase completa que acaba de ser completada
        current_phrase_text = self.get_current_phrase_data()["phrase_text"]
        sub_message_label = tk.Label(frame, text=f"¡Has completado la frase: \"{current_phrase_text}\"! 🎉",
                                      font=("Arial", 14),
                                      bg="white", fg="#FF5757", wraplength=350, justify="center")
        sub_message_label.pack(pady=(0, 20))

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=10)

        next_button = tk.Button(button_frame, text="Siguiente Frase",
                                font=("Arial", 12, "bold"),
                                bg="#FF6B6B", fg="white",
                                activebackground="#E04D4D",
                                relief="flat", bd=0, padx=15, pady=8,
                                command=lambda: self._handle_phrase_complete_action("next_phrase", win_screen))
        next_button.pack(side="left", padx=10)

        menu_button = tk.Button(button_frame, text="Volver al Menú",
                                font=("Arial", 12, "bold"),
                                bg="#5B84B1", fg="white",
                                activebackground="#4A6E94",
                                relief="flat", bd=0, padx=15, pady=8,
                                command=lambda: self._handle_phrase_complete_action("menu", win_screen))
        menu_button.pack(side="left", padx=10)

        win_screen.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (win_screen.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (win_screen.winfo_height() // 2)
        win_screen.geometry(f"+{x}+{y}")

    def _handle_phrase_complete_action(self, action, win_screen):
        win_screen.destroy()
        self.master.grab_release()

        if action == "next_phrase":
            # Reinicia la frase de forma controlada (solo al presionar el botón)
            if self.current_phrase_index < len(self.available_phrases) - 1:
                self.current_phrase_index += 1
            else:
                self.shuffle_available_phrases()
                self.current_phrase_index = 0
            self.current_word_in_phrase_index = 0
            self.update_display()

        elif action == "menu":
            self.go_to_menu()


    def _on_phrase_complete_screen_close(self, win_screen):
        win_screen.destroy()
        self.master.grab_release()


    def go_to_menu(self, event=None):
        self.master.destroy()

        try:
            current_script_dir = os.path.dirname(__file__)
            simon_dice_dir = os.path.dirname(current_script_dir)
            menu_simondice_path = os.path.join(simon_dice_dir, "menu", "menu_simondice.py")

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


if __name__ == "__main__":
    root = tk.Tk()
    game = FrasesGame(root)
    root.mainloop()