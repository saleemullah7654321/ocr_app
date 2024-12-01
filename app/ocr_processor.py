import easyocr
import cv2
import numpy as np
import base64

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        
    def process_image(self, image):
        # Perform OCR
        results = self.reader.readtext(image)
        
        # Draw bounding boxes and text
        annotated_image = image.copy()
        text_results = []
        
        for (bbox, text, prob) in results:
            if prob > 0.5:  # Confidence threshold
                # Convert bbox to numpy array if it isn't already
                points = np.array(bbox).astype(np.int32)
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
        
        # Convert the annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "text_data": text_results,
            "image_data": image_base64
        } 