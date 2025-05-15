import math
import json
import numpy as np

class AimCalculator:
    def __init__(self, ship_data_path="ship_data.json"):
        """
        Initialize the aim calculator with ship data.
        
        Args:
            ship_data_path (str): Path to the ship data JSON file
        """
        self.ship_data = self.load_ship_data(ship_data_path)
        
        # Default ballistic parameters (can be tuned)
        self.gravity = 9.8  # m/s²
        self.default_shell_velocity = 800  # m/s
        
    def load_ship_data(self, ship_data_path):
        """
        Load ship data from JSON file.
        
        Args:
            ship_data_path (str): Path to the ship data JSON file
            
        Returns:
            dict: Ship data
        """
        try:
            with open(ship_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading ship data: {e}")
            return {}
    
    def get_ship_params(self, ship_type, ship_name):
        """
        Get parameters for a specific ship.
        
        Args:
            ship_type (str): Type of ship (destroyer, cruiser, etc.)
            ship_name (str): Name of the ship
            
        Returns:
            dict: Ship parameters
        """
        ship_type = ship_type.lower() if ship_type else "unknown"
        ship_name = ship_name.lower() if ship_name else "unknown"
        
        # Try to find the ship in the data
        type_data = self.ship_data.get(f"{ship_type}s", {})
        ship_params = type_data.get(ship_name, {})
        
        # Use defaults if not found
        if not ship_params:
            # Default values based on ship type
            if ship_type == "destroyer":
                return {"max_speed": 35.0, "acceleration": 2.0, "shell_velocity": 800}
            elif ship_type == "cruiser":
                return {"max_speed": 32.0, "acceleration": 1.8, "shell_velocity": 850}
            elif ship_type == "battleship":
                return {"max_speed": 28.0, "acceleration": 1.3, "shell_velocity": 800}
            else:
                return {"max_speed": 30.0, "acceleration": 1.5, "shell_velocity": 800}
        
        return ship_params
    
    def calculate_time_of_flight(self, distance_km, shell_velocity):
        """
        Calculate the approximate time of flight for a shell.
        
        Args:
            distance_km (float): Distance to target in kilometers
            shell_velocity (float): Shell velocity in m/s
            
        Returns:
            float: Time of flight in seconds
        """
        distance_m = distance_km * 1000
        
        # Simple ballistic model (can be improved with more accurate physics)
        # t = d / v + (g * d^2) / (2 * v^2)
        time = (distance_m / shell_velocity) + \
               (self.gravity * distance_m**2) / (2 * shell_velocity**2)
        
        return time
    
    def calculate_lead_distance(self, target_data):
        """
        Calculate the lead distance for moving targets.
        
        Args:
            target_data (dict): Dictionary containing target information
                - distance (float): Distance to target in km
                - speed (float): Target speed in knots
                - angle (float): Target angle in degrees (0 = coming straight, 90 = perpendicular)
                - ship_type (str): Type of target ship
                - ship_name (str): Name of target ship
            
        Returns:
            tuple: (lead_distance_pixels, aim_point_offset_x, aim_point_offset_y)
        """
        # Extract target data
        distance_km = target_data.get('distance', 10)
        speed_knots = target_data.get('speed', 0)
        angle_degrees = target_data.get('angle', 90)
        ship_type = target_data.get('ship_type', 'cruiser')
        ship_name = target_data.get('ship_name', 'unknown')
        
        # Get ship parameters
        ship_params = self.get_ship_params(ship_type, ship_name)
        shell_velocity = ship_params.get('shell_velocity', self.default_shell_velocity)
        
        # Convert speed from knots to m/s
        speed_ms = speed_knots * 0.5144
        
        # Convert angle to radians
        angle_rad = math.radians(angle_degrees)
        
        # Calculate effective speed (perpendicular component)
        effective_speed = speed_ms * math.sin(angle_rad)
        
        # Calculate time of flight
        tof = self.calculate_time_of_flight(distance_km, shell_velocity)
        
        # Calculate lead distance in meters
        lead_distance_m = effective_speed * tof
        
        # Convert to pixels (approximate, based on game UI)
        # This conversion factor would need to be calibrated for specific game settings
        # Assuming 1km at 10km distance is about 100 pixels on screen
        pixels_per_km_at_10km = 100
        pixels_per_km = pixels_per_km_at_10km * (10 / distance_km)
        lead_distance_pixels = lead_distance_m / 1000 * pixels_per_km
        
        # Calculate x and y components
        aim_point_offset_x = lead_distance_pixels * math.sin(angle_rad)
        aim_point_offset_y = -lead_distance_pixels * math.cos(angle_rad)  # Negative because screen y increases downward
        
        return (lead_distance_pixels, aim_point_offset_x, aim_point_offset_y)
    
    def calculate_aim_point(self, target_center, target_data, screen_size=(1920, 1080)):
        """
        Calculate the final aim point.
        
        Args:
            target_center (tuple): (x, y) coordinates of target center
            target_data (dict): Dictionary containing target information
            screen_size (tuple): Screen resolution (width, height)
            
        Returns:
            tuple: (aim_x, aim_y)
        """
        # Calculate lead distance
        _, offset_x, offset_y = self.calculate_lead_distance(target_data)
        
        # Apply offset to target center
        aim_x = target_center[0] + int(offset_x)
        aim_y = target_center[1] + int(offset_y)
        
        # Ensure aim point is within screen bounds
        aim_x = max(0, min(aim_x, screen_size[0]))
        aim_y = max(0, min(aim_y, screen_size[1]))
        
        return (aim_x, aim_y)
    
    def calculate_shell_drop(self, distance_km, shell_velocity):
        """
        Calculate approximate shell drop compensation.
        
        Args:
            distance_km (float): Distance to target in kilometers
            shell_velocity (float): Shell velocity in m/s
            
        Returns:
            float: Vertical aim offset in pixels
        """
        # Simple model based on time of flight
        tof = self.calculate_time_of_flight(distance_km, shell_velocity)
        
        # Calculate vertical drop in meters
        drop_m = 0.5 * self.gravity * tof**2
        
        # Convert to pixels (approximate)
        # Assuming 100m at 10km distance is about 10 pixels on screen
        pixels_per_100m_at_10km = 10
        pixels_per_100m = pixels_per_100m_at_10km * (10 / distance_km)
        drop_pixels = drop_m / 100 * pixels_per_100m
        
        return drop_pixels

if __name__ == "__main__":
    # Test the aim calculator
    calculator = AimCalculator()
    
    # Sample target data
    target_data = {
        'distance': 8.5,       # km
        'speed': 25,           # knots
        'angle': 45,           # degrees
        'ship_type': 'destroyer',
        'ship_name': 'shimakaze'
    }
    
    # Calculate lead
    lead, offset_x, offset_y = calculator.calculate_lead_distance(target_data)
    print(f"Lead distance: {lead:.2f} pixels")
    print(f"Offset X: {offset_x:.2f}, Y: {offset_y:.2f}")
    
    # Calculate aim point for a target at screen center
    screen_center = (1920//2, 1080//2)
    aim_point = calculator.calculate_aim_point(screen_center, target_data)
    print(f"Aim point: {aim_point}")
