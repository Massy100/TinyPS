"""
src/processors/image_processor.py
Procesador de imágenes con operaciones básicas y efectos.
"""

import cv2
import numpy as np


class ImageProcessor:
    """Clase que maneja todas las transformaciones de imagen"""
    
    def __init__(self):
        """Inicializa el procesador"""
        pass
    
    def adjust_rgb(self, image, r_adjust=0, g_adjust=0, b_adjust=0):
        """
        Ajusta los canales RGB de la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR (OpenCV)
            r_adjust (int): Valor de ajuste para rojo (-255 a 255)
            g_adjust (int): Valor de ajuste para verde (-255 a 255)
            b_adjust (int): Valor de ajuste para azul (-255 a 255)
            
        Returns:
            numpy.ndarray: Imagen con ajuste RGB aplicado
        """
        # Hacer una copia para no modificar la original
        result = image.copy().astype(np.int16)
        
        # OpenCV usa BGR, así que:
        # Canal 0 = Blue, Canal 1 = Green, Canal 2 = Red
        result[:, :, 0] = np.clip(result[:, :, 0] + b_adjust, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] + g_adjust, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] + r_adjust, 0, 255)
        
        return result.astype(np.uint8)
    
    def apply_blur(self, image, radius=0):
        """
        Aplica desenfoque gaussiano a la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            radius (int): Radio del desenfoque (0 = sin desenfoque, valores impares recomendados)
            
        Returns:
            numpy.ndarray: Imagen con desenfoque aplicado
        """
        if radius <= 0:
            return image.copy()
        
        # El kernel debe ser impar, así que aseguramos que sea impar
        kernel_size = radius * 2 + 1 if radius % 2 == 0 else radius
        kernel_size = max(1, kernel_size)
        
        # Aplicar desenfoque gaussiano
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        return result
    
    def detect_edges(self, image, low_threshold=50, high_threshold=150):
        """
        Detecta bordes usando el algoritmo Canny.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            low_threshold (int): Umbral inferior para Canny (0-100)
            high_threshold (int): Umbral superior para Canny (0-100)
            
        Returns:
            numpy.ndarray: Imagen con bordes detectados (en escala de grises)
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar Canny
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        
        # Convertir a BGR para mantener el formato (3 canales)
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def rotate(self, image, angle):
        """
        Rota la imagen según el ángulo especificado.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            angle (float): Ángulo de rotación en grados (-180 a 180)
            
        Returns:
            numpy.ndarray: Imagen rotada
        """
        if angle == 0:
            return image.copy()
        
        # Obtener dimensiones
        height, width = image.shape[:2]
        
        # Calcular centro de la imagen
        center = (width // 2, height // 2)
        
        # Obtener matriz de rotación
        rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)  # Negativo porque OpenCV rota en sentido antihorario
        
        # Calcular nuevo tamaño para que la imagen completa quepa
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Ajustar matriz de rotación para centrar
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # Aplicar rotación
        result = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                               borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        
        return result
    
    def resize(self, image, width=None, height=None, keep_aspect=True):
        """
        Redimensiona la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            width (int, optional): Nuevo ancho
            height (int, optional): Nuevo alto
            keep_aspect (bool): Mantener relación de aspecto
            
        Returns:
            numpy.ndarray: Imagen redimensionada
        """
        h, w = image.shape[:2]
        
        if width is None and height is None:
            return image.copy()
        
        if keep_aspect:
            if width is not None:
                ratio = width / w
                new_height = int(h * ratio)
                new_width = width
            else:
                ratio = height / h
                new_width = int(w * ratio)
                new_height = height
        else:
            new_width = width if width is not None else w
            new_height = height if height is not None else h
        
        result = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        return result
    
    def flip_horizontal(self, image):
        """
        Voltea la imagen horizontalmente (efecto espejo izquierda-derecha).
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            
        Returns:
            numpy.ndarray: Imagen volteada horizontalmente
        """
        return cv2.flip(image, 1)

    def flip_vertical(self, image):
        """
        Voltea la imagen verticalmente (efecto espejo arriba-abajo).
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            
        Returns:
            numpy.ndarray: Imagen volteada verticalmente
        """
        return cv2.flip(image, 0)