import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import threading
import pygame.mixer
from gtts import gTTS

# --- CONFIGURACIÓN ---
class Config:
    BG_COLOR = "#FFFDE7"       
    HEADER_BG = "#FBC02D"      
    SENTENCE_BAR_BG = "#FFFFFF" 
    
    FOLDER_COLOR = "#FFEE58"   
    FOLDER_BORDER = "#F9A825"  
    
    ITEM_COLOR = "#FFFFFF"     
    ITEM_BORDER = "#BCAAA4"    
    
    TEXT_COLOR = "#5D4037"     
    BTN_BACK_BG = "#FFF59D"
    
    ICON_SIZE = 140            
    MINI_ICON_SIZE = 80        
    GRID_COLS = 5              
    
    CARPETA_IMG = "." 
    CARPETA_AUDIO = "audio_cache" 

class TEAyudoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEAyudo - Comunicador Completo")
        self.root.state("zoomed") 
        self.root.configure(bg=Config.BG_COLOR)

        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Error audio: {e}")

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir = os.path.join(self.current_dir, Config.CARPETA_AUDIO)
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

        self.frase_actual = [] 

        # --- BASE DE DATOS COMPLETA ---
        self.DATA = {
            "root": [
                # --- FILA 1: COMUNICACIÓN BÁSICA (NUEVO) ---
                {"tipo": "folder", "label": "Social",    "id": "social",    "color": "#FFCCBC", "emoji": "👋"},
                {"tipo": "folder", "label": "Preguntas", "id": "preguntas", "color": "#B2EBF2", "emoji": "❓"},
                {"tipo": "folder", "label": "Emociones", "id": "emociones", "color": "#F48FB1", "emoji": "🙂"},
                {"tipo": "folder", "label": "Acciones",  "id": "acciones",  "color": "#AED581", "emoji": "🏃"},
                {"tipo": "item",   "label": "Yo",        "text": "Yo quiero", "color": "#E1BEE7", "emoji": "🙋"},

                # --- FILA 2: NECESIDADES ---
                {"tipo": "folder", "label": "Comida",    "id": "comida",    "color": Config.FOLDER_COLOR, "emoji": "🍽️"},
                {"tipo": "folder", "label": "Bebida",    "id": "bebida",    "color": "#81D4FA", "emoji": "🥤"},
                {"tipo": "folder", "label": "Higiene",   "id": "higiene",   "color": "#80DEEA", "emoji": "🧼"},
                {"tipo": "folder", "label": "Ropa",      "id": "ropa",      "color": "#CE93D8", "emoji": "👕"},
                {"tipo": "folder", "label": "Salud",     "id": "salud",     "color": "#EF9A9A", "emoji": "🏥"},
                
                # --- FILA 3: ENTORNO ---
                {"tipo": "folder", "label": "Lugares",   "id": "lugares",   "color": "#BCAAA4", "emoji": "🏠"},
                {"tipo": "folder", "label": "Escuela",   "id": "escuela",   "color": "#FFF59D", "emoji": "🏫"},
                {"tipo": "folder", "label": "Cocina",    "id": "cocina",    "color": "#B0BEC5", "emoji": "🍴"}, # Nuevo
                {"tipo": "folder", "label": "Tecnología","id": "tecnologia","color": "#90CAF9", "emoji": "📱"}, # Nuevo
                {"tipo": "folder", "label": "Transporte","id": "transporte","color": "#CFD8DC", "emoji": "🚗"},

                # --- FILA 4: PERSONAS Y SERES ---
                {"tipo": "folder", "label": "Personas",  "id": "personas",  "color": "#FFAB91", "emoji": "👥"},
                {"tipo": "folder", "label": "Cuerpo",    "id": "cuerpo",    "color": "#FFCCBC", "emoji": "👃"},
                {"tipo": "folder", "label": "Animales",  "id": "animales",  "color": "#D7CCC8", "emoji": "🐾"},
                {"tipo": "folder", "label": "Tiempo",    "id": "tiempo",    "color": "#9FA8DA", "emoji": "⏰"},
                {"tipo": "folder", "label": "Juguetes",  "id": "juguetes",  "color": "#F48FB1", "emoji": "🧸"},

                # --- FILA 5: CONCEPTOS ---
                {"tipo": "folder", "label": "Deportes",  "id": "deportes",  "color": "#C5E1A5", "emoji": "⚽"}, # Nuevo
                {"tipo": "folder", "label": "Colores",   "id": "colores",   "color": "#FFFFFF", "emoji": "🎨"},
                {"tipo": "folder", "label": "Describir", "id": "descriptivos", "color": "#E0E0E0", "emoji": "📏"},
                {"tipo": "folder", "label": "Formas",    "id": "formas",    "color": "#EEEEEE", "emoji": "🔺"},
                
                # --- FILA 6: RESPUESTAS RÁPIDAS ---
                {"tipo": "item", "label": "Sí", "text": "Sí", "color": "#C8E6C9", "emoji": "👍"},
                {"tipo": "item", "label": "No", "text": "No", "color": "#FFCDD2", "emoji": "👎"},
                {"tipo": "item", "label": "Ayuda", "text": "Ayuda por favor", "color": "#FFF176", "emoji": "🆘"},
                {"tipo": "item", "label": "Baño", "text": "Quiero ir al baño", "img": "baño.png", "ruta": "acciones"},
            ],

            # --- CATEGORÍAS NUEVAS (INSPIRADAS EN CBOARD) ---
            "social": [
                {"tipo": "item", "label": "Hola", "img": "hola.png", "ruta": "social"},
                {"tipo": "item", "label": "Adiós", "img": "adios.png", "ruta": "social"},
                {"tipo": "item", "label": "Buenos días", "img": "buenos dias.png", "ruta": "social"},
                {"tipo": "item", "label": "Buenas noches", "img": "buenas noches.png", "ruta": "social"},
                {"tipo": "item", "label": "Por favor", "img": "por favor.png", "ruta": "social"},
                {"tipo": "item", "label": "Gracias", "img": "gracias.png", "ruta": "social"},
                {"tipo": "item", "label": "De nada", "img": "de nada.png", "ruta": "social"},
                {"tipo": "item", "label": "Perdón", "img": "perdon.png", "ruta": "social"},
                {"tipo": "item", "label": "Te quiero", "img": "te quiero.png", "ruta": "social"},
                {"tipo": "item", "label": "Bien", "img": "bien.png", "ruta": "social"},
                {"tipo": "item", "label": "Mal", "img": "mal.png", "ruta": "social"},
            ],
            "preguntas": [
                {"tipo": "item", "label": "Qué", "img": "que.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Quién", "img": "quien.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Dónde", "img": "donde.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Cuándo", "img": "cuando.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Por qué", "img": "por que.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Cómo", "img": "como.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Cuánto", "img": "cuanto.png", "ruta": "preguntas"},
                {"tipo": "item", "label": "Cuál", "img": "cual.png", "ruta": "preguntas"},
            ],
            "tecnologia": [
                {"tipo": "item", "label": "Teléfono", "img": "telefono.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Tablet", "img": "tablet.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Computadora", "img": "ordenador.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "TV", "img": "television.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Cámara", "img": "camara.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Música", "img": "musica.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Videojuego", "img": "videojuego.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Internet", "img": "internet.png", "ruta": "tecnologia"},
                {"tipo": "item", "label": "Wifi", "img": "wifi.png", "ruta": "tecnologia"},
            ],
            "cocina": [
                {"tipo": "item", "label": "Plato", "img": "plato.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Vaso", "img": "vaso.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Cuchara", "img": "cuchara.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Tenedor", "img": "tenedor.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Cuchillo", "img": "cuchillo.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Servilleta", "img": "servilleta.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Olla", "img": "olla.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Sartén", "img": "sarten.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Botella", "img": "botella.png", "ruta": "cocina_utensilios"},
                {"tipo": "item", "label": "Taza", "img": "taza.png", "ruta": "cocina_utensilios"},
            ],
            "deportes": [
                {"tipo": "item", "label": "Fútbol", "img": "futbol.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Baloncesto", "img": "baloncesto.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Natación", "img": "natacion.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Tenis", "img": "tenis.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Correr", "img": "correr.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Bici", "img": "bicicleta.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Pelota", "img": "pelota.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Ganar", "img": "ganar.png", "ruta": "deportes"},
                {"tipo": "item", "label": "Perder", "img": "perder.png", "ruta": "deportes"},
            ],

            # --- TUS CATEGORÍAS ORIGINALES (MANTENIDAS) ---
            "comida": [
                {"tipo": "folder", "label": "Frutas", "id": "frutas", "color": "#FFE0B2"},
                {"tipo": "folder", "label": "Verduras", "id": "verduras", "color": "#C5E1A5"},
                {"tipo": "item", "label": "Pan", "img": "pan.png", "ruta": "comida"},
                {"tipo": "item", "label": "Galleta", "img": "galleta.png", "ruta": "comida"},
                {"tipo": "item", "label": "Sopa", "img": "sopa.png", "ruta": "comida"},
                {"tipo": "item", "label": "Carne", "img": "carne.png", "ruta": "comida"},
                {"tipo": "item", "label": "Huevo", "img": "huevo.png", "ruta": "comida"},
                {"tipo": "item", "label": "Queso", "img": "queso.png", "ruta": "comida"},
                {"tipo": "item", "label": "Arroz", "img": "arroz.png", "ruta": "comida"},
                {"tipo": "item", "label": "Fideos", "img": "fideos.png", "ruta": "comida"},
            ],
            "frutas": [
                {"tipo": "item", "label": "Manzana", "img": "manzana.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Banana", "img": "banana.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Naranja", "img": "naranja.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Uva", "img": "uva.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Pera", "img": "pera.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Sandía", "img": "sandia.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Piña", "img": "piña.png", "ruta": "comida/frutas"},
                {"tipo": "item", "label": "Fresa", "img": "fresa.png", "ruta": "comida/frutas"},
            ],
            "verduras": [
                {"tipo": "item", "label": "Papa", "img": "papa.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Zanahoria", "img": "zanahoria.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Tomate", "img": "tomate.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Lechuga", "img": "lechuga.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Brócoli", "img": "brocoli.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Maíz", "img": "maiz.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Cebolla", "img": "cebolla.png", "ruta": "comida/verduras"},
                {"tipo": "item", "label": "Pepino", "img": "pepino.png", "ruta": "comida/verduras"},
            ],
            "bebida": [
                {"tipo": "item", "label": "Agua", "img": "agua.png", "ruta": "bebida"},
                {"tipo": "item", "label": "Jugo", "img": "jugo.png", "ruta": "bebida"},
                {"tipo": "item", "label": "Leche", "img": "leche.png", "ruta": "bebida"},
                {"tipo": "item", "label": "Chocolate", "img": "chocolate.jpg", "ruta": "bebida"},
                {"tipo": "item", "label": "Gaseosa", "img": "gaseosa.png", "ruta": "bebida"},
                {"tipo": "item", "label": "Té", "img": "te.png", "ruta": "bebida"},
            ],
            "emociones": [
                {"tipo": "item", "label": "Feliz", "img": "feliz.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Triste", "img": "triste.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Enojado", "img": "enojado.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Cansado", "img": "cansado.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Miedo", "img": "miedo.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Dolor", "img": "dolor.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Sorpresa", "img": "sorprendido.png", "ruta": "emociones"},
                {"tipo": "item", "label": "Enfermo", "img": "enfermo.png", "ruta": "emociones"},
            ],
            "acciones": [
                {"tipo": "item", "label": "Baño", "img": "baño.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Dormir", "img": "dormir.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Jugar", "img": "jugar.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Comer", "img": "comer.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Beber", "img": "beber.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Dibujar", "img": "dibujar.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Correr", "img": "correr.png", "ruta": "acciones"},
                {"tipo": "item", "label": "Mirar", "img": "mirar.png", "ruta": "acciones"},
            ],
            "ropa": [
                {"tipo": "item", "label": "Camisa", "img": "camisa.png", "ruta": "ropa"},
                {"tipo": "item", "label": "Pantalón", "img": "pantalon.png", "ruta": "ropa"},
                {"tipo": "item", "label": "Zapatos", "img": "zapato.png", "ruta": "ropa"},
                {"tipo": "item", "label": "Medias", "img": "medias.png", "ruta": "ropa"},
                {"tipo": "item", "label": "Campera", "img": "campera.png", "ruta": "ropa"},
                {"tipo": "item", "label": "Gorro", "img": "gorro.png", "ruta": "ropa"},
            ],
            "higiene": [
                {"tipo": "item", "label": "Jabón", "img": "jabon.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Toalla", "img": "toalla.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Cepillo", "img": "cepillo de dientes.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Pasta", "img": "pasta de dientes.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Peine", "img": "peine.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Papel", "img": "papel higiénico.png", "ruta": "higiene"},
                {"tipo": "item", "label": "Ducha", "img": "ducha.png", "ruta": "higiene"},
            ],
            "lugares": [
                {"tipo": "item", "label": "Casa", "img": "casa.png", "ruta": "lugares"},
                {"tipo": "item", "label": "Escuela", "img": "escuela.png", "ruta": "lugares"},
                {"tipo": "item", "label": "Plaza", "img": "plaza.png", "ruta": "lugares"},
                {"tipo": "item", "label": "Hospital", "img": "hospital.png", "ruta": "lugares"},
                {"tipo": "item", "label": "Súper", "img": "supermercado.png", "ruta": "lugares"},
            ],
            "escuela": [
                {"tipo": "folder", "label": "Materias", "id": "materias", "color": "#FFF59D"},
                {"tipo": "item", "label": "Lápiz", "img": "lapiz.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Papel", "img": "papel.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Libro", "img": "libro.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Cuaderno", "img": "cuaderno.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Mochila", "img": "mochila.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Mesa", "img": "mesa.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Silla", "img": "silla.png", "ruta": "escuela"},
                {"tipo": "item", "label": "Ordenador", "img": "ordenador.png", "ruta": "escuela"},
            ],
            "materias": [
                {"tipo": "item", "label": "Matemáticas", "img": "matematicas.png", "ruta": "escuela/materias"},
                {"tipo": "item", "label": "Lengua", "img": "lengua.png", "ruta": "escuela/materias"},
                {"tipo": "item", "label": "Música", "img": "musica.png", "ruta": "escuela/materias"},
                {"tipo": "item", "label": "Arte", "img": "arte.png", "ruta": "escuela/materias"},
            ],
            "animales": [
                {"tipo": "folder", "label": "Mascotas", "id": "mascotas", "color": "#D7CCC8"},
                {"tipo": "folder", "label": "Granja", "id": "granja", "color": "#D7CCC8"},
                {"tipo": "folder", "label": "Selva", "id": "selva", "color": "#D7CCC8"},
                {"tipo": "folder", "label": "Mar", "id": "mar", "color": "#D7CCC8"},
                {"tipo": "folder", "label": "Insectos", "id": "insectos", "color": "#D7CCC8"},
            ],
            "mascotas": [
                {"tipo": "item", "label": "Perro", "img": "perro.png", "ruta": "animales/mascotas"},
                {"tipo": "item", "label": "Gato", "img": "gato.png", "ruta": "animales/mascotas"},
                {"tipo": "item", "label": "Conejo", "img": "conejo.png", "ruta": "animales/mascotas"},
                {"tipo": "item", "label": "Pez", "img": "pez.png", "ruta": "animales/mascotas"},
                {"tipo": "item", "label": "Loro", "img": "loro.png", "ruta": "animales/mascotas"},
            ],
            "granja": [
                {"tipo": "item", "label": "Vaca", "img": "vaca.png", "ruta": "animales/granja"},
                {"tipo": "item", "label": "Caballo", "img": "caballo.png", "ruta": "animales/granja"},
                {"tipo": "item", "label": "Cerdo", "img": "cerdo.png", "ruta": "animales/granja"},
                {"tipo": "item", "label": "Oveja", "img": "oveja.png", "ruta": "animales/granja"},
                {"tipo": "item", "label": "Gallina", "img": "gallina.png", "ruta": "animales/granja"},
            ],
            "selva": [
                {"tipo": "item", "label": "León", "img": "leon.png", "ruta": "animales/selva"},
                {"tipo": "item", "label": "Elefante", "img": "elefante.png", "ruta": "animales/selva"},
                {"tipo": "item", "label": "Mono", "img": "mono.png", "ruta": "animales/selva"},
                {"tipo": "item", "label": "Jirafa", "img": "jirafa.png", "ruta": "animales/selva"},
                {"tipo": "item", "label": "Tigre", "img": "tigre.png", "ruta": "animales/selva"},
            ],
            "mar": [
                {"tipo": "item", "label": "Ballena", "img": "ballena.png", "ruta": "animales/mar"},
                {"tipo": "item", "label": "Delfín", "img": "delfin.png", "ruta": "animales/mar"},
                {"tipo": "item", "label": "Tiburón", "img": "tiburon.png", "ruta": "animales/mar"},
                {"tipo": "item", "label": "Pulpo", "img": "pulpo.png", "ruta": "animales/mar"},
            ],
            "insectos": [
                {"tipo": "item", "label": "Mariposa", "img": "mariposa.png", "ruta": "animales/insectos"},
                {"tipo": "item", "label": "Abeja", "img": "abeja.png", "ruta": "animales/insectos"},
                {"tipo": "item", "label": "Araña", "img": "araña.png", "ruta": "animales/insectos"},
            ],
            "tiempo": [
                {"tipo": "folder", "label": "Clima", "id": "clima", "color": "#90CAF9"},
                {"tipo": "folder", "label": "Días", "id": "dias", "color": "#9FA8DA"},
                {"tipo": "item", "label": "Hoy", "img": "hoy.png", "ruta": "tiempo"},
                {"tipo": "item", "label": "Mañana", "img": "mañana.png", "ruta": "tiempo"},
                {"tipo": "item", "label": "Ayer", "img": "ayer.png", "ruta": "tiempo"},
                {"tipo": "item", "label": "Día", "img": "dia.png", "ruta": "tiempo"},
                {"tipo": "item", "label": "Noche", "img": "noche.png", "ruta": "tiempo"},
            ],
            "clima": [
                {"tipo": "item", "label": "Sol", "img": "sol.png", "ruta": "clima"},
                {"tipo": "item", "label": "Lluvia", "img": "lluvia.png", "ruta": "clima"},
                {"tipo": "item", "label": "Frío", "img": "frio.png", "ruta": "clima"},
                {"tipo": "item", "label": "Calor", "img": "calor.png", "ruta": "clima"},
                {"tipo": "item", "label": "Nieve", "img": "nieve.png", "ruta": "clima"},
            ],
            "dias": [
                {"tipo": "item", "label": "Lunes", "img": "lunes.png", "ruta": "dias"},
                {"tipo": "item", "label": "Martes", "img": "martes.png", "ruta": "dias"},
                {"tipo": "item", "label": "Miércoles", "img": "miercoles.png", "ruta": "dias"},
                {"tipo": "item", "label": "Jueves", "img": "jueves.png", "ruta": "dias"},
                {"tipo": "item", "label": "Viernes", "img": "viernes.png", "ruta": "dias"},
                {"tipo": "item", "label": "Sábado", "img": "sabado.png", "ruta": "dias"},
                {"tipo": "item", "label": "Domingo", "img": "domingo.png", "ruta": "dias"},
            ],
            "juguetes": [
                {"tipo": "item", "label": "Pelota", "img": "pelota.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Muñeca", "img": "muñeca.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Coche", "img": "coche.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Tren", "img": "tren.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Bloques", "img": "bloques.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Puzzle", "img": "rompecabezas.png", "ruta": "juguetes"},
                {"tipo": "item", "label": "Tablet", "img": "tablet.png", "ruta": "juguetes"},
            ],
            "colores": [
                {"tipo": "item", "label": "Rojo", "img": "rojo.png", "ruta": "colores"},
                {"tipo": "item", "label": "Azul", "img": "azul.png", "ruta": "colores"},
                {"tipo": "item", "label": "Amarillo", "img": "amarillo.png", "ruta": "colores"},
                {"tipo": "item", "label": "Verde", "img": "verde.png", "ruta": "colores"},
                {"tipo": "item", "label": "Naranja", "img": "color naranja.png", "ruta": "colores"},
                {"tipo": "item", "label": "Rosa", "img": "rosa.png", "ruta": "colores"},
                {"tipo": "item", "label": "Negro", "img": "negro.png", "ruta": "colores"},
                {"tipo": "item", "label": "Blanco", "img": "blanco.png", "ruta": "colores"},
            ],
            "personas": [
                {"tipo": "folder", "label": "Profesiones", "id": "profesiones", "color": "#FFAB91"},
                {"tipo": "item", "label": "Mamá", "img": "mama.png", "ruta": "personas"},
                {"tipo": "item", "label": "Papá", "img": "papá.png", "ruta": "personas"},
                {"tipo": "item", "label": "Bebé", "img": "bebe.png", "ruta": "personas"},
                {"tipo": "item", "label": "Abuelo", "img": "abuelo.png", "ruta": "personas"},
                {"tipo": "item", "label": "Abuela", "img": "abuela.png", "ruta": "personas"},
                {"tipo": "item", "label": "Hermano", "img": "hermano.png", "ruta": "personas"},
                {"tipo": "item", "label": "Hermana", "img": "hermana.png", "ruta": "personas"},
                {"tipo": "item", "label": "Amigo", "img": "amigo.png", "ruta": "personas"},
                {"tipo": "item", "label": "Niño", "img": "niño.png", "ruta": "personas"},
                {"tipo": "item", "label": "Niña", "img": "niña.png", "ruta": "personas"},
            ],
            "profesiones": [
                {"tipo": "item", "label": "Maestra", "img": "maestra.png", "ruta": "personas/profesiones"},
                {"tipo": "item", "label": "Médico", "img": "medico.png", "ruta": "personas/profesiones"},
                {"tipo": "item", "label": "Policía", "img": "policia.png", "ruta": "personas/profesiones"},
                {"tipo": "item", "label": "Bombero", "img": "bombero.png", "ruta": "personas/profesiones"},
            ],
            "cuerpo": [
                {"tipo": "item", "label": "Cabeza", "img": "cabeza.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Mano", "img": "mano.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Pie", "img": "pie.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Barriga", "img": "barriga.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Ojo", "img": "ojo.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Boca", "img": "boca.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Nariz", "img": "nariz.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Oreja", "img": "oreja.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Brazo", "img": "brazo.png", "ruta": "cuerpo"},
                {"tipo": "item", "label": "Pierna", "img": "pierna.png", "ruta": "cuerpo"},
            ],
            "salud": [
                {"tipo": "item", "label": "Medicina", "img": "medicina.png", "ruta": "salud"},
                {"tipo": "item", "label": "Jarabe", "img": "jarabe.png", "ruta": "salud"},
                {"tipo": "item", "label": "Fiebre", "img": "fiebre.png", "ruta": "salud"},
                {"tipo": "item", "label": "Tos", "img": "tos.png", "ruta": "salud"},
                {"tipo": "item", "label": "Hospital", "img": "hospital.png", "ruta": "salud"},
                {"tipo": "item", "label": "Ambulancia", "img": "ambulancia.png", "ruta": "salud"},
            ],
            "formas": [
                {"tipo": "item", "label": "Círculo", "img": "circulo.png", "ruta": "formas"},
                {"tipo": "item", "label": "Cuadrado", "img": "cuadrado.png", "ruta": "formas"},
                {"tipo": "item", "label": "Triángulo", "img": "triangulo.png", "ruta": "formas"},
                {"tipo": "item", "label": "Estrella", "img": "estrella.jpg", "ruta": "formas"},
                {"tipo": "item", "label": "Corazón", "img": "corazon.png", "ruta": "formas"},
            ],
            "transporte": [
                {"tipo": "item", "label": "Coche", "img": "coche.png", "ruta": "transporte"},
                {"tipo": "item", "label": "Autobús", "img": "autobus.png", "ruta": "transporte"},
                {"tipo": "item", "label": "Camión", "img": "camion.png", "ruta": "transporte"},
                {"tipo": "item", "label": "Avión", "img": "avion.png", "ruta": "transporte"},
                {"tipo": "item", "label": "Tren", "img": "tren.png", "ruta": "transporte"},
                {"tipo": "item", "label": "Bici", "img": "bicicleta.png", "ruta": "transporte"},
            ],
            "descriptivos": [
                {"tipo": "item", "label": "Grande", "img": "grande.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Pequeño", "img": "pequeño.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Bueno", "img": "bueno.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Malo", "img": "malo.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Limpio", "img": "limpio.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Sucio", "img": "sucio.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Rápido", "img": "rapido.png", "ruta": "descriptivos"},
                {"tipo": "item", "label": "Lento", "img": "lento.png", "ruta": "descriptivos"},
            ]
        }

        self.history = ["root"]
        self.crear_interfaz()
        self.cargar_vista("root")

    def crear_interfaz(self):
        # --- BARRA SUPERIOR ---
        self.nav_frame = tk.Frame(self.root, bg=Config.HEADER_BG, height=80)
        self.nav_frame.pack(fill="x", side="top")
        
        # Contenedor botones Izquierda
        self.left_nav = tk.Frame(self.nav_frame, bg=Config.HEADER_BG)
        self.left_nav.pack(side="left", padx=10)

        self.btn_back = tk.Button(self.left_nav, text="⬅ ATRÁS", font=("Segoe UI", 12, "bold"),
                                  bg=Config.BTN_BACK_BG, fg=Config.TEXT_COLOR, 
                                  activebackground="#FFF9C4", activeforeground=Config.TEXT_COLOR,
                                  command=self.ir_atras, relief="flat", bd=0, padx=20, pady=10)
        self.btn_back.pack(side="left", padx=5)
        
        # Botón Inicio
        self.btn_home = tk.Button(self.left_nav, text="🏠 INICIO", font=("Segoe UI", 12, "bold"),
                                  bg=Config.BTN_BACK_BG, fg=Config.TEXT_COLOR, 
                                  activebackground="#FFF9C4", activeforeground=Config.TEXT_COLOR,
                                  command=self.ir_inicio, relief="flat", bd=0, padx=20, pady=10)
        self.btn_home.pack(side="left", padx=5)
        
        # Título carpeta
        self.lbl_path = tk.Label(self.nav_frame, text="INICIO", font=("Segoe UI", 20, "bold"),
                                 bg=Config.HEADER_BG, fg=Config.TEXT_COLOR)
        self.lbl_path.pack(side="left", padx=20)

        # --- BARRA DE FRASE ---
        self.frame_frase = tk.Frame(self.root, bg="white", height=130, bd=2, relief="solid")
        self.frame_frase.pack(fill="x", padx=20, pady=10)
        self.frame_frase.pack_propagate(False)

        # Contenedor Pictogramas Frase
        self.frase_container = tk.Frame(self.frame_frase, bg="white")
        self.frase_container.pack(side="left", fill="y", padx=10)

        # Botones Acciones (Derecha)
        self.actions_frame = tk.Frame(self.frame_frase, bg="white")
        self.actions_frame.pack(side="right", padx=10)

        btn_play = tk.Button(self.actions_frame, text="▶️ LEER", font=("Segoe UI", 12, "bold"),
                             bg="#81C784", fg="white", relief="flat", command=self.leer_frase_completa)
        btn_play.pack(side="left", padx=5)

        btn_del = tk.Button(self.actions_frame, text="⌫", font=("Segoe UI", 14, "bold"),
                            bg="#E57373", fg="white", relief="flat", command=self.borrar_ultimo)
        btn_del.pack(side="left", padx=5)

        btn_clear = tk.Button(self.actions_frame, text="🗑️", font=("Segoe UI", 14, "bold"),
                              bg="#D32F2F", fg="white", relief="flat", command=self.limpiar_frase)
        btn_clear.pack(side="left", padx=5)

        # --- ÁREA DE SCROLL PARA CONTENIDO ---
        # Marco contenedor para el Canvas y Scrollbar
        self.main_container = tk.Frame(self.root, bg=Config.BG_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.main_container, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # Canvas
        self.canvas = tk.Canvas(self.main_container, bg=Config.BG_COLOR, highlightthickness=0,
                                yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Vincular scrollbar al canvas
        self.scrollbar.config(command=self.canvas.yview)

        # Frame interno (donde van los botones)
        self.container = tk.Frame(self.canvas, bg=Config.BG_COLOR)
        
        # Crear ventana dentro del canvas
        self.canvas_window = self.canvas.create_window((0,0), window=self.container, anchor="n")

        # Eventos para el scroll
        self.container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind MouseWheel
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def on_frame_configure(self, event):
        # Actualizar región de scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Ajustar ancho del frame interno al ancho del canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Scroll con la rueda
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def cargar_vista(self, folder_id):
        # Limpiar frame interno
        for widget in self.container.winfo_children():
            widget.destroy()
            
        items = self.DATA.get(folder_id, [])
        
        if len(self.history) > 1:
            self.btn_back.config(state="normal", bg=Config.BTN_BACK_BG, cursor="hand2")
        else:
            self.btn_back.config(state="disabled", bg="#FFECB3", cursor="arrow")
        
        titulo = "INICIO" if folder_id == "root" else folder_id.upper()
        self.lbl_path.config(text=titulo)

        # Grid con peso para centrado
        for i in range(Config.GRID_COLS):
            self.container.columnconfigure(i, weight=1)

        row, col = 0, 0
        for item in items:
            # Frame del botón
            frame_btn = tk.Frame(self.container, bg=Config.BG_COLOR)
            frame_btn.grid(row=row, column=col, padx=10, pady=15, sticky="n") # Sticky North para alinear arriba
            
            img_name = item.get("img", None)
            ruta_rel = item.get("ruta", "")
            emoji = item.get("emoji", None)
            es_carpeta = (item["tipo"] == "folder")
            
            if "color" in item:
                color_bg = item["color"]
            else:
                color_bg = Config.FOLDER_COLOR if es_carpeta else Config.ITEM_COLOR
            
            photo = self.generar_icono(item["label"], color_bg, es_carpeta, img_name, ruta_rel, emoji)
            
            btn = tk.Button(frame_btn, image=photo, bg=Config.BG_COLOR, 
                            activebackground=Config.BG_COLOR,
                            bd=0, relief="flat", cursor="hand2",
                            command=lambda i=item: self.al_pulsar(i))
            btn.image = photo 
            btn.pack()
            
            lbl = tk.Label(frame_btn, text=item["label"], font=("Segoe UI", 13, "bold"), 
                           bg=Config.BG_COLOR, fg=Config.TEXT_COLOR)
            lbl.pack(pady=5)
            
            col += 1
            if col >= Config.GRID_COLS:
                col = 0; row += 1
        
        # Resetear scroll al cambiar vista
        self.canvas.yview_moveto(0)

    def al_pulsar(self, item):
        if item["tipo"] == "folder":
            next_id = item["id"]
            if next_id in self.DATA:
                self.history.append(next_id)
                self.cargar_vista(next_id)
            else:
                messagebox.showinfo("Info", "Carpeta vacía")
        elif item["tipo"] == "item":
            self.agregar_a_frase(item)
            texto = item.get("text", item.get("label"))
            self.reproducir_audio(texto)

    # --- FUNCIONES BARRA FRASE ---
    def agregar_a_frase(self, item):
        self.frase_actual.append(item)
        self.dibujar_frase()

    def borrar_ultimo(self):
        if self.frase_actual:
            self.frase_actual.pop()
            self.dibujar_frase()

    def limpiar_frase(self):
        self.frase_actual = []
        self.dibujar_frase()

    def leer_frase_completa(self):
        if not self.frase_actual: return
        texto_completo = ""
        for item in self.frase_actual:
            t = item.get("text", item.get("label"))
            texto_completo += t + " "
        self.reproducir_audio(texto_completo.strip())

    def dibujar_frase(self):
        for w in self.frase_container.winfo_children():
            w.destroy()
            
        for item in self.frase_actual:
            frame = tk.Frame(self.frase_container, bg="white")
            frame.pack(side="left", padx=5, pady=5)
            
            img_name = item.get("img", None)
            ruta_rel = item.get("ruta", "")
            emoji = item.get("emoji", None)
            label = item.get("label", "")
            
            photo = self.generar_icono(label, "#FFFFFF", False, img_name, ruta_rel, emoji, size=Config.MINI_ICON_SIZE)
            
            lbl_img = tk.Label(frame, image=photo, bg="white")
            lbl_img.image = photo
            lbl_img.pack()
            
            lbl_txt = tk.Label(frame, text=label, font=("Segoe UI", 10), bg="white")
            lbl_txt.pack()

    def ir_atras(self):
        if len(self.history) > 1:
            self.history.pop()
            self.cargar_vista(self.history[-1])

    def ir_inicio(self):
        self.history = ["root"]
        self.cargar_vista("root")

    def reproducir_audio(self, texto):
        threading.Thread(target=self._generar_y_reproducir, args=(texto,), daemon=True).start()

    def _generar_y_reproducir(self, texto):
        nombre_clean = "".join(c for c in texto if c.isalnum() or c.isspace()).lower().strip().replace(" ", "_")[:30]
        nombre_archivo = f"{nombre_clean}.mp3"
        ruta_audio = os.path.join(self.audio_dir, nombre_archivo)

        if not os.path.exists(ruta_audio):
            try:
                tts = gTTS(text=texto, lang='es')
                tts.save(ruta_audio)
            except Exception as e:
                print(f"Error gTTS: {e}")
                return

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta_audio)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error pygame: {e}")

    def generar_icono(self, texto, color, es_carpeta, nombre_archivo=None, ruta_relativa="", emoji_char=None, size=Config.ICON_SIZE):
        s = size
        border_color = Config.FOLDER_BORDER if es_carpeta else Config.ITEM_BORDER
        
        img = Image.new("RGBA", (s, s), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        self.draw_rounded_rect_pil(draw, 0, 0, s, s, 15, color)
        self.draw_rounded_rect_pil(draw, 0, 0, s, s, 15, outline=border_color, width=3)

        if es_carpeta:
            draw.polygon([(0,0), (s//2, 0), (s//2 + 15, 20), (0, 20)], fill=border_color)

        img_cargada = False
        if nombre_archivo:
            base_path = os.path.dirname(os.path.abspath(__file__))
            ruta_completa = os.path.join(base_path, Config.CARPETA_IMG, ruta_relativa, nombre_archivo)
            
            if os.path.exists(ruta_completa):
                try:
                    pic = Image.open(ruta_completa).convert("RGBA")
                    margin = int(s * 0.15)
                    max_w = s - margin * 2
                    max_h = s - margin * 2
                    pic.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                    
                    offset_x = (s - pic.width) // 2
                    offset_y = (s - pic.height) // 2
                    
                    img.paste(pic, (offset_x, offset_y), pic)
                    img_cargada = True
                except: pass

        if not img_cargada:
            contenido = emoji_char if emoji_char else texto[0].upper()
            font_size = int(s * 0.5)
            try: font = ImageFont.truetype("seguiemj.ttf", font_size) 
            except: 
                try: font = ImageFont.truetype("arial.ttf", font_size)
                except: font = ImageFont.load_default()
            
            try:
                bbox = draw.textbbox((0,0), contenido, font=font)
                w_txt = bbox[2] - bbox[0]
                h_txt = bbox[3] - bbox[1]
                draw.text(((s - w_txt) // 2, (s - h_txt) // 2 - (font_size * 0.1)), contenido, fill=Config.TEXT_COLOR, font=font)
            except:
                draw.text((s//3, s//3), contenido, fill=Config.TEXT_COLOR)

        return ImageTk.PhotoImage(img)

    def draw_rounded_rect_pil(self, draw, x, y, w, h, r, fill=None, outline=None, width=1):
        draw.rounded_rectangle((x, y, x+w, y+h), radius=r, fill=fill, outline=outline, width=width)

if __name__ == "__main__":
    root = tk.Tk()
    app = TEAyudoApp(root)
    root.mainloop()