import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import subprocess
import platform 

# ========== CONFIGURACIÓN GLOBAL ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_system_font():
    if platform.system() == "Windows":
        return "Segoe UI"
    else:
        return "DejaVu Sans" 

SYSTEM_FONT = get_system_font()

# ---------- Configuración del Juego (NIVEL 2) ----------
class GameConfig:
    PIECE_SIZE = 120
    ROWS = 3  # Nivel 2 es 3x3
    COLS = 3

    # Imágenes del Nivel 2
    IMAGE_FILENAMES = [
        "amigos.png", "escalar.png", "horno de cocina.png", 
        "Año nuevo.png", "esperar en la parada.png", "estoy mal.png", 
        "freír un huevo.png", "hacer la cama.png", "picnic.png", "tener calor.png"
    ]

    CURRENT_IMAGE_FILENAME = ""
    CURRENT_IMAGE_NAME = ""

    # Paleta de Colores
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

    SIDE_PIECE_PADDING_X = 10 
    SIDE_PIECE_SPACING_Y = 5

    CARD_WIDTH = 900
    CARD_HEIGHT = 650

# ---------- Clase del Juego ----------
class PuzzleGame:
    def __init__(self, master):
        self.master = master
        master.title("Rompecabezas Nivel 2")
        
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        base_width = 1000
        base_height = 750
        self.scale = min(screen_width / base_width, screen_height / base_height)

        master.attributes("-fullscreen", True)
        master.configure(bg=GameConfig.BG_COLOR_MAIN)
        
        # Salida con Escape
        master.bind("<Escape>", lambda e: self._back_to_menu())

        # ✅ Aplicar escala
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
        self.left_canvas_1 = None
        self.left_canvas_2 = None
        self.board_canvas = None
        self.right_canvas_1 = None
        self.right_canvas_2 = None
        self.next_image_button = None
        self.back_to_menu_button = None

        self._create_gui()
        self._start_new_round()

    def _apply_scaling(self):
        scale = self.scale

        # Escalar tamaños
        GameConfig.PIECE_SIZE = int(120 * scale)
        GameConfig.CARD_WIDTH = int(900 * scale)
        GameConfig.CARD_HEIGHT = int(650 * scale)
        GameConfig.SIDE_PIECE_PADDING_X = int(10 * scale)
        GameConfig.SIDE_PIECE_SPACING_Y = int(5 * scale)

        # Escalar fuentes
        self.font_title = (SYSTEM_FONT, int(24 * scale), "bold")
        self.font_name = (SYSTEM_FONT, int(26 * scale), "bold")
        self.font_button = (SYSTEM_FONT, int(16 * scale), "bold")

    def _start_new_round(self):
        if not GameConfig.IMAGE_FILENAMES:
            messagebox.showerror("Error", "No hay imágenes configuradas.", parent=self.master)
            return

        GameConfig.CURRENT_IMAGE_FILENAME = random.choice(GameConfig.IMAGE_FILENAMES)
        base_name = os.path.splitext(GameConfig.CURRENT_IMAGE_FILENAME)[0]
        GameConfig.CURRENT_IMAGE_NAME = " ".join([word.capitalize() for word in base_name.split()])

        self.piece_images = []
        for lbl in self.side_piece_labels:
            lbl.destroy()
        self.side_piece_labels = []

        self._load_and_split_image()
        self._initialize_game()
        self.object_name_label.config(text=GameConfig.CURRENT_IMAGE_NAME)
        self.next_image_button.config(text="Siguiente Imagen")

    def _load_and_split_image(self):
        filename_to_load = os.path.join(SCRIPT_DIR, GameConfig.CURRENT_IMAGE_FILENAME)
        img = None
        
        if os.path.exists(filename_to_load):
            try:
                img = Image.open(filename_to_load).convert("RGBA")
            except Exception as e:
                print(f"Error cargando imagen: {e}")

        if img is None:
            img = Image.new("RGBA", (GameConfig.PIECE_SIZE * GameConfig.COLS, GameConfig.PIECE_SIZE * GameConfig.ROWS), (200, 200, 255, 255))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 14) if platform.system() == "Windows" else ImageFont.load_default()
            except:
                font = ImageFont.load_default() 
            text = f"ERROR:\n{GameConfig.CURRENT_IMAGE_FILENAME}"
            draw.text((10, 10), text, fill="black", font=font)

        min_dim = min(img.size)
        img = img.crop((0, 0, min_dim, min_dim))
        img = img.resize((GameConfig.PIECE_SIZE * GameConfig.COLS, GameConfig.PIECE_SIZE * GameConfig.ROWS), Image.LANCZOS)

        for r in range(GameConfig.ROWS):
            for c in range(GameConfig.COLS):
                piece = img.crop((c * GameConfig.PIECE_SIZE, r * GameConfig.PIECE_SIZE,
                                  (c + 1) * GameConfig.PIECE_SIZE, (r + 1) * GameConfig.PIECE_SIZE))
                self.piece_images.append(ImageTk.PhotoImage(piece))

    def _create_gui(self):
        total_pieces = GameConfig.ROWS * GameConfig.COLS 
        counts = [2, 2, 2, 3] 
        max_in_col = max(counts) 

        side_canvas_width = GameConfig.PIECE_SIZE + (2 * GameConfig.SIDE_PIECE_PADDING_X)
        side_canvas_height = max_in_col * (GameConfig.PIECE_SIZE + GameConfig.SIDE_PIECE_SPACING_Y) + GameConfig.SIDE_PIECE_SPACING_Y

        board_width  = GameConfig.PIECE_SIZE * GameConfig.COLS
        board_height = GameConfig.PIECE_SIZE * GameConfig.ROWS

        pad = 2 

        card_required_width = (4 * side_canvas_width) + board_width + (5 * pad)
        card_required_height = max(side_canvas_height, board_height) + 180

        card_width  = max(GameConfig.CARD_WIDTH,  card_required_width  + 40)
        card_height = max(GameConfig.CARD_HEIGHT, card_required_height + 40)

        self.card_canvas = tk.Canvas(self.master, bg=GameConfig.BG_COLOR_MAIN, highlightthickness=0)
        self.card_canvas.place(relx=0.5, rely=0.5, anchor="center", width=card_width, height=card_height)

        rounded_rect_padding = 10
        # DIBUJO CON ESQUINAS SIMÉTRICAS
        self._draw_rounded_rectangle(self.card_canvas,
                                     rounded_rect_padding, rounded_rect_padding,
                                     card_width - rounded_rect_padding, card_height - rounded_rect_padding,
                                     40,
                                     fill=GameConfig.BG_COLOR_CARD, outline="", width=0)

        self.content_frame = tk.Frame(self.card_canvas, bg=GameConfig.BG_COLOR_CARD)
        self.card_canvas.create_window(card_width / 2, card_height / 2, window=self.content_frame,
                                        width=card_width - (2 * rounded_rect_padding),
                                        height=card_height - (2 * rounded_rect_padding))

        self.level_title_label = tk.Label(self.content_frame, text="Rompecabezas Nivel 2",
                                          font=self.font_title,
                                          bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        self.level_title_label.pack(pady=(25, 10))

        header_frame_object = tk.Frame(self.content_frame, bg=GameConfig.BG_COLOR_CARD)
        header_frame_object.pack(pady=(0, 15))

        sound_icon = tk.Label(header_frame_object, text="🔊", font=("Segoe UI Emoji", 26) if platform.system() == "Windows" else (SYSTEM_FONT, 26),
                              bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.SOUND_ICON_COLOR)
        sound_icon.pack(side="left", padx=7)

        self.object_name_label = tk.Label(header_frame_object, text="Objeto", font=self.font_name,
                                           bg=GameConfig.BG_COLOR_CARD, fg=GameConfig.HEADER_TEXT_COLOR)
        self.object_name_label.pack(side="left")

        game_area_frame = tk.Frame(self.content_frame, bg=GameConfig.BG_COLOR_CARD)
        game_area_frame.pack(pady=10, expand=True)

        # Canvas laterales y tablero
        self.left_canvas_1 = tk.Canvas(game_area_frame, 
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.left_canvas_1.grid(row=0, column=0, padx=pad, sticky="n")

        self.left_canvas_2 = tk.Canvas(game_area_frame, 
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.left_canvas_2.grid(row=0, column=1, padx=pad, sticky="n")

        self.board_canvas = tk.Canvas(game_area_frame, 
                                       width=board_width,
                                       height=board_height,
                                       bg="white", highlightthickness=1, highlightbackground=GameConfig.BOARD_BORDER_COLOR)
        self.board_canvas.grid(row=0, column=2, padx=pad, sticky="n")

        self.right_canvas_1 = tk.Canvas(game_area_frame, 
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.right_canvas_1.grid(row=0, column=3, padx=pad, sticky="n")

        self.right_canvas_2 = tk.Canvas(game_area_frame, 
                                    width=side_canvas_width, height=side_canvas_height,
                                    bg=GameConfig.BG_COLOR_CARD, highlightthickness=0)
        self.right_canvas_2.grid(row=0, column=4, padx=pad, sticky="n")
        
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
                                      font=self.font_button,
                                      bg=GameConfig.BUTTON_BG_COLOR, fg=GameConfig.BUTTON_TEXT_COLOR,
                                      activebackground=GameConfig.BUTTON_ACTIVE_BG_COLOR,
                                      relief="flat", bd=0, padx=20, pady=10,
                                      command=self._start_new_round)
        self.next_image_button.pack(side="left", padx=10)

    # ========================================================
    # FUNCIÓN DE DIBUJO CORREGIDA (ESQUINAS SIMÉTRICAS)
    # ========================================================
    def _draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            (x1 + radius, y1), (x1 + radius, y1),
            (x2 - radius, y1), (x2 - radius, y1),
            (x2, y1),
            (x2, y1 + radius), (x2, y1 + radius),
            (x2, y2 - radius), (x2, y2 - radius),
            (x2, y2),
            (x2 - radius, y2), (x2 - radius, y2),
            (x1 + radius, y2), (x1 + radius, y2),
            (x1, y2),
            (x1, y2 - radius), (x1, y2 - radius),
            (x1, y1 + radius), (x1, y1 + radius),
            (x1, y1)
        ]
        canvas.create_polygon(points, smooth=True, **kwargs)

    def _initialize_game(self):
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
            self._create_side_pieces()

    def _create_side_pieces(self):
        for lbl in self.side_piece_labels:
            lbl.destroy()
        self.side_piece_labels = []

        self.piece_current_slot = {}
        self.piece_initial_position = {}

        cols = [self.left_canvas_1, self.left_canvas_2, self.right_canvas_1, self.right_canvas_2]
        counts = [2, 2, 2, 3] 
        idx = 0
        for col_idx, canvas in enumerate(cols):
            for pos_in_col in range(counts[col_idx]):
                if idx >= len(self.shuffled_indices): 
                    break
                original_idx = self.shuffled_indices[idx]
                idx += 1
                photo_image = self.piece_images[original_idx]

                lbl = tk.Label(canvas, image=photo_image, bd=1, relief="solid",
                               bg="white", highlightbackground=GameConfig.BORDER_COLOR_PIECE, highlightthickness=1)
                lbl.image = photo_image
                lbl.bind("<Button-1>", lambda e, oid=original_idx: self._start_drag(e, oid))

                x_pos = GameConfig.SIDE_PIECE_PADDING_X
                y_pos = GameConfig.SIDE_PIECE_SPACING_Y + pos_in_col * (GameConfig.PIECE_SIZE + GameConfig.SIDE_PIECE_SPACING_Y)

                lbl.place(x=x_pos, y=y_pos)
                self.side_piece_labels.append(lbl)
                self.piece_current_slot[original_idx] = None
                self.piece_initial_position[original_idx] = (x_pos, y_pos, canvas)

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
            self._return_piece_to_side(self.drag_data["piece_idx"])
            return

        board_x_root = self.board_canvas.winfo_rootx()
        board_y_root = self.board_canvas.winfo_rooty()

        relative_x_on_board = drop_x_root - board_x_root
        relative_y_on_board = drop_y_root - board_y_root

        self._try_drop(relative_x_on_board, relative_y_on_board)

    def _return_piece_to_side(self, original_idx):
        if original_idx not in self.piece_initial_position:
            return
        x, y, canvas_widget = self.piece_initial_position[original_idx]
        try:
            for lbl in self.side_piece_labels:
                if lbl.image == self.piece_images[original_idx]:
                    lbl.place(x=x, y=y)
                    break
        except Exception as e:
            print(f"Error al intentar devolver pieza {original_idx} al lado: {e}")

    def _try_drop(self, drop_x, drop_y):
        original_idx = self.drag_data["piece_idx"]

        if not (0 <= drop_x < self.board_canvas.winfo_width() and
                0 <= drop_y < self.board_canvas.winfo_height()):
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

                found_and_hidden = False
                for lbl in self.side_piece_labels:
                    if hasattr(lbl, 'image') and lbl.image == self.piece_images[original_idx]:
                        lbl.place_forget()
                        found_and_hidden = True
                        break
                
                self._check_for_win()
            else:
                self._return_piece_to_side(original_idx)
        else:
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
    
    # =============================================================
    # VENTANA DE FELICITACIÓN MEJORADA (ESQUINAS IGUALES)
    # =============================================================
    def _show_win_screen(self):
        # 1. Ventana sin bordes
        win = tk.Toplevel(self.master)
        win.overrideredirect(True) 
        win.attributes("-topmost", True)
        win.grab_set()
        
        # Dimensiones y escalado
        w, h = int(500 * self.scale), int(350 * self.scale)
        
        # Centrar
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        
        # Color del borde (El lila del juego)
        border_color = GameConfig.BG_COLOR_MAIN 
        win.configure(bg=border_color)

        # 2. Canvas para fondo redondeado
        canvas = tk.Canvas(win, width=w, height=h, bg=border_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Rectángulo blanco con esquinas redondeadas SIMÉTRICAS
        self._draw_rounded_rectangle(canvas, 10, 10, w-10, h-10, radius=20, fill="white", outline="white")
        
        # --- CONTENIDO ---
        
        # Título Grande
        title_font = (SYSTEM_FONT, int(40 * self.scale), "bold")
        tk.Label(win, text="¡Muy Bien!", font=title_font, bg="white", fg=GameConfig.SOUND_ICON_COLOR).place(relx=0.5, rely=0.25, anchor="center")
        
        # Subtítulo
        sub_font = (SYSTEM_FONT, int(16 * self.scale))
        tk.Label(win, text=f"¡Armaste: {GameConfig.CURRENT_IMAGE_NAME}!", font=sub_font, bg="white", fg=GameConfig.HEADER_TEXT_COLOR).place(relx=0.5, rely=0.5, anchor="center")
        
        # --- BOTONES ---
        btn_container = tk.Frame(win, bg="white")
        btn_container.place(relx=0.5, rely=0.75, anchor="center")
        
        def action(act):
            win.destroy()
            self.master.grab_release()
            if act == "next": self._start_new_round()
            elif act == "menu": self._back_to_menu()
            
        # Efectos Hover
        def on_enter_purple(e): e.widget['bg'] = GameConfig.BUTTON_ACTIVE_BG_COLOR
        def on_leave_purple(e): e.widget['bg'] = GameConfig.BUTTON_BG_COLOR
        
        def on_enter_blue(e): e.widget['bg'] = '#7FA6D6'
        def on_leave_blue(e): e.widget['bg'] = '#5B84B1'

        # Botón Menú
        btn_menu = tk.Button(btn_container, text="Menú 🏠", font=self.font_button,
                             bg="#5B84B1", fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("menu"))
        btn_menu.pack(side=tk.LEFT, padx=15)
        
        btn_menu.bind("<Enter>", on_enter_blue)
        btn_menu.bind("<Leave>", on_leave_blue)

        # Botón Siguiente
        btn_next = tk.Button(btn_container, text="Siguiente ➡", font=self.font_button,
                             bg=GameConfig.BUTTON_BG_COLOR, fg="white", 
                             relief="flat", cursor="hand2", padx=20, pady=10,
                             command=lambda: action("next"))
        btn_next.pack(side=tk.LEFT, padx=15)
        
        btn_next.bind("<Enter>", on_enter_purple)
        btn_next.bind("<Leave>", on_leave_purple)
    # =============================================================

    def _back_to_menu(self):
        self.master.destroy()
        try:
            path_to_menu_script = os.path.join(SCRIPT_DIR, '..', 'menu', 'menu_rompecabezas.py')
            path_to_menu_script = os.path.normpath(path_to_menu_script) 

            if not os.path.exists(path_to_menu_script):
                path_to_menu_script = os.path.join(SCRIPT_DIR, '..', 'menu_rompecabezas.py')
            
            if os.path.exists(path_to_menu_script):
                subprocess.Popen([sys.executable, path_to_menu_script])
            else:
                messagebox.showerror("Error", f"No se encuentra el menú en:\n{path_to_menu_script}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al volver: {e}", parent=self.master)

if __name__ == "__main__":
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()
