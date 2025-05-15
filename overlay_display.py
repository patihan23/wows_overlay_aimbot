import sys
import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

class TransparentOverlay(QMainWindow):
    def __init__(self, screen_width=1920, screen_height=1080):
        """
        Initialize the transparent overlay window.
        
        Args:
            screen_width (int): Screen width
            screen_height (int): Screen height
        """
        super().__init__()
        
        # Store screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize overlay data
        self.target_data = None
        self.aim_point = None
        self.detected_ships = []
        self.lead_line = None
        self.display_info = {}
        
        # Setup window properties
        self.setWindowTitle("WoWS Overlay")
        self.setGeometry(0, 0, screen_width, screen_height)
        
        # Make the window transparent and frameless
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        
        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Set up a timer for periodic updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_overlay)
        self.update_timer.start(16)  # ~60 FPS
        
        # Create visual elements
        self.crosshair_size = 20
        self.crosshair_color = QColor(255, 0, 0, 200)
        self.aim_point_color = QColor(0, 255, 0, 200)
        self.lead_line_color = QColor(0, 255, 255, 150)
        self.ship_box_color = QColor(255, 255, 0, 150)
        self.text_color = QColor(255, 255, 255, 220)
        
        # Initialize toggle state
        self.show_info = True
        self.show_aim = True
        self.show_boxes = True
    
    def update_overlay(self):
        """
        Update the overlay - called by timer.
        """
        self.update()
    
    def set_target_data(self, target_data):
        """
        Set current target data.
        
        Args:
            target_data (dict): Dictionary with target information
        """
        self.target_data = target_data
        self.update()
    
    def set_aim_point(self, aim_point):
        """
        Set the calculated aim point.
        
        Args:
            aim_point (tuple): (x, y) coordinates for aim point
        """
        self.aim_point = aim_point
        self.update()
    
    def set_detected_ships(self, ships):
        """
        Set the list of detected ships.
        
        Args:
            ships (list): List of dictionaries with ship detection data
        """
        self.detected_ships = ships
        self.update()
    
    def set_lead_line(self, start_point, end_point):
        """
        Set the lead line from target to aim point.
        
        Args:
            start_point (tuple): (x, y) coordinates of line start (target)
            end_point (tuple): (x, y) coordinates of line end (aim point)
        """
        self.lead_line = (start_point, end_point)
        self.update()
    
    def set_display_info(self, info):
        """
        Set additional display information.
        
        Args:
            info (dict): Dictionary with display information
        """
        self.display_info = info
        self.update()
    
    def toggle_info_display(self):
        """Toggle the display of information overlay."""
        self.show_info = not self.show_info
        self.update()
    
    def toggle_aim_display(self):
        """Toggle the display of aim elements."""
        self.show_aim = not self.show_aim
        self.update()
    
    def toggle_boxes_display(self):
        """Toggle the display of detection boxes."""
        self.show_boxes = not self.show_boxes
        self.update()
    
    def paintEvent(self, event):
        """
        Paint event for rendering the overlay.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        
        # Enable antialiasing
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw crosshair at screen center
        if self.show_aim:
            self.draw_crosshair(painter, self.screen_width//2, self.screen_height//2, 
                               self.crosshair_size, self.crosshair_color)
        
        # Draw aim point if available
        if self.show_aim and self.aim_point:
            self.draw_crosshair(painter, self.aim_point[0], self.aim_point[1], 
                               self.crosshair_size, self.aim_point_color)
            
            # Draw lead line if available
            if self.lead_line:
                painter.setPen(QPen(self.lead_line_color, 2, Qt.DashLine))
                painter.drawLine(self.lead_line[0][0], self.lead_line[0][1], 
                                self.lead_line[1][0], self.lead_line[1][1])
        
        # Draw detected ship boxes
        if self.show_boxes and self.detected_ships:
            for ship in self.detected_ships:
                bbox = ship.get('bbox', [0, 0, 0, 0])
                conf = ship.get('confidence', 0)
                
                painter.setPen(QPen(self.ship_box_color, 2))
                painter.drawRect(bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1])
                
                # Draw confidence value
                painter.setFont(QFont("Arial", 10))
                painter.setPen(self.text_color)
                painter.drawText(bbox[0], bbox[1]-5, f"Ship: {conf:.2f}")
        
        # Draw information overlay
        if self.show_info:
            self.draw_info_overlay(painter)
    
    def draw_crosshair(self, painter, x, y, size, color):
        """
        Draw a crosshair at the specified position.
        
        Args:
            painter (QPainter): The painter object
            x (int): X-coordinate
            y (int): Y-coordinate
            size (int): Size of the crosshair
            color (QColor): Color of the crosshair
        """
        painter.setPen(QPen(color, 2))
        
        # Draw horizontal line
        painter.drawLine(x - size, y, x + size, y)
        
        # Draw vertical line
        painter.drawLine(x, y - size, x, y + size)
        
        # Draw circle
        painter.drawEllipse(x - size//2, y - size//2, size, size)
    
    def draw_info_overlay(self, painter):
        """
        Draw the information overlay.
        
        Args:
            painter (QPainter): The painter object
        """
        # Set font and color
        painter.setFont(QFont("Arial", 12))
        painter.setPen(self.text_color)
        
        # Background for text
        bg_color = QColor(0, 0, 0, 120)
        painter.setBrush(bg_color)
        
        # Draw target information if available
        if self.target_data:
            # Create text lines
            lines = []
            if 'ship_info' in self.target_data:
                ship_info = self.target_data['ship_info']
                if 'name' in ship_info:
                    lines.append(f"Target: {ship_info.get('name', 'Unknown')}")
                if 'type' in ship_info:
                    lines.append(f"Type: {ship_info.get('type', 'Unknown')}")
            
            if 'distance' in self.target_data:
                lines.append(f"Distance: {self.target_data['distance']:.1f} km")
            if 'speed' in self.target_data:
                lines.append(f"Speed: {self.target_data['speed']:.1f} knots")
            
            # Draw text box
            if lines:
                text_width = 250
                line_height = 20
                text_height = len(lines) * line_height
                
                # Position in top-right corner
                text_x = self.screen_width - text_width - 20
                text_y = 20
                
                # Draw background
                painter.drawRect(text_x - 5, text_y - 5, 
                                text_width + 10, text_height + 10)
                
                # Draw text
                for i, line in enumerate(lines):
                    painter.drawText(text_x, text_y + i * line_height + 15, line)
        
        # Draw additional information
        if self.display_info:
            lines = []
            for key, value in self.display_info.items():
                lines.append(f"{key}: {value}")
            
            # Draw text box
            if lines:
                text_width = 250
                line_height = 20
                text_height = len(lines) * line_height
                
                # Position in bottom-left corner
                text_x = 20
                text_y = self.screen_height - text_height - 20
                
                # Draw background
                painter.drawRect(text_x - 5, text_y - 5, 
                                text_width + 10, text_height + 10)
                
                # Draw text
                for i, line in enumerate(lines):
                    painter.drawText(text_x, text_y + i * line_height + 15, line)
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event: Key event
        """
        # ESC to exit
        if event.key() == Qt.Key_Escape:
            self.close()
        
        # F1 to toggle info display
        elif event.key() == Qt.Key_F1:
            self.toggle_info_display()
        
        # F2 to toggle aim display
        elif event.key() == Qt.Key_F2:
            self.toggle_aim_display()
        
        # F3 to toggle boxes display
        elif event.key() == Qt.Key_F3:
            self.toggle_boxes_display()

