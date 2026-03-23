"""
src/gui/app.py
Ventana principal de TinyPS con distribución en 4 cuadrantes.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2

from services.file_service import FileService
from processors.image_processor import ImageProcessor
from utils.image_utils import ImageUtils


class TinyPSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyPS - Editor de Imágenes con IA")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)

        # Inicializar servicios y procesadores
        self.file_service = FileService()
        self.image_processor = ImageProcessor()
        self.image_utils = ImageUtils()

        # Variables de estado
        self.original_image = None      # Imagen original (numpy array BGR)
        self.current_image = None       # Imagen actual (numpy array BGR)
        self.tk_image = None            # Imagen para mostrar en canvas
        self.modified = False           # Flag para saber si hay cambios sin guardar
        self.last_transform_image = None # Última imagen antes de voltear (para reset)

        # Variables para controles
        self.r_value = tk.IntVar(value=0)
        self.g_value = tk.IntVar(value=0)
        self.b_value = tk.IntVar(value=0)
        self.blur_value = tk.IntVar(value=0)
        self.angle_value = tk.IntVar(value=0)
        
        # Variables para selección de figuras
        self.selection_mode = tk.StringVar(value="ninguno")  # ninguno, cuadrado, circulo
        self.size_percent = tk.IntVar(value=10)  # Tamaño en porcentaje (1-100)
        
        # Variables para coordenadas
        self.x_pos = tk.IntVar(value=0)
        self.y_pos = tk.IntVar(value=0)

        # Configurar la interfaz
        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        """Configura los 4 cuadrantes principales"""
        # Configurar grid principal (2x2)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Cuadrante 1: Superior Izquierdo (Cargar + Canvas)
        self.frame_top_left = ttk.Frame(self.root, relief="solid", borderwidth=1)
        self.frame_top_left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self._setup_quadrant1()

        # Cuadrante 2: Superior Derecho (Controles RGB, Blur, Voltear, Reset)
        self.frame_top_right = ttk.Frame(self.root, relief="solid", borderwidth=1)
        self.frame_top_right.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self._setup_quadrant2()

        # Cuadrante 3: Inferior Izquierdo (Selección: Ninguno/Cuadrado/Círculo + tamaño)
        self.frame_bottom_left = ttk.Frame(self.root, relief="solid", borderwidth=1)
        self.frame_bottom_left.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self._setup_quadrant3()

        # Cuadrante 4: Inferior Derecho (Ángulo con slider y plano cartesiano)
        self.frame_bottom_right = ttk.Frame(self.root, relief="solid", borderwidth=1)
        self.frame_bottom_right.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self._setup_quadrant4()

    def _setup_quadrant1(self):
        """Cuadrante 1: Botón cargar + Canvas para la imagen"""
        inner = ttk.Frame(self.frame_top_left)
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        btn_load = ttk.Button(inner, text="📁 Cargar Imagen", command=self.load_image)
        btn_load.pack(pady=(0, 10))

        canvas_frame = ttk.Frame(inner)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="gray20", highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

    def _setup_quadrant2(self):
        """Cuadrante 2: Controles RGB, Blur, botones voltear y reset"""
        inner = ttk.Frame(self.frame_top_right)
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(inner, text="Controles de Edición", font=("Arial", 12, "bold")).pack(pady=(0, 15))

        # Sliders RGB
        self._create_slider(inner, "🔴 R:", self.r_value, 0, 255, self.on_rgb_change)
        self._create_slider(inner, "🟢 G:", self.g_value, 0, 255, self.on_rgb_change)
        self._create_slider(inner, "🔵 B:", self.b_value, 0, 255, self.on_rgb_change)

        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=10)

        # Slider Blur
        self._create_slider(inner, "✨ Blur:", self.blur_value, 0, 20, self.on_blur_change)

        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=10)

        # Botones para voltear
        flip_frame = ttk.Frame(inner)
        flip_frame.pack(fill="x", pady=5)
        
        ttk.Label(flip_frame, text="🔄 Voltear:", width=15).pack(side="left")
        
        btn_flip_horizontal = ttk.Button(flip_frame, text="Horizontal", command=self.on_flip_horizontal)
        btn_flip_horizontal.pack(side="left", padx=5)
        
        btn_flip_vertical = ttk.Button(flip_frame, text="Vertical", command=self.on_flip_vertical)
        btn_flip_vertical.pack(side="left", padx=5)
        
        # Botón Reset
        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=10)
        
        reset_frame = ttk.Frame(inner)
        reset_frame.pack(fill="x", pady=5)
        
        btn_reset = ttk.Button(reset_frame, text="🔄 Reset (Original)", command=self.on_reset)
        btn_reset.pack(fill="x", pady=5)

    def _setup_quadrant3(self):
        """Cuadrante 3: Selección (Ninguno/Cuadrado/Círculo) + tamaño y coordenadas"""
        inner = ttk.Frame(self.frame_bottom_left)
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(inner, text="Dibujo de Figuras", font=("Arial", 12, "bold")).pack(pady=(0, 15))

        # Radio buttons para selección de figura
        radio_frame = ttk.Frame(inner)
        radio_frame.pack(fill="x", pady=5)
        ttk.Radiobutton(radio_frame, text="Ninguno", variable=self.selection_mode, 
                       value="ninguno", command=self.on_selection_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Cuadrado", variable=self.selection_mode, 
                       value="cuadrado", command=self.on_selection_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Círculo", variable=self.selection_mode, 
                       value="circulo", command=self.on_selection_mode_change).pack(side="left", padx=5)

        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=10)

        # Slider para tamaño
        self._create_slider(inner, "📏 Tamaño (%):", self.size_percent, 1, 100, self.on_size_change)
        
        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=10)

        # Sliders para coordenadas
        self._create_slider(inner, "📍 Posición X:", self.x_pos, 0, 1000, self.on_coord_change)
        self._create_slider(inner, "📍 Posición Y:", self.y_pos, 0, 1000, self.on_coord_change)

        # Label para información
        self.selection_info = ttk.Label(inner, text="Información: --", relief="sunken", anchor="center")
        self.selection_info.pack(fill="x", pady=(15, 0))

    def _setup_quadrant4(self):
        """Cuadrante 4: Ángulo y plano cartesiano"""
        inner = ttk.Frame(self.frame_bottom_right)
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(inner, text="Rotación", font=("Arial", 12, "bold")).pack(pady=(0, 15))

        self._create_slider(inner, "🔄 Ángulo:", self.angle_value, -180, 180, self.on_angle_change)

        angle_canvas_frame = ttk.Frame(inner)
        angle_canvas_frame.pack(fill="both", expand=True, pady=10)

        self.angle_canvas = tk.Canvas(angle_canvas_frame, width=200, height=200, bg="white", 
                                      highlightthickness=1, relief="sunken")
        self.angle_canvas.pack(pady=10)
        self._draw_coordinate_plane()

    def _create_slider(self, parent, label, variable, from_, to_, command):
        """Helper para crear un slider con label y valor numérico"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=3)

        label_frame = ttk.Frame(frame)
        label_frame.pack(fill="x")
        
        ttk.Label(label_frame, text=label, width=15).pack(side="left")
        value_label = ttk.Label(label_frame, textvariable=variable, width=5)
        value_label.pack(side="right")

        slider = ttk.Scale(frame, from_=from_, to=to_, orient="horizontal",
                           variable=variable, command=command)
        slider.pack(fill="x", pady=(2, 0))

    def _draw_coordinate_plane(self):
        """Dibuja el plano cartesiano de 360° en el canvas de ángulo"""
        self.angle_canvas.delete("all")
        w, h = 200, 200
        cx, cy = w // 2, h // 2

        self.angle_canvas.create_oval(10, 10, w-10, h-10, outline="gray", width=2)
        self.angle_canvas.create_line(cx, 10, cx, h-10, fill="black", width=1, dash=(2, 4))
        self.angle_canvas.create_line(10, cy, w-10, cy, fill="black", width=1, dash=(2, 4))

        for angle, text in [(0, "0°"), (90, "90°"), (-90, "-90°"), (180, "180°"), (-180, "-180°")]:
            rad = np.radians(angle)
            x = cx + 80 * np.sin(rad)
            y = cy - 80 * np.cos(rad)
            self.angle_canvas.create_text(x, y, text=text, font=("Arial", 8))

        self.angle_line = self.angle_canvas.create_line(cx, cy, cx, cy-70, fill="red", width=2, arrow="last")

    def _update_angle_indicator(self, angle_deg):
        """Actualiza la línea del plano cartesiano según el ángulo"""
        w, h = 200, 200
        cx, cy = w // 2, h // 2
        rad = np.radians(angle_deg)
        x = cx + 70 * np.sin(rad)
        y = cy - 70 * np.cos(rad)
        self.angle_canvas.coords(self.angle_line, cx, cy, x, y)

    def _draw_shape_with_contour(self, image, x, y, shape_type, size_px):
        """
        Dibuja una figura usando la técnica de contornos.
        Crea una máscara con la figura y luego encuentra su contorno para dibujarlo.
        """
        h, w = image.shape[:2]
        
        # Crear una máscara en blanco del mismo tamaño que la imagen
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Dibujar la figura en la máscara
        if shape_type == "cuadrado":
            half_size = size_px // 2
            top_left = (max(0, x - half_size), max(0, y - half_size))
            bottom_right = (min(w, x + half_size), min(h, y + half_size))
            cv2.rectangle(mask, top_left, bottom_right, 255, -1)
            
        elif shape_type == "circulo":
            radius = size_px // 2
            cv2.circle(mask, (x, y), radius, 255, -1)
        
        # Encontrar contornos en la máscara
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dibujar los contornos encontrados en la imagen original
        result = image.copy()
        for contour in contours:
            # Calcular área del contorno
            area = cv2.contourArea(contour)
            
            # Obtener rectángulo delimitador
            rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
            
            # Aproximar polígono para mejor precisión
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Dibujar el contorno en verde con grosor 3
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 3)
            
            # Calcular y mostrar información adicional (opcional)
            if shape_type == "cuadrado":
                aspect_ratio = float(rect_w) / rect_h
                info_text = f"Rect: {rect_w}x{rect_h}"
            else:
                info_text = f"Circ: r={radius}"
            
            # Posicionar el texto cerca del contorno
            cv2.putText(result, info_text, (rect_x, rect_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return result, contours

    def _draw_shape_on_canvas(self):
        """Dibuja la figura seleccionada usando detección de contornos"""
        if self.current_image is None:
            return
        
        mode = self.selection_mode.get()
        if mode == "ninguno":
            self._update_display()
            return
        
        # Obtener coordenadas y tamaño
        x = self.x_pos.get()
        y = self.y_pos.get()
        size_percent = self.size_percent.get() / 100.0
        
        # Calcular tamaño basado en el menor lado de la imagen
        h, w = self.current_image.shape[:2]
        max_size = min(w, h)
        shape_size = int(max_size * size_percent)
        
        # Asegurar que las coordenadas estén dentro de los límites
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        
        # Dibujar la figura usando contornos
        display_image, contours = self._draw_shape_with_contour(
            self.current_image, x, y, mode, shape_size
        )
        
        # Actualizar información
        if contours:
            contour = contours[0]
            area = cv2.contourArea(contour)
            rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
            
            if mode == "cuadrado":
                info = f"Cuadrado detectado en ({x}, {y}) | Área: {area:.0f}px² | Tamaño: {rect_w}x{rect_h}px"
            else:
                radius = shape_size // 2
                info = f"Círculo detectado en ({x}, {y}) | Área: {area:.0f}px² | Radio: {radius}px"
        else:
            info = f"{mode.capitalize()} en ({x}, {y}) | Tamaño: {shape_size}px"
        
        self.selection_info.config(text=info)
        
        # Mostrar la imagen con el contorno dibujado
        pil_image = self.image_utils.cv2_to_pil(display_image)
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _setup_bindings(self):
        """Configura eventos adicionales"""
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # ==================== EVENTOS ====================

    def load_image(self):
        """Carga una imagen desde el sistema de archivos"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.original_image = self.file_service.load_image(filepath)
            self.current_image = self.original_image.copy()
            self.last_transform_image = self.original_image.copy()
            self.modified = False
            self._reset_sliders()
            self._update_display()

    def _reset_sliders(self):
        """Restablece todos los sliders a sus valores por defecto"""
        self.r_value.set(0)
        self.g_value.set(0)
        self.b_value.set(0)
        self.blur_value.set(0)
        self.angle_value.set(0)
        self.selection_mode.set("ninguno")
        self.size_percent.set(10)
        self.x_pos.set(0)
        self.y_pos.set(0)
        self._update_angle_indicator(0)

    def on_reset(self):
        """Restablece la imagen a su estado original (resetea RGB, Blur, Ángulo y Volteos)"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.last_transform_image = self.original_image.copy()
            self._reset_sliders()
            self._update_display()
            self.selection_info.config(text="Imagen restablecida a original")

    def _update_display(self):
        """Actualiza el canvas con la imagen actual"""
        if self.current_image is None:
            return

        pil_image = self.image_utils.cv2_to_pil(self.current_image)
        self.tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    # ==================== HANDLERS DE CONTROLES ====================

    def on_rgb_change(self, event=None):
        """Aplica ajuste RGB cuando cambian los sliders"""
        if self.original_image is None:
            return
        r = self.r_value.get()
        g = self.g_value.get()
        b = self.b_value.get()
        self.current_image = self.image_processor.adjust_rgb(self.original_image, r, g, b)
        self.last_transform_image = self.current_image.copy()
        self._draw_shape_on_canvas()

    def on_blur_change(self, event=None):
        """Aplica blur cuando cambia el slider"""
        if self.original_image is None:
            return
        blur = self.blur_value.get()
        self.current_image = self.image_processor.apply_blur(self.original_image, blur)
        self.last_transform_image = self.current_image.copy()
        self._draw_shape_on_canvas()

    def on_angle_change(self, event=None):
        """Aplica rotación cuando cambia el slider de ángulo"""
        if self.original_image is None:
            return
        angle = self.angle_value.get()
        self._update_angle_indicator(angle)
        self.current_image = self.image_processor.rotate(self.original_image, angle)
        self.last_transform_image = self.current_image.copy()
        self._draw_shape_on_canvas()

    def on_flip_horizontal(self):
        """Voltea la imagen horizontalmente sobre la imagen actual"""
        if self.current_image is None:
            return
        # Guardar estado actual antes de voltear
        self.last_transform_image = self.current_image.copy()
        self.current_image = self.image_processor.flip_horizontal(self.current_image)
        self._draw_shape_on_canvas()

    def on_flip_vertical(self):
        """Voltea la imagen verticalmente sobre la imagen actual"""
        if self.current_image is None:
            return
        # Guardar estado actual antes de voltear
        self.last_transform_image = self.current_image.copy()
        self.current_image = self.image_processor.flip_vertical(self.current_image)
        self._draw_shape_on_canvas()

    def on_selection_mode_change(self):
        """Cuando cambia el modo de selección, redibuja la figura"""
        if self.current_image is not None:
            self._draw_shape_on_canvas()

    def on_size_change(self, event=None):
        """Cuando cambia el tamaño, redibuja la figura"""
        if self.current_image is not None and self.selection_mode.get() != "ninguno":
            self._draw_shape_on_canvas()

    def on_coord_change(self, event=None):
        """Maneja cambios en los sliders de coordenadas"""
        if self.current_image is not None and self.selection_mode.get() != "ninguno":
            self._draw_shape_on_canvas()
        elif self.current_image is not None:
            x = self.x_pos.get()
            y = self.y_pos.get()
            h, w = self.current_image.shape[:2]
            if 0 <= x < w and 0 <= y < h:
                b, g, r = self.current_image[y, x]
                self.selection_info.config(text=f"Coordenadas ({x}, {y}) | RGB({r}, {g}, {b})")
            else:
                self.selection_info.config(text=f"Coordenadas fuera de la imagen")

    def on_mouse_move(self, event):
        """Actualiza los sliders de coordenadas según la posición del mouse"""
        if self.current_image is None:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        img_width = self.current_image.shape[1]
        img_height = self.current_image.shape[0]

        if 0 <= x < img_width and 0 <= y < img_height:
            self.x_pos.set(int(x))
            self.y_pos.set(int(y))

    def on_canvas_click(self, event):
        """Dibuja la figura al hacer click en el canvas"""
        if self.current_image is not None and self.selection_mode.get() != "ninguno":
            self._draw_shape_on_canvas()


def main():
    root = tk.Tk()
    app = TinyPSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()