"""
src/utils/image_utils.py
Utilidades para conversión y manejo de formatos de imagen.
"""

import cv2
import numpy as np
from PIL import Image


class ImageUtils:
    """Clase con utilidades para conversión entre formatos"""
    
    @staticmethod
    def cv2_to_pil(cv2_image):
        """
        Convierte imagen de OpenCV (BGR) a PIL (RGB).
        
        Args:
            cv2_image (numpy.ndarray): Imagen en formato BGR (OpenCV)
            
        Returns:
            PIL.Image: Imagen en formato PIL (RGB)
        """
        # Convertir BGR a RGB
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        
        # Convertir a PIL
        pil_image = Image.fromarray(rgb_image)
        
        return pil_image
    
    @staticmethod
    def pil_to_cv2(pil_image):
        """
        Convierte imagen de PIL (RGB) a OpenCV (BGR).
        
        Args:
            pil_image (PIL.Image): Imagen en formato PIL (RGB)
            
        Returns:
            numpy.ndarray: Imagen en formato BGR (OpenCV)
        """
        # Convertir PIL a numpy array (RGB)
        rgb_image = np.array(pil_image)
        
        # Convertir RGB a BGR
        cv2_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        return cv2_image
    
    @staticmethod
    def normalize_image(image):
        """
        Normaliza la imagen a valores entre 0 y 255 (uint8).
        
        Args:
            image (numpy.ndarray): Imagen de entrada
            
        Returns:
            numpy.ndarray: Imagen normalizada
        """
        if image.dtype == np.uint8:
            return image
        
        # Normalizar a 0-255
        min_val = np.min(image)
        max_val = np.max(image)
        
        if max_val - min_val > 0:
            normalized = ((image - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(image, dtype=np.uint8)
        
        return normalized
    
    @staticmethod
    def get_image_dimensions(image):
        """
        Obtiene dimensiones de la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            
        Returns:
            tuple: (alto, ancho, canales)
        """
        if image is None:
            return (0, 0, 0)
        
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        return (height, width, channels)
    
    @staticmethod
    def create_blank_image(width, height, color=(0, 0, 0)):
        """
        Crea una imagen en blanco del tamaño y color especificados.
        
        Args:
            width (int): Ancho de la imagen
            height (int): Alto de la imagen
            color (tuple): Color en BGR (B, G, R)
            
        Returns:
            numpy.ndarray: Imagen en blanco
        """
        return np.full((height, width, 3), color, dtype=np.uint8)
    
    @staticmethod
    def is_color_image(image):
        """
        Verifica si la imagen es a color (3 canales).
        
        Args:
            image (numpy.ndarray): Imagen de entrada
            
        Returns:
            bool: True si tiene 3 canales, False si es escala de grises
        """
        return len(image.shape) == 3 and image.shape[2] == 3