import torch
import cv2
import numpy as np
import os

class YOLODetector:
    def __init__(self, model_path="assets/yolo_model.pt"):
        """
        Initialize the YOLO ship detector.
        
        Args:
            model_path (str): Path to the YOLO model file
        """
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model if exists, otherwise set to None and print warning
        if os.path.exists(model_path):
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            self.model.to(self.device)
            print(f"YOLO model loaded from {model_path}")
        else:
            self.model = None
            print(f"WARNING: YOLO model not found at {model_path}. "
                  f"Detection will not work until a valid model is provided.")
    
    def detect_ships(self, image, conf_threshold=0.5):
        """
        Detect ships in the given image.
        
        Args:
            image (numpy.ndarray): Input image (BGR format)
            conf_threshold (float): Confidence threshold for detections
            
        Returns:
            list: List of detections, each with [x1, y1, x2, y2, confidence, class]
        """
        if self.model is None:
            print("No YOLO model loaded. Cannot perform detection.")
            return []
        
        # Run inference
        results = self.model(image)
        
        # Process results
        detections = []
        for pred in results.pred:
            if len(pred) > 0:
                # Convert predictions to numpy array
                pred_cpu = pred.cpu().numpy()
                
                # Filter by confidence
                confident_detections = pred_cpu[pred_cpu[:, 4] >= conf_threshold]
                
                for detection in confident_detections:
                    x1, y1, x2, y2, conf, cls = detection
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(conf),
                        'class': int(cls)
                    })
        
        return detections
    
    def draw_detections(self, image, detections):
        """
        Draw detection boxes on the image.
        
        Args:
            image (numpy.ndarray): Input image
            detections (list): List of detections from detect_ships
            
        Returns:
            numpy.ndarray: Image with drawn detections
        """
        img_copy = image.copy()
        
        colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (0, 255, 255)]  # Different colors for classes
        
        for det in detections:
            bbox = det['bbox']
            conf = det['confidence']
            cls = det['class']
            
            # Get color based on class
            color = colors[cls % len(colors)]
            
            # Draw bounding box
            cv2.rectangle(img_copy, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw class and confidence
            label = f"Ship {cls}: {conf:.2f}"
            cv2.putText(img_copy, label, (bbox[0], bbox[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy
    
    def get_center_of_detection(self, detection):
        """
        Get the center point of a detection.
        
        Args:
            detection (dict): A detection from detect_ships
            
        Returns:
            tuple: (center_x, center_y)
        """
        bbox = detection['bbox']
        center_x = (bbox[0] + bbox[2]) // 2
        center_y = (bbox[1] + bbox[3]) // 2
        return (center_x, center_y)
    
    def get_ship_dimensions(self, detection):
        """
        Get the dimensions of a ship detection.
        
        Args:
            detection (dict): A detection from detect_ships
            
        Returns:
            tuple: (width, height)
        """
        bbox = detection['bbox']
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return (width, height)

if __name__ == "__main__":
    # Test the detector if model is available
    detector = YOLODetector()
    
    if detector.model is not None:
        # Test on a sample image if available
        print("YOLO detector initialized. Use with capture_screen.py to detect ships.")
