import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess 
import socket
import threading
import time

class GameConfig:
    PIECE_SIZE = 150    # Tamaño de cada ficha (cuadrada)
    ROWS = 2            # Nivel 1: 2x2
    COLS = 2            # Nivel 1: 2x2

    IMAGE_FILENAMES = ["aceite.png", "asustar.png","batidora.png","batir.png","calabaza.png","cepillar los dientes.png","cumpleaños.png","dormir.png","dormitorio.png","estoy bien.png",]

    CURRENT_IMAGE_FILENAME = ""
    CURRENT_IMAGE_NAME = ""

    # Colores
    BG_COLOR_MAIN = "#c59fd7"
    BG_COLOR_CARD = "#ffffff"
    HEADER_TEXT_COLOR = "#2c3e50"
    SOUND_ICON_COLOR = "#8e44ad"
    BUTTON_BG_COLOR = "#c59fd7"
    BUTTON_ACTIVE_BG_COLOR = "#a07dc2"
    BUTTON_TEXT_COLOR = "white"
    BORDER_COLOR_PIECE = "#cccccc"
    BOARD_GRID_COLOR = "#eeeeee"
    BOARD_BORDER_COLOR = "#cccccc"

    # Espaciado para las piezas laterales
    SIDE_PIECE_PADDING_X = 15
    SIDE_PIECE_SPACING_Y = 15

    CARD_WIDTH = 900
    CARD_HEIGHT = 650



