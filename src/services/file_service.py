"""
src/services/file_service.py
Servicio para manejar la carga y guardado de imágenes.
"""

import cv2
import numpy as np
from PIL import Image
import os


class FileService:
    """Servicio para operaciones de entrada/salida de imágenes"""
    
    @staticmethod
    def load_image(filepath):
        """
        Carga una imagen desde el sistema de archivos.
        
        Args:
            filepath (str): Ruta de la imagen
            
        Returns:
            numpy.ndarray: Imagen en formato BGR (OpenCV)
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato no es soportado
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
        
        # Cargar imagen con OpenCV
        image = cv2.imread(filepath)
        
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen. Formato no soportado: {filepath}")
        
        return image
    
    @staticmethod
    def save_image(image, filepath):
        """
        Guarda una imagen en el sistema de archivos.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR (OpenCV)
            filepath (str): Ruta donde guardar la imagen
            
        Returns:
            bool: True si se guardó correctamente
        """
        # Crear directorio si no existe
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Guardar imagen
        success = cv2.imwrite(filepath, image)
        
        if not success:
            raise IOError(f"No se pudo guardar la imagen en: {filepath}")
        
        return True
    
    @staticmethod
    def get_image_info(image):
        """
        Obtiene información de la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR
            
        Returns:
            dict: Diccionario con información (alto, ancho, canales, dtype)
        """
        if image is None:
            return {}
        
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'dtype': str(image.dtype),
            'size': image.size
        }