import numpy as np
import cv2
import mss
import time

class ScreenCapture:
    def __init__(self, monitor_number=0):
        """
        Initialize the screen capture class.
        
        Args:
            monitor_number (int): The monitor number to capture from
        """
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[monitor_number]
        
    def capture_full_screen(self):
        """
        Capture the entire screen.
        
        Returns:
            numpy.ndarray: The captured screen as a BGR image
        """
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def capture_region(self, x, y, width, height):
        """
        Capture a specific region of the screen.
        
        Args:
            x (int): X-coordinate of the top-left corner
            y (int): Y-coordinate of the top-left corner
            width (int): Width of the region
            height (int): Height of the region
            
        Returns:
            numpy.ndarray: The captured region as a BGR image
        """
        region = {
            'left': self.monitor['left'] + x,
            'top': self.monitor['top'] + y,
            'width': width,
            'height': height
        }
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def capture_minimap(self, game_resolution=(1920, 1080)):
        """
        Capture the minimap area based on standard WoWS UI layout.
        
        Args:
            game_resolution (tuple): Resolution of the game (width, height)
            
        Returns:
            numpy.ndarray: The minimap area as a BGR image
        """
        # Assuming minimap is in bottom right corner (adjust as needed)
        minimap_size = int(game_resolution[1] * 0.25)  # Approximate size
        minimap_x = game_resolution[0] - minimap_size - 20
        minimap_y = game_resolution[1] - minimap_size - 20
        
        return self.capture_region(minimap_x, minimap_y, minimap_size, minimap_size)
    
    def capture_target_info_area(self, game_resolution=(1920, 1080)):
        """
        Capture the area where target information is displayed.
        
        Args:
            game_resolution (tuple): Resolution of the game (width, height)
            
        Returns:
            numpy.ndarray: The target info area as a BGR image
        """
        # Assuming target info is in the middle-top of the screen
        width = int(game_resolution[0] * 0.3)
        height = int(game_resolution[1] * 0.1)
        x = (game_resolution[0] - width) // 2
        y = int(game_resolution[1] * 0.05)
        
        return self.capture_region(x, y, width, height)
    
    def capture_aim_area(self):
        """
        Capture the area around the crosshair/aim point.
        
        Returns:
            numpy.ndarray: The aim area as a BGR image
        """
        # Center of the screen
        screen_width = self.monitor['width']
        screen_height = self.monitor['height']
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Capture a square area around the center
        capture_size = int(screen_height * 0.4)
        x = center_x - capture_size // 2
        y = center_y - capture_size // 2
        
        return self.capture_region(x, y, capture_size, capture_size)

if __name__ == "__main__":
    # Test the screen capture
    capture = ScreenCapture()
    
    # Capture full screen
    full_screen = capture.capture_full_screen()
    cv2.imwrite("full_screen.jpg", full_screen)
    
    # Capture aim area
    aim_area = capture.capture_aim_area()
    cv2.imwrite("aim_area.jpg", aim_area)
    
    # Capture minimap
    minimap = capture.capture_minimap()
    cv2.imwrite("minimap.jpg", minimap)
    
    print("Test captures saved as images.")
