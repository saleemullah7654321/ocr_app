import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.blur_threshold = 50  # Reduced blur threshold

    def process_image(self, image):
        # Resize image if it's too large
        max_dimension = 1000
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, None, fx=scale, fy=scale)

        # Basic image enhancement
        image = self._enhance_image(image)
        return image
    
    def _enhance_image(self, image):
        # Apply some basic image enhancements to improve OCR
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        # Denoise
        enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        return enhanced