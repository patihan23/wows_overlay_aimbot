# World of Warships Overlay Aimbot

This project creates an overlay aimbot for World of Warships that assists with aiming by calculating lead distances and displaying visual aids.

## Disclaimer

This project is for **educational purposes only**. Using aimbots in online games:
- May violate the game's terms of service
- Could result in a ban of your account
- Is considered cheating by most game communities

I do not recommend using this in actual gameplay. This is a technical demonstration of computer vision and game overlay techniques.

## Features

- Transparent overlay that stays on top of the game
- Ship detection using YOLO
- OCR text recognition to extract target information
- Aim point calculation based on ship movement and distance
- Auto-aim capability (movable with hotkey)
- Visual aids including lead lines and information display

## Requirements

- Windows
- Python 3.7+
- World of Warships game
- Tesseract OCR installed (required for OCR functionality)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Tesseract OCR:
   - Download from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to the default location (`C:\Program Files\Tesseract-OCR\`)
   - If installed to a different location, update the path in `ocr_reader.py`

3. Create or obtain a trained YOLO model:
   - The placeholder file in `assets/yolo_model.pt` needs to be replaced with a real model
   - Train your own using YOLOv5 and ship screenshots from the game
   - Place the trained model file in the `assets` folder

## Usage

1. Start the World of Warships game
2. Run the aimbot:
   ```
   python main.py
   ```
3. Use the following hotkeys:
   - `F8`: Toggle overlay visibility
   - `F9`: Toggle auto-aim functionality
   - `F12`: Exit the application
   - `F1`: Toggle information display
   - `F2`: Toggle aim display
   - `F3`: Toggle detection boxes display

## Components

- `main.py`: Main application logic
- `capture_screen.py`: Screen capture functionality
- `ocr_reader.py`: Text recognition from game UI
- `aim_calculator.py`: Calculations for aim points
- `overlay_display.py`: Transparent overlay UI
- `yolo_detector.py`: Ship detection using YOLO
- `ship_data.json`: Ship parameters

## Customization

You can customize various parameters in the code to match your setup:
- Update screen capture regions in `capture_screen.py` for your resolution
- Adjust ship parameters in `ship_data.json`
- Modify the overlay appearance in `overlay_display.py`

## Notes

- You will need a trained YOLO model for ship detection
- The OCR accuracy depends on game UI, resolution, and text clarity
- Auto-aim is implemented as mouse movement to calculated coordinates

## License

This project is for educational purposes only.
