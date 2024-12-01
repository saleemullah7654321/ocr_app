import easyocr
import cv2
import numpy as np
import base64

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        
    def process_image(self, image):
        # Store original image
        original_image = image.copy()
        
        # Perform OCR
        results = self.reader.readtext(image)
        
        # Draw bounding boxes and text
        annotated_image = image.copy()
        text_results = []
        
        for (bbox, text, prob) in results:
            if prob > 0.5:  # Confidence threshold
                # Convert bbox to numpy array if it isn't already
                points = np.array(bbox).astype(np.int32)
                
                # Draw bounding box
                cv2.polylines(annotated_image, [points], True, (0, 255, 0), 2)
                
                # Add text above bounding box
                cv2.putText(annotated_image, text, 
                          (int(points[0][0]), int(points[0][1] - 10)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                          
                # Convert bbox coordinates to regular Python lists with integer values
                bbox_list = [[int(x) for x in point] for point in bbox]
                
                text_results.append({
                    "text": str(text),
                    "confidence": float(prob),
                    "bbox": bbox_list
                })
        
        # Convert both images to base64
        _, original_buffer = cv2.imencode('.jpg', original_image)
        _, annotated_buffer = cv2.imencode('.jpg', annotated_image)
        
        original_base64 = base64.b64encode(original_buffer).decode('utf-8')
        annotated_base64 = base64.b64encode(annotated_buffer).decode('utf-8')
        
        return {
            "text_data": text_results,
            "original_image": original_base64,
            "annotated_image": annotated_base64
        } 