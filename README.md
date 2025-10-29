# Rickroll Application

A playful prank application that creates animated popups and changes the desktop wallpaper, accompanied by music playback.

## Features

- **Animated Popups**: Randomly generates animated windows with GIFs or rotating images
- **Text Popups**: Displays lyrics from the classic song at random intervals
- **Wallpaper Management**: Automatically sets a custom desktop background
- **Music Playback**: Plays songs with a special "disco mode" effect
- **Smooth Animations**: Popups glide across the screen with randomized movement patterns

## Requirements

- Python 3.7+
- Windows OS (for wallpaper management functionality)
- Required Python packages:
  - `pygame`
  - `Pillow` (PIL)
  - `tkinter` (usually included with Python)

## Installation

1. Clone or download this repository

2. Install the required dependencies:
```bash
pip install pygame Pillow
```

3. Ensure you have the following assets folder structure:
```
project_root/
├── rickroll.py
└── assets/
    ├── head.png
    ├── background.jpg
    ├── rickroll.mp3
    ├── rickroll2.mp3
    ├── rickroll1.gif
    ├── rickroll2.gif
    └── rickroll3.gif
```

## Usage

Simply run the main script:

```bash
python rickroll.py
```

**Warning**: This application will:
- Change your desktop wallpaper
- Create multiple popup windows
- Play music automatically
- Enter fullscreen "disco mode" during the second song

## Configuration

You can customize the application behavior by modifying the `Config` class:

```python
class Config:
    POPUP_SIZE_RANGE = (115, 135)      # Size range for popups
    POPUP_LIFETIME_MS = 5000           # How long popups stay visible
    HEAD_PROBABILITY = 0.15            # Chance of rotating head vs GIF
    TEXT_POPUP_PROBABILITY = 0.1       # Chance of text popup vs animated
```

## Architecture

The application is organized into several key components:

- **AssetManager**: Handles preloading and caching of GIFs and images
- **SoundManager**: Manages music playback and disco mode effects
- **WallpaperManager**: Changes the Windows desktop wallpaper
- **PopupFactory**: Creates different types of animated and text popups
- **RickrollApp**: Main application controller

## Technical Details

### Popup System
- Popups are created using `tkinter.Toplevel` windows
- Animations run at 50ms intervals for smooth playback
- Movement uses interpolated gliding between random positions
- Transparent backgrounds using `transparentcolor` attribute

### Performance
- GIFs are preloaded into memory on startup
- Resized frames are cached to avoid redundant processing
- Threaded music playback prevents UI blocking

### Disco Mode
- Activates during the second song
- Changes background color every 200ms
- Uses fullscreen semi-transparent overlay

## Limitations

- Windows-only wallpaper management (uses PowerShell and Windows registry)
- Requires Windows user32.dll for SystemParametersInfo
- Assets must be present in the `assets/` directory

## Disclaimer

This application is intended for harmless pranks among friends. Please use responsibly and ensure you have permission before running it on someone else's computer.

## License

This project is provided as-is for educational and entertainment purposes.
