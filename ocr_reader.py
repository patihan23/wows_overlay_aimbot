import cv2
import numpy as np
import pytesseract
import re
import os

# Set path to tesseract executable (update this path for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRReader:
    def __init__(self):
        """
        Initialize the OCR reader for extracting text from game images.
        """
        self.distance_pattern = re.compile(r'(\d+\.?\d*)\s*km')
        self.speed_pattern = re.compile(r'(\d+\.?\d*)\s*kn')
        
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image (numpy.ndarray): The input image
        
        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return opening
    
    def extract_text(self, image):
        """
        Extract all text from an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            str: Extracted text
        """
        preprocessed = self.preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed, config='--psm 6')
        return text
    
    def extract_target_info(self, target_info_image):
        """
        Extract target information (distance, speed, etc.) from the target info area.
        
        Args:
            target_info_image (numpy.ndarray): Image of the target info area
            
        Returns:
            dict: Dictionary containing extracted target information
        """
        text = self.extract_text(target_info_image)
        
        # Extract distance
        distance_match = self.distance_pattern.search(text)
        distance = float(distance_match.group(1)) if distance_match else None
        
        # Extract speed
        speed_match = self.speed_pattern.search(text)
        speed = float(speed_match.group(1)) if speed_match else None
        
        # Extract ship type and name (based on common patterns in WoWS UI)
        ship_info = {}
        lines = text.split('\n')
        for line in lines:
            if any(ship_type in line.lower() for ship_type in 
                   ["destroyer", "cruiser", "battleship", "carrier"]):
                ship_info["type"] = next((t for t in ["destroyer", "cruiser", "battleship", "carrier"] 
                                           if t in line.lower()), None)
                # Try to extract name based on common patterns
                ship_info["name"] = line.strip()
        
        return {
            "distance": distance,
            "speed": speed,
            "ship_info": ship_info
        }
    
    def extract_minimap_coordinates(self, minimap_image):
        """
        Extract coordinates from the minimap.
        
        Args:
            minimap_image (numpy.ndarray): Image of the minimap
            
        Returns:
            tuple: (x, y) coordinates or None if not found
        """
        # Extract the area where coordinates are typically shown
        height, width = minimap_image.shape[:2]
        coord_area = minimap_image[height-30:height, 0:100]
        
        text = self.extract_text(coord_area)
        
        # Look for coordinate patterns like "A7" or "D10"
        coord_pattern = re.compile(r'([A-J])\s*(\d{1,2})')
        match = coord_pattern.search(text)
        
        if match:
            letter, number = match.groups()
            return (letter, int(number))
        
        return None

if __name__ == "__main__":
    # Test OCR on sample image if available
    ocr = OCRReader()
    
    # You can test with a sample image if you have one
    print("OCR module initialized. Use with capture_screen.py to extract game information.")