class PuzzleGame:
    def __init__(self, master):
        self.master = master
        master.title("Rompecabezas Nivel 1")

        # ✅ Pantalla completa y escala
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1000
        base_height = 750
        self.scale = min(screen_width / base_width, screen_height / base_height)

        master.attributes("-fullscreen", True)
        master.configure(bg=GameConfig.BG_COLOR_MAIN)

        # ✅ Aplicar escala a todos los tamaños
        self._apply_scaling()

        self.piece_images = []
        self.side_piece_labels = []

        self.occupied_slots = {}
        self.piece_current_slot = {}
        self.piece_initial_position = {}

        self.drag_data = {"toplevel": None, "piece_idx": None, "image_tk": None, "start_x_offset": 0, "start_y_offset": 0}

        self.card_canvas = None
        self.content_frame = None
        self.object_name_label = None
        self.level_title_label = None
        self.left_canvas = None # Solo un canvas izquierdo
        self.board_canvas = None
        self.right_canvas = None # Solo un canvas derecho
        self.next_image_button = None
        self.back_to_menu_button = None

        self._create_gui()
        self._start_new_round()
    
    def _apply_scaling(self):
        scale = self.scale

        # Escalar tamaños base
        GameConfig.PIECE_SIZE = int(150 * scale)
        GameConfig.CARD_WIDTH = int(900 * scale)
        GameConfig.CARD_HEIGHT = int(650 * scale)
        GameConfig.SIDE_PIECE_PADDING_X = int(15 * scale)
        GameConfig.SIDE_PIECE_SPACING_Y = int(15 * scale)

        # Escalar fuentes
        self.font_title = ("Segoe UI", int(24 * scale), "bold")
        self.font_name = ("Segoe UI", int(26 * scale), "bold")
        self.font_button = ("Segoe UI", int(16 * scale), "bold")

    def _start_new_round(self):
        if not GameConfig.IMAGE_FILENAMES:
            messagebox.showerror("Error", "No hay imágenes configuradas para el juego.", parent=self.master)
            return

        GameConfig.CURRENT_IMAGE_FILENAME = random.choice(GameConfig.IMAGE_FILENAMES)
        base_name = os.path.splitext(GameConfig.CURRENT_IMAGE_FILENAME)[0]
        GameConfig.CURRENT_IMAGE_NAME = " ".join([word.capitalize() for word in base_name.split()])

        print(f"Iniciando nueva ronda con la imagen: {GameConfig.CURRENT_IMAGE_FILENAME}")
        print(f"Nombre del objeto para el título: {GameConfig.CURRENT_IMAGE_NAME}")

        self.piece_images = []
        for lbl in self.side_piece_labels:
            lbl.destroy()
        self.side_piece_labels = []

        self._load_and_split_image()
        self._initialize_game()

        self.object_name_label.config(text=GameConfig.CURRENT_IMAGE_NAME)
        self.next_image_button.config(text="Siguiente Imagen")

    def _load_and_split_image(self):
        filename_to_load = GameConfig.CURRENT_IMAGE_FILENAME

        if not os.path.exists(filename_to_load):
            print(f"ADVERTENCIA: La imagen '{filename_to_load}' no se encontró. Creando una imagen de reemplazo.")
            img = Image.new("RGBA", (GameConfig.PIECE_SIZE * GameConfig.COLS, GameConfig.PIECE_SIZE * GameConfig.ROWS), (200, 200, 255, 255))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            text = f"IMAGEN NO ENCONTRADA\n({filename_to_load})"
            text_bbox = draw.textbbox((0,0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x_pos = (img.width - text_width) / 2
            y_pos = (img.height - text_height) / 2
            draw.text((x_pos, y_pos), text, fill="black", font=font, align="center")

        else:
            try:
                img = Image.open(filename_to_load).convert("RGBA")
                print(f"Imagen '{filename_to_load}' cargada correctamente.")
            except Exception as e:
                print(f"ERROR: No se pudo cargar la imagen '{filename_to_load}': {e}. Usando una imagen de reemplazo.")
                img = Image.new("RGBA", (GameConfig.PIECE_SIZE * GameConfig.COLS, GameConfig.PIECE_SIZE * GameConfig.ROWS), (255, 150, 150, 255))
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 14)
                except IOError:
                    font = ImageFont.load_default()
                text = f"ERROR AL CARGAR:\n{e}"
                text_bbox = draw.textbbox((0,0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x_pos = (img.width - text_width) / 2
                y_pos = (img.height - text_height) / 2
                draw.text((x_pos, y_pos), text, fill="black", font=font, align="center")

        min_dim = min(img.size)
        img = img.crop((0, 0, min_dim, min_dim))
        img = img.resize((GameConfig.PIECE_SIZE * GameConfig.COLS, GameConfig.PIECE_SIZE * GameConfig.ROWS), Image.LANCZOS)

        for r in range(GameConfig.ROWS):
            for c in range(GameConfig.COLS):
                piece = img.crop((c * GameConfig.PIECE_SIZE, r * GameConfig.PIECE_SIZE,
                                  (c + 1) * GameConfig.PIECE_SIZE, (r + 1) * GameConfig.PIECE_SIZE))
                self.piece_images.append(ImageTk.PhotoImage(piece))

        print(f"Total de {len(self.piece_images)} piezas de imagen creadas.")

    def _create_gui(self):
        total_pieces = GameConfig.ROWS * GameConfig.COLS 
        max_pieces_on_one_side = (total_pieces + 1) // 2 # 2 piezas para cada lado si se distribuyen

        side_canvas_width = GameConfig.PIECE_SIZE + 2 * GameConfig.SIDE_PIECE_PADDING_X
        side_canvas_height = (max_pieces_on_one_side * GameConfig.PIECE_SIZE) + \
                             ((max_pieces_on_one_side + 1) * GameConfig.SIDE_PIECE_SPACING_Y)

        print(f"Calculando side_canvas_width: {side_canvas_width}, side_canvas_height: {side_canvas_height}")

        board_width = GameConfig.PIECE_SIZE * GameConfig.COLS
        board_height = GameConfig.PIECE_SIZE * GameConfig.ROWS

        horizontal_padding_between_elements = 30
        # Ajustar el cálculo del ancho de la tarjeta para solo 2 paneles laterales
        card_required_width = (side_canvas_width * 2) + board_width + (horizontal_padding_between_elements * 4) + 40
        card_required_height = max(side_canvas_height, board_height) + 150

        card_width = GameConfig.CARD_WIDTH if GameConfig.CARD_WIDTH > card_required_width else card_required_width + 50
        card_height = GameConfig.CARD_HEIGHT if GameConfig.CARD_HEIGHT > card_required_height else card_required_height + 50

        self.card_canvas = tk.Canvas(self.master, bg=GameConfig.BG_COLOR_MAIN, highlightthickness=0)
        self.card_canvas.place(relx=0.5, rely=0.5, anchor="center", width=card_width, height=card_height)

        rounded_rect_padding = 10
        self._draw_rounded_rectangle(self.card_canvas,
                                     rounded_rect_padding, rounded_rect_padding,
                                     card_width - rounded_rect_padding, card_height - rounded_rect_padding,
                                     40,
                                     fill=GameConfig.BG_COLOR_CARD, outline="", width=0)

        self.content_frame = tk.Frame(self.card_canvas, bg=GameConfig.BG_COLOR_CARD)
        self.card_canvas.create_window(card_width / 2, card_height / 2, window=self.content_frame,
                                        width=card_width - (2 * rounded_rect_padding),
                                        height=card_height - (2 * rounded_rect_padding))

        self.level_title_label = tk.Label(self.content_frame, text="Rompecabezas Nivel 1", # Título del nivel 1
                                          font=self.font_title,
                                          bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        self.level_title_label.pack(pady=(25, 10))

        header_frame_object = tk.Frame(self.content_frame, bg=GameConfig.BG_COLOR_CARD)
        header_frame_object.pack(pady=(0, 15))

        sound_icon = tk.Label(header_frame_object, text="🔊", font=("Segoe UI Emoji", 26),
                              bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.SOUND_ICON_COLOR)
        sound_icon.pack(side="left", padx=7)

        self.object_name_label = tk.Label(header_frame_object, text="Objeto", font=self.font_name,
                                           bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        self.object_name_label.pack(side="left")

        game_area_frame = tk.Frame(self.content_frame, bg=GameConfig.BG_COLOR_CARD)
        game_area_frame.pack(pady=10, expand=True)

        self.left_canvas = tk.Canvas(game_area_frame,
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.left_canvas.grid(row=0, column=0, padx=horizontal_padding_between_elements, sticky="ns")

        self.board_canvas = tk.Canvas(game_area_frame,
                                       width=board_width,
                                       height=board_height,
                                       bg="white", highlightthickness=1, highlightbackground=GameConfig.BOARD_BORDER_COLOR)
        self.board_canvas.grid(row=0, column=1, padx=horizontal_padding_between_elements)

        self.right_canvas = tk.Canvas(game_area_frame,
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.right_canvas.grid(row=0, column=2, padx=horizontal_padding_between_elements, sticky="ns")

        for r in range(GameConfig.ROWS):
            for c in range(GameConfig.COLS):
                x0, y0 = c * GameConfig.PIECE_SIZE, r * GameConfig.PIECE_SIZE
                self.board_canvas.create_rectangle(x0, y0, x0 + GameConfig.PIECE_SIZE, y0 + GameConfig.PIECE_SIZE,
                                                   outline=GameConfig.BOARD_GRID_COLOR, width=1)

        buttons_frame = tk.Frame(self.content_frame, bg=GameConfig.BG_COLOR_CARD)
        buttons_frame.pack(pady=(20, 25))

        self.back_to_menu_button = tk.Button(buttons_frame, text="Volver al Menú",
                                             font=self.font_button,
                                             bg=GameConfig.BUTTON_BG_COLOR, fg=GameConfig.BUTTON_TEXT_COLOR,
                                             activebackground=GameConfig.BUTTON_ACTIVE_BG_COLOR,
                                             relief="flat", bd=0, padx=20, pady=10,
                                             command=self._back_to_menu)
        self.back_to_menu_button.pack(side="left", padx=10)

        self.next_image_button = tk.Button(buttons_frame, text="Siguiente Imagen",
                                      font=("Segoe UI", 16, "bold"),
                                      bg=GameConfig.BUTTON_BG_COLOR, fg=GameConfig.BUTTON_TEXT_COLOR,
                                      activebackground=GameConfig.BUTTON_ACTIVE_BG_COLOR,
                                      relief="flat", bd=0, padx=20, pady=10,
                                      command=self._start_new_round)
        self.next_image_button.pack(side="left", padx=10)
        print("GUI creada.")

    def _draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1 + radius, x2, y2 - radius,
                  x2 - radius, y2, x1 + radius, y2, x1, y1 + radius]
        canvas.create_polygon(points, smooth=True, **kwargs)

    def _initialize_game(self):
        print("Inicializando juego...")
        if self.board_canvas:
            self.board_canvas.delete("all")
            for r in range(GameConfig.ROWS):
                for c in range(GameConfig.COLS):
                    self.occupied_slots[(r, c)] = None
                    x0, y0 = c * GameConfig.PIECE_SIZE, r * GameConfig.PIECE_SIZE
                    self.board_canvas.create_rectangle(x0, y0, x0 + GameConfig.PIECE_SIZE, y0 + GameConfig.PIECE_SIZE,
                                                       outline=GameConfig.BOARD_GRID_COLOR, width=1)

            self.shuffled_indices = list(range(GameConfig.ROWS * GameConfig.COLS))
            random.shuffle(self.shuffled_indices)
            print(f"Índices mezclados para fichas laterales: {self.shuffled_indices}")

            self._create_side_pieces()
            print("Juego inicializado.")
        else:
            print("ERROR: board_canvas no se ha inicializado en _create_gui().")

    def _create_side_pieces(self):
        print("Creando fichas laterales...")
        for lbl in self.side_piece_labels:
            lbl.destroy()
        self.side_piece_labels = []

        self.piece_current_slot = {}
        self.piece_initial_position = {}

        total_pieces = GameConfig.ROWS * GameConfig.COLS 

        # Distribuimos las 4 piezas entre los dos canvases laterales (2 en cada uno)
        pieces_on_left_canvas = total_pieces // 2 # 2 piezas
        pieces_on_right_canvas = total_pieces - pieces_on_left_canvas # 2 piezas

        # Creamos una lista de tuplas (original_idx, canvas_destino)
        pieces_to_distribute = []
        for i, original_idx in enumerate(self.shuffled_indices):
            if i < pieces_on_left_canvas:
                pieces_to_distribute.append((original_idx, self.left_canvas))
            else:
                pieces_to_distribute.append((original_idx, self.right_canvas))

        # Ahora colocamos las piezas en sus respectivos canvases
        left_canvas_count = 0
        right_canvas_count = 0

        for original_idx, canvas_to_use in pieces_to_distribute:
            photo_image = self.piece_images[original_idx]

            lbl = tk.Label(canvas_to_use, image=photo_image, bd=1, relief="solid",
                           bg="white", highlightbackground=GameConfig.BORDER_COLOR_PIECE, highlightthickness=1)
            lbl.image = photo_image
            lbl.bind("<Button-1>", lambda e, idx=original_idx: self._start_drag(e, idx))

            x_pos = GameConfig.SIDE_PIECE_PADDING_X

            if canvas_to_use == self.left_canvas:
                y_pos = GameConfig.SIDE_PIECE_SPACING_Y + left_canvas_count * (GameConfig.PIECE_SIZE + GameConfig.SIDE_PIECE_SPACING_Y)
                left_canvas_count += 1
            else: # canvas_to_use == self.right_canvas
                y_pos = GameConfig.SIDE_PIECE_SPACING_Y + right_canvas_count * (GameConfig.PIECE_SIZE + GameConfig.SIDE_PIECE_SPACING_Y)
                right_canvas_count += 1

            lbl.place(x=x_pos, y=y_pos)
            self.side_piece_labels.append(lbl)
            self.piece_current_slot[original_idx] = None
            self.piece_initial_position[original_idx] = (x_pos, y_pos, canvas_to_use)
            print(f"Pieza {original_idx} colocada en {canvas_to_use} en ({x_pos},{y_pos})")

        print(f"Total de {len(self.side_piece_labels)} fichas laterales creadas y posicionadas.")


    def _start_drag(self, event, original_idx):
        if self.piece_current_slot[original_idx] is not None:
            return

        drag_toplevel = tk.Toplevel(self.master)
        drag_toplevel.overrideredirect(True)
        drag_toplevel.attributes("-topmost", True)

        self.drag_data["image_tk"] = self.piece_images[original_idx]
        drag_label = tk.Label(drag_toplevel, image=self.drag_data["image_tk"], bd=1, relief="solid", bg="white")
        drag_label.pack()

        self.drag_data["toplevel"] = drag_toplevel
        self.drag_data["piece_idx"] = original_idx

        self.drag_data["start_x_offset"] = event.x
        self.drag_data["start_y_offset"] = event.y

        x, y = self.master.winfo_pointerxy()
        drag_toplevel.geometry(f"+{x - self.drag_data['start_x_offset']}+{y - self.drag_data['start_y_offset']}")

        self.master.bind("<B1-Motion>", self._move_drag)
        self.master.bind("<ButtonRelease-1>", self._drop_drag)

    def _move_drag(self, event):
        if self.drag_data["toplevel"]:
            x, y = self.master.winfo_pointerxy()
            self.drag_data["toplevel"].geometry(f"+{x - self.drag_data['start_x_offset']}+{y - self.drag_data['start_y_offset']}")

    def _drop_drag(self, event):
        if self.drag_data["toplevel"]:
            self.drag_data["toplevel"].destroy()
            self.drag_data["toplevel"] = None
            self.drag_data["image_tk"] = None

        self.master.unbind("<B1-Motion>")
        self.master.unbind("<ButtonRelease-1>")

        drop_x_root = event.x_root
        drop_y_root = event.y_root

        if not self.board_canvas:
            print("ERROR: board_canvas no está disponible para el evento de soltar.")
            self._return_piece_to_side(self.drag_data["piece_idx"])
            return

        board_x_root = self.board_canvas.winfo_rootx()
        board_y_root = self.board_canvas.winfo_rooty()

        relative_x_on_board = drop_x_root - board_x_root
        relative_y_on_board = drop_y_root - board_y_root

        self._try_drop(relative_x_on_board, relative_y_on_board)

    def _return_piece_to_side(self, original_idx):
        if original_idx not in self.piece_initial_position:
            print(f"Advertencia: piece_initial_position no tiene datos para original_idx {original_idx}")
            return

        x, y, canvas_widget = self.piece_initial_position[original_idx]

        try:
            original_idx_in_shuffled = self.shuffled_indices.index(original_idx)
            if original_idx_in_shuffled < len(self.side_piece_labels):
                self.side_piece_labels[original_idx_in_shuffled].place(x=x, y=y)
            else:
                print(f"Advertencia: original_idx_in_shuffled {original_idx_in_shuffled} fuera de rango para side_piece_labels ({len(self.side_piece_labels)})")
        except ValueError:
            print(f"Advertencia: original_idx {original_idx} no encontrado en shuffled_indices.")

    def _try_drop(self, drop_x, drop_y):
        original_idx = self.drag_data["piece_idx"]

        if not (0 <= drop_x < self.board_canvas.winfo_width() and
                0 <= drop_y < self.board_canvas.winfo_height()):
            print(f"Soltado fuera del tablero. Volviendo pieza {original_idx}.")
            self._return_piece_to_side(original_idx)
            return

        col = int(drop_x // GameConfig.PIECE_SIZE)
        row = int(drop_y // GameConfig.PIECE_SIZE)

        target_slot = (row, col)
        correct_original_idx_for_slot = row * GameConfig.COLS + col

        if self.occupied_slots[target_slot] is None:
            if original_idx == correct_original_idx_for_slot:
                x = col * GameConfig.PIECE_SIZE
                y = row * GameConfig.PIECE_SIZE

                img_id = self.board_canvas.create_image(x, y, anchor="nw",
                                                      image=self.piece_images[original_idx], tags=str(original_idx))
                self.board_canvas.tag_bind(img_id, "<Double-Button-1>", lambda e, i=original_idx: self._release_piece_from_board(i))

                self.occupied_slots[target_slot] = img_id
                self.piece_current_slot[original_idx] = target_slot

                try:
                    original_idx_in_shuffled_list = self.shuffled_indices.index(original_idx)
                    self.side_piece_labels[original_idx_in_shuffled_list].place_forget()
                except ValueError:
                    print(f"Advertencia: original_idx {original_idx} no encontrado en shuffled_indices al intentar ocultar.")

                self._check_for_win()
            else:
                print(f"Pieza {original_idx} incorrecta para slot {target_slot}. Volviendo.")
                self._return_piece_to_side(original_idx)
        else:
            print(f"Slot {target_slot} ocupado. Volviendo pieza {original_idx}.")
            self._return_piece_to_side(original_idx)

    def _release_piece_from_board(self, original_idx):
        slot = self.piece_current_slot[original_idx]
        if slot is None:
            return

        img_id = self.occupied_slots[slot]
        if img_id:
            self.board_canvas.delete(img_id)

        self.occupied_slots[slot] = None
        self.piece_current_slot[original_idx] = None

        self._return_piece_to_side(original_idx)

    def _check_for_win(self):
        all_correct = True
        for r in range(GameConfig.ROWS):
            for c in range(GameConfig.COLS):
                slot = (r, c)
                img_id = self.occupied_slots[slot]
                expected_original_idx = r * GameConfig.COLS + c

                if img_id is None or int(self.board_canvas.gettags(img_id)[0]) != expected_original_idx:
                    all_correct = False
                    break
            if not all_correct:
                break

        if all_correct:
            self._show_win_screen()
            self.next_image_button.config(text="Siguiente Imagen")

    def _show_win_screen(self):
        win_screen = tk.Toplevel(self.master)
        win_screen.title("¡Ganaste!")
        win_screen.geometry("400x250") # Tamaño de la ventana de felicitación
        win_screen.resizable(False, False)
        win_screen.attributes("-topmost", True) 
        win_screen.grab_set() # Bloquea la interacción con la ventana principal

        # Manejar el cierre con la X para liberar el grab_set
        win_screen.protocol("WM_DELETE_WINDOW", lambda: self._on_win_screen_close(win_screen))

        frame = tk.Frame(win_screen, bg=GameConfig.BG_COLOR_CARD, padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        # Mensaje de felicitación
        message_label = tk.Label(frame, text="¡Felicidades!",
                                 font=self.font_title,
                                 bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        message_label.pack(pady=(10, 5))

        sub_message_label = tk.Label(frame, text="¡Completaste el rompecabezas! 🎉",
                                      font=("Segoe UI", 14),
                                      bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        sub_message_label.pack(pady=(0, 20))

        # Contenedor para los botones
        button_frame = tk.Frame(frame, bg=GameConfig.BG_COLOR_CARD)
        button_frame.pack(pady=10)

        # Botón "Siguiente Imagen"
        next_button = tk.Button(button_frame, text="Siguiente Imagen",
                                font=("Segoe UI", 12, "bold"),
                                bg=GameConfig.BUTTON_BG_COLOR, fg=GameConfig.BUTTON_TEXT_COLOR,
                                activebackground=GameConfig.BUTTON_ACTIVE_BG_COLOR,
                                relief="flat", bd=0, padx=15, pady=8,
                                command=lambda: self._handle_win_action("next", win_screen))
        next_button.pack(side="left", padx=10)

        # Botón "Volver al Menú"
        menu_button = tk.Button(button_frame, text="Volver al Menú",
                                font=("Segoe UI", 12, "bold"),
                                bg=GameConfig.BUTTON_BG_COLOR, fg=GameConfig.BUTTON_TEXT_COLOR,
                                activebackground=GameConfig.BUTTON_ACTIVE_BG_COLOR,
                                relief="flat", bd=0, padx=15, pady=8,
                                command=lambda: self._handle_win_action("menu", win_screen))
        menu_button.pack(side="left", padx=10)

        # Centrar la ventana de felicitación en la pantalla
        win_screen.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (win_screen.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (win_screen.winfo_height() // 2)
        win_screen.geometry(f"+{x}+{y}")

    def _handle_win_action(self, action, win_screen):
        win_screen.destroy() # Cierra la ventana de felicitación
        self.master.grab_release() 
        if action == "next":
            self._start_new_round() # Inicia una nueva ronda
        elif action == "menu":
            self._back_to_menu() # Vuelve al menú principal

    def _on_win_screen_close(self, win_screen):
        win_screen.destroy()
        self.master.grab_release()

    def _back_to_menu(self):
        self.master.destroy()

        try:
            current_level_dir = os.path.dirname(os.path.abspath(__file__))
            path_to_menu_script = os.path.join(current_level_dir, '..', 'menu', 'menu_rompecabezas.py')

            print(f"DEBUG: Desde nivel1.py, _back_to_menu")
            print(f"DEBUG: Directorio actual del script: {current_level_dir}")
            print(f"DEBUG: Ruta calculada para menu_rompecabezas.py: {path_to_menu_script}")
            print(f"DEBUG: ¿Existe menu_rompecabezas.py en esta ruta? {os.path.exists(path_to_menu_script)}")

            subprocess.Popen([sys.executable, path_to_menu_script])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el menú: {e}. Revisa la consola para más detalles.", parent=self.master)

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()