class OverlayManager:
    def __init__(self):
        """
        Initialize the overlay manager.
        """
        # Get screen resolution
        app = QApplication.instance() or QApplication(sys.argv)
        screen_rect = app.desktop().screenGeometry()
        screen_width, screen_height = screen_rect.width(), screen_rect.height()
        
        # Create overlay
        self.overlay = TransparentOverlay(screen_width, screen_height)
    
    def show(self):
        """Show the overlay."""
        self.overlay.show()
    
    def hide(self):
        """Hide the overlay."""
        self.overlay.hide()
    
    def update_target_data(self, target_data):
        """
        Update target data on the overlay.
        
        Args:
            target_data (dict): Target information
        """
        self.overlay.set_target_data(target_data)
    
    def update_aim_point(self, aim_point):
        """
        Update aim point on the overlay.
        
        Args:
            aim_point (tuple): (x, y) coordinates
        """
        self.overlay.set_aim_point(aim_point)
    
    def update_detected_ships(self, ships):
        """
        Update detected ships on the overlay.
        
        Args:
            ships (list): List of ship detections
        """
        self.overlay.set_detected_ships(ships)
    
    def update_lead_line(self, target_point, aim_point):
        """
        Update the lead line on the overlay.
        
        Args:
            target_point (tuple): (x, y) coordinates of target
            aim_point (tuple): (x, y) coordinates of aim point
        """
        self.overlay.set_lead_line(target_point, aim_point)
    
    def update_display_info(self, info):
        """
        Update display information on the overlay.
        
        Args:
            info (dict): Information to display
        """
        self.overlay.set_display_info(info)
    
    def toggle_overlay(self):
        """Toggle the visibility of the overlay."""
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

if __name__ == "__main__":
    # Test the overlay
    app = QApplication(sys.argv)
    
    manager = OverlayManager()
    
    # Show overlay
    manager.show()
    
    # Test with sample data
    target_data = {
        'distance': 8.5,
        'speed': 25,
        'ship_info': {
            'name': 'Shimakaze',
            'type': 'Destroyer'
        }
    }
    
    manager.update_target_data(target_data)
    
    # Sample aim point (center of screen)
    screen_rect = app.desktop().screenGeometry()
    screen_center = (screen_rect.width()//2, screen_rect.height()//2)
    aim_point = (screen_center[0] + 100, screen_center[1] - 50)
    
    manager.update_aim_point(aim_point)
    manager.update_lead_line(screen_center, aim_point)
    
    # Sample detected ships
    ships = [
        {
            'bbox': [500, 300, 700, 400],
            'confidence': 0.85
        },
        {
            'bbox': [900, 500, 1100, 600],
            'confidence': 0.77
        }
    ]
    
    manager.update_detected_ships(ships)
    
    # Sample display info
    info = {
        'FPS': 60,
        'Mode': 'Auto-Aim',
        'Status': 'Active'
    }
    
    manager.update_display_info(info)
    
    sys.exit(app.exec_())
