import sys
import time
import numpy as np
import cv2
import win32api
import win32con
import keyboard
from PyQt5.QtWidgets import QApplication

from capture_screen import ScreenCapture
from ocr_reader import OCRReader
from aim_calculator import AimCalculator
from overlay_display import OverlayManager
from yolo_detector import YOLODetector

class WoWSAimbot:
    def __init__(self):
        """
        Initialize the World of Warships aimbot.
        """
        print("Initializing WoWS Aimbot...")
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.ocr = OCRReader()
        self.aim_calculator = AimCalculator()
        self.detector = YOLODetector()
        
        # Get screen resolution
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # Initialize overlay
        self.overlay_manager = OverlayManager()
        
        # Initialize state variables
        self.running = False
        self.auto_aim = False
        self.target_data = None
        self.detected_ships = []
        self.aim_point = None
        self.target_center = None
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0
        
        # Configure hotkeys
        self.setup_hotkeys()
        
        print(f"Initialized with screen resolution: {self.screen_width}x{self.screen_height}")
    
    def setup_hotkeys(self):
        """
        Set up keyboard hotkeys.
        """
        # Toggle overlay (F8)
        keyboard.add_hotkey('f8', self.toggle_overlay)
        
        # Toggle auto-aim (F9)
        keyboard.add_hotkey('f9', self.toggle_auto_aim)
        
        # Exit application (F12)
        keyboard.add_hotkey('f12', self.exit_application)
        
        print("Hotkeys configured:")
        print("F8 - Toggle overlay")
        print("F9 - Toggle auto-aim")
        print("F12 - Exit application")
        print("F1/F2/F3 - Toggle info/aim/boxes display")
    
    def toggle_overlay(self):
        """Toggle the overlay display."""
        self.overlay_manager.toggle_overlay()
        print("Overlay toggled")
    
    def toggle_auto_aim(self):
        """Toggle auto-aim functionality."""
        self.auto_aim = not self.auto_aim
        print(f"Auto-aim {'enabled' if self.auto_aim else 'disabled'}")
        
        # Update display info
        self.update_display_info()
    
    def exit_application(self):
        """Exit the application."""
        print("Exiting application...")
        self.running = False
        # Allow some time for cleanup
        time.sleep(0.5)
        sys.exit(0)
    
    def update_display_info(self):
        """Update information displayed on the overlay."""
        info = {
            'FPS': f"{self.fps:.1f}",
            'Mode': 'Auto-Aim' if self.auto_aim else 'Manual',
            'Status': 'Active' if self.running else 'Inactive'
        }
        
        if self.target_data:
            if 'distance' in self.target_data:
                info['Distance'] = f"{self.target_data['distance']:.1f} km"
            if 'speed' in self.target_data:
                info['Speed'] = f"{self.target_data['speed']:.1f} knots"
        
        self.overlay_manager.update_display_info(info)
    
    def calculate_fps(self):
        """Calculate and update FPS."""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_time = current_time
    
    def move_mouse_to_aim_point(self):
        """Move the mouse to the calculated aim point."""
        if not self.auto_aim or not self.aim_point:
            return
        
        # Move mouse smoothly to aim point
        current_x, current_y = win32api.GetCursorPos()
        target_x, target_y = self.aim_point
        
        # Calculate distance and direction
        dx = target_x - current_x
        dy = target_y - current_y
        distance = (dx**2 + dy**2)**0.5
        
        # Only move if the distance is significant but not too large
        if 5 < distance < 200:
            # Move in small increments for smooth motion
            steps = max(1, int(distance / 10))
            for i in range(1, steps + 1):
                step_x = current_x + dx * i / steps
                step_y = current_y + dy * i / steps
                win32api.SetCursorPos((int(step_x), int(step_y)))
                time.sleep(0.01)  # Small delay between steps
    
    def process_frame(self):
        """
        Process a single frame: capture screen, detect ships, calculate aim.
        """
        # Capture aim area (around crosshair)
        aim_area = self.screen_capture.capture_aim_area()
        
        # Detect ships in the aim area
        self.detected_ships = self.detector.detect_ships(aim_area, conf_threshold=0.4)
        
        # Update overlay with detected ships
        # Need to adjust coordinates since aim_area is not full screen
        screen_width = self.screen_capture.monitor['width']
        screen_height = self.screen_capture.monitor['height']
        center_x = screen_width // 2
        center_y = screen_height // 2
        capture_size = int(screen_height * 0.4)
        x_offset = center_x - capture_size // 2
        y_offset = center_y - capture_size // 2
        
        adjusted_ships = []
        for ship in self.detected_ships:
            adjusted_ship = ship.copy()
            bbox = ship['bbox']
            adjusted_bbox = [
                bbox[0] + x_offset, 
                bbox[1] + y_offset,
                bbox[2] + x_offset, 
                bbox[3] + y_offset
            ]
            adjusted_ship['bbox'] = adjusted_bbox
            adjusted_ships.append(adjusted_ship)
        
        self.overlay_manager.update_detected_ships(adjusted_ships)
        
        # Find the ship closest to the center of the screen
        if adjusted_ships:
            closest_ship = None
            min_distance = float('inf')
            
            for ship in adjusted_ships:
                bbox = ship['bbox']
                ship_center_x = (bbox[0] + bbox[2]) // 2
                ship_center_y = (bbox[1] + bbox[3]) // 2
                
                # Calculate distance to screen center
                distance = ((ship_center_x - center_x)**2 + 
                            (ship_center_y - center_y)**2)**0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_ship = ship
                    self.target_center = (ship_center_x, ship_center_y)
            
            # Capture target info area
            target_info_area = self.screen_capture.capture_target_info_area()
            
            # Extract target information using OCR
            ocr_info = self.ocr.extract_target_info(target_info_area)
            
            # Create target data dictionary
            self.target_data = ocr_info
            
            # Add estimated angle based on ship position
            if self.target_center:
                dx = self.target_center[0] - center_x
                dy = self.target_center[1] - center_y
                angle = np.degrees(np.arctan2(dx, dy))
                self.target_data['angle'] = angle
                
                # Get ship type from OCR or use default
                ship_type = (self.target_data.get('ship_info', {})
                            .get('type', 'cruiser'))
                ship_name = (self.target_data.get('ship_info', {})
                            .get('name', 'unknown'))
                
                # Calculate aim point
                self.aim_point = self.aim_calculator.calculate_aim_point(
                    self.target_center, 
                    self.target_data
                )
                
                # Update overlay with target data and aim point
                self.overlay_manager.update_target_data(self.target_data)
                self.overlay_manager.update_aim_point(self.aim_point)
                self.overlay_manager.update_lead_line(
                    self.target_center, 
                    self.aim_point
                )
                
                # Move mouse to aim point if auto-aim is enabled
                self.move_mouse_to_aim_point()
        else:
            # No ships detected
            self.target_data = None
            self.aim_point = None
            self.target_center = None
            self.overlay_manager.update_target_data(None)
            self.overlay_manager.update_aim_point(None)
            self.overlay_manager.update_lead_line(None, None)
        
        # Update FPS counter
        self.calculate_fps()
        
        # Update display information
        self.update_display_info()
    
    def run(self):
        """
        Main loop for the aimbot.
        """
        print("Starting aimbot...")
        self.running = True
        self.overlay_manager.show()
        
        try:
            while self.running:
                self.process_frame()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
                # Check for keypress to exit
                if keyboard.is_pressed('f12'):
                    break
        
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        finally:
            print("Aimbot stopped")
            self.overlay_manager.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    aimbot = WoWSAimbot()
    aimbot.run()
    
    sys.exit(app.exec_())
