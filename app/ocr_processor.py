import easyocr
import cv2
import numpy as np
import base64
import random

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (0, 128, 128),  # Teal
            (255, 192, 203) # Pink
        ]
        
    def find_text_position(self, points, text, existing_boxes, image_shape):
        """Find a suitable position for text that doesn't overlap with existing boxes"""
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_height = text_size[1] + 8  # Add padding
        text_width = text_size[0]
        
        # Try positions in this order: above, below, right, left
        x, y = points[0][0], points[0][1]  # Top-left point of bbox
        
        # Potential positions
        positions = [
            (x, y - text_height - 5),  # Above
            (x, y + text_height + 5),  # Below
            (x + points[2][0] - points[0][0] + 5, y),  # Right
            (x - text_width - 5, y)   # Left
        ]
        
        for pos_x, pos_y in positions:
            # Check if position is within image bounds
            if (pos_x >= 0 and pos_x + text_width < image_shape[1] and 
                pos_y >= text_height and pos_y < image_shape[0]):
                
                # Create text box
                text_box = np.array([
                    [pos_x, pos_y - text_height],
                    [pos_x + text_width, pos_y - text_height],
                    [pos_x + text_width, pos_y],
                    [pos_x, pos_y]
                ])
                
                # Check intersection with existing boxes
                overlap = False
                for existing_box in existing_boxes:
                    if self.check_intersection(text_box, existing_box):
                        overlap = True
                        break
                
                if not overlap:
                    existing_boxes.append(text_box)
                    return (int(pos_x), int(pos_y)), existing_boxes
        
        # If no good position found, return original position
        return (int(x), int(y - text_height)), existing_boxes
    
    def check_intersection(self, box1, box2):
        """Check if two boxes intersect"""
        x1 = max(min(box1[:, 0]), min(box2[:, 0]))
        y1 = max(min(box1[:, 1]), min(box2[:, 1]))
        x2 = min(max(box1[:, 0]), max(box2[:, 0]))
        y2 = min(max(box1[:, 1]), max(box2[:, 1]))
        return x1 < x2 and y1 < y2
        
    def process_image(self, image):
        original_image = image.copy()
        results = self.reader.readtext(image)
        annotated_image = image.copy()
        text_results = []
        existing_boxes = []  # Keep track of existing text boxes
        
        # Sort results by y-coordinate to process from top to bottom
        results.sort(key=lambda x: x[0][0][1])
        
        for idx, (bbox, text, prob) in enumerate(results):
            if prob > 0.5:
                color = self.colors[idx % len(self.colors)]
                points = np.array(bbox).astype(np.int32)
                
                # Draw bounding box
                cv2.polylines(annotated_image, [points], True, color, 1)
                
                # Find suitable position for text
                text_pos, existing_boxes = self.find_text_position(
                    points, text, existing_boxes, annotated_image.shape)
                
                # Add white background to text
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(annotated_image, 
                            (text_pos[0], text_pos[1] - text_size[1] - 4),
                            (text_pos[0] + text_size[0], text_pos[1] + 4),
                            (255, 255, 255),
                            -1)
                
                # Draw text
                cv2.putText(annotated_image, text, 
                          text_pos,
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                bbox_list = [[int(x) for x in point] for point in bbox]
                text_results.append({
                    "text": str(text),
                    "confidence": float(prob),
                    "bbox": bbox_list,
                    "color": color
                })
        
        _, original_buffer = cv2.imencode('.jpg', original_image)
        _, annotated_buffer = cv2.imencode('.jpg', annotated_image)
        
        original_base64 = base64.b64encode(original_buffer).decode('utf-8')
        annotated_base64 = base64.b64encode(annotated_buffer).decode('utf-8')
        
        return {
            "text_data": text_results,
            "original_image": original_base64,
            "annotated_image": annotated_base64
        } 