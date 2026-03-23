# TinyPS - Mini Editor de Imágenes con IA

**TinyPS** es un editor de imágenes liviano construido con Python, OpenCV y Tkinter. Ofrece herramientas esenciales de edición potenciadas con visión por computadora para ajustes de color, filtros, transformaciones geométricas y dibujo de figuras con detección de contornos.

---

## Características Actuales

### Ajustes de Color
- Control deslizante para canales **R (Red)**, **G (Green)** y **B (Blue)**
- Ajuste en tiempo real con rango de 0 a 255 por canal

###  Filtros
- **Desenfoque Gaussiano**: Control deslizante con radio de 0 a 20 píxeles

###  Transformaciones Geométricas
- **Rotación**: Slider de -180° a 180° con indicador visual en plano cartesiano
- **Volteo Horizontal**: Efecto espejo izquierda-derecha
- **Volteo Vertical**: Efecto espejo arriba-abajo
- **Reset**: Botón para restaurar la imagen original y limpiar todas las modificaciones

###  Dibujo de Figuras con Contornos
- **Cuadrado**: Dibuja un cuadrado con detección de contornos en la posición seleccionada
- **Círculo**: Dibuja un círculo con detección de contornos en la posición seleccionada
- Control de **tamaño en porcentaje** (1% a 100% del lado menor de la imagen)
- Selección de **posición X/Y** mediante sliders o clic en la imagen
- Visualización del **contorno** detectado usando `cv2.findContours`

###  Interacción con la Imagen
- **Carga de imágenes**: Soporta formatos JPG, JPEG, PNG, BMP, TIFF
- **Canvas con scrollbars**: Navegación para imágenes grandes
- **Coordenadas interactivas**: Mueve el mouse para actualizar posición X/Y
- **Información de píxel**: Muestra valores RGB en las coordenadas actuales

---

