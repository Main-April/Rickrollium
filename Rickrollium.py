"""
Rickroll Application
Une application de prank qui affiche des popups animés et change le fond d'écran.
"""

import os
import random
import subprocess
import threading
from pathlib import Path
from typing import List, Tuple

import pygame
import tkinter as tk
import winreg
from PIL import Image, ImageTk, ImageSequence


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration globale de l'application."""
    
    DRIVE_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    TEXT_CONTENT = [
        "Give you up!",
        "Let you down!",
        "Run around and desert you!",
        "Make you cry!",
        "Say goodbye!",
        "Tell a lie and hurt you!"
    ]
    
    POPUP_SIZE_RANGE = (115, 135)
    POPUP_LIFETIME_MS = 5000
    HEAD_PROBABILITY = 0.15
    TEXT_POPUP_PROBABILITY = 0.1


# Chemins des assets (définis en dehors de la classe pour éviter les problèmes de référence)
SCRIPT_DIR = Path(__file__).parent
ASSET_DIR = SCRIPT_DIR / "assets"

HEAD_IMAGE = ASSET_DIR / "head.png"
BACKGROUND_IMAGE = ASSET_DIR / "background.jpg"
SONGS = [
    ASSET_DIR / "rickroll.mp3",
    ASSET_DIR / "rickroll2.mp3"
]
GIFS = [
    ASSET_DIR / f"rickroll{i}.gif" for i in range(1, 4)
]


# ============================================================================
# GESTION DES ASSETS
# ============================================================================

class AssetManager:
    """Gère le préchargement et le cache des assets (GIFs, images)."""
    
    def __init__(self):
        self.gif_cache = {}
    
    def preload_gifs(self) -> None:
        """Précharge tous les GIFs en mémoire."""
        for gif_path in GIFS:
            if gif_path not in self.gif_cache:
                gif = Image.open(gif_path)
                frames = [
                    frame.copy().convert("RGBA") 
                    for frame in ImageSequence.Iterator(gif)
                ]
                self.gif_cache[str(gif_path)] = frames
    
    def get_resized_frames(self, gif_path: Path, size: int) -> List[Image.Image]:
        """Retourne les frames d'un GIF redimensionné (avec cache)."""
        cache_key = (str(gif_path), size)
        
        if cache_key in self.gif_cache:
            return self.gif_cache[cache_key]
        
        original_frames = self.gif_cache[str(gif_path)]
        resized = [
            frame.resize((size, size), Image.LANCZOS) 
            for frame in original_frames
        ]
        self.gif_cache[cache_key] = resized
        return resized
    
    @staticmethod
    def get_random_gif() -> Path:
        """Retourne un chemin de GIF aléatoire."""
        return random.choice(GIFS)


# ============================================================================
# GESTION DU SON
# ============================================================================

class SoundManager:
    """Gère la lecture de la musique et les effets visuels."""
    
    def __init__(self, root: tk.Tk, on_second_song_callback=None):
        self.root = root
        self.on_second_song_callback = on_second_song_callback
        self.mixer = None
    
    def play_songs(self) -> None:
        """Lance la lecture des chansons dans un thread séparé."""
        thread = threading.Thread(target=self._play_songs_thread, daemon=True)
        thread.start()
    
    def _play_songs_thread(self) -> None:
        """Thread de lecture des chansons."""
        self.mixer = pygame.mixer
        self.mixer.init()
        
        for idx, song_path in enumerate(SONGS):
            self.mixer.music.load(str(song_path))
            self.mixer.music.play()
            
            # Active le mode disco pour la deuxième chanson
            if idx == 1:
                if self.on_second_song_callback:
                    self.on_second_song_callback()
                self._start_disco_mode()
            
            # Attend la fin de la chanson
            while self.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    
    def _start_disco_mode(self) -> None:
        """Active le mode disco avec des couleurs aléatoires."""
        def disco():
            if not self.root.winfo_exists():
                return
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            self.root.configure(bg=color)
            self.root.attributes("-fullscreen", True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.5)
            self.root.deiconify()
            self.root.after(200, disco)
        
        disco()


# ============================================================================
# GESTION DU FOND D'ÉCRAN
# ============================================================================

class WallpaperManager:
    """Gère le changement du fond d'écran Windows."""
    
    @staticmethod
    def set_wallpaper(image_path: Path) -> None:
        """Change le fond d'écran Windows."""
        reg_path = r"Control Panel\Desktop"
        
        # Vérifie si le fond d'écran est déjà configuré
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                current_wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
                if Path(current_wallpaper).resolve() == image_path.resolve():
                    return
        except Exception:
            pass
        
        # Change le fond d'écran via PowerShell
        powershell_cmd = (
            "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; "
            "public class Win32 { [DllImport(\"user32.dll\", SetLastError = true)] "
            "public static extern bool SystemParametersInfo(int uAction, int uParam, "
            "string lpvParam, int fuWinIni); }'; "
            f"[Win32]::SystemParametersInfo(20, 0, '{image_path}', 3)"
        )
        
        subprocess.run(["powershell", "-Command", powershell_cmd])


# ============================================================================
# CRÉATION DES POPUPS
# ============================================================================

class PopupFactory:
    """Crée différents types de popups."""
    
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.text_index = 0
    
    def create_animated_popup(self, parent: tk.Tk) -> None:
        """Crée un popup avec une animation (GIF ou tête tournante)."""
        popup = tk.Toplevel(parent)
        popup.overrideredirect(True)
        popup.attributes("-transparentcolor", "white")
        popup.attributes("-topmost", True)
        
        # Position et taille aléatoires
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        x = random.randint(0, screen_w - 200)
        y = random.randint(0, screen_h - 200)
        
        size = random.randint(*Config.POPUP_SIZE_RANGE)
        size = (size // 10) * 10
        
        popup.geometry(f"{size}x{size}+{x}+{y}")
        popup.after(Config.POPUP_LIFETIME_MS, popup.destroy)
        
        label = tk.Label(popup, bg="white")
        label.pack()
        
        # Décide aléatoirement entre tête tournante ou GIF
        if random.random() < Config.HEAD_PROBABILITY:
            self._animate_rotating_head(popup, label, size)
        else:
            self._animate_gif(popup, label, size)
        
        # Ajoute le mouvement aléatoire
        self._add_movement(popup, x, y, screen_w, screen_h)
    
    def _animate_rotating_head(self, popup: tk.Toplevel, label: tk.Label, size: int) -> None:
        """Anime une tête qui tourne."""
        base_image = Image.open(HEAD_IMAGE).convert("RGBA")
        base_image = base_image.resize((size, size), Image.LANCZOS)
        
        def rotate(angle=0):
            if not popup.winfo_exists():
                return
            
            rotated = base_image.rotate(angle, resample=Image.BICUBIC, expand=True)
            w, h = rotated.size
            offset_x = (w - size) // 2
            offset_y = (h - size) // 2
            cropped = rotated.crop((offset_x, offset_y, offset_x + size, offset_y + size))
            
            tk_img = ImageTk.PhotoImage(cropped)
            label.config(image=tk_img)
            label.image = tk_img
            popup.after(50, rotate, (angle + 10) % 360)
        
        rotate()
    
    def _animate_gif(self, popup: tk.Toplevel, label: tk.Label, size: int) -> None:
        """Anime un GIF."""
        gif_path = self.asset_manager.get_random_gif()
        frames_resized = self.asset_manager.get_resized_frames(gif_path, size)
        frames_tk = [ImageTk.PhotoImage(frame) for frame in frames_resized]
        
        def animate(frame_index=0):
            if popup.winfo_exists():
                label.config(image=frames_tk[frame_index])
                label.image = frames_tk[frame_index]
                popup.after(50, animate, (frame_index + 1) % len(frames_tk))
        
        animate()
    
    def _add_movement(self, popup: tk.Toplevel, start_x: int, start_y: int, 
                     screen_w: int, screen_h: int) -> None:
        """Ajoute un mouvement aléatoire au popup."""
        x, y = start_x, start_y
        
        def move():
            nonlocal x, y
            target_x = random.randint(0, screen_w - 300)
            target_y = random.randint(0, screen_h - 300)
            steps = random.randint(50, 100)
            step = 0
            
            def glide():
                nonlocal x, y, step
                if not popup.winfo_exists():
                    return
                
                step += 1
                new_x = x + (target_x - x) * step / steps
                new_y = y + (target_y - y) * step / steps
                popup.geometry(f"+{int(new_x)}+{int(new_y)}")
                
                if step < steps:
                    popup.after(20, glide)
                else:
                    x, y = target_x, target_y
                    popup.after(1000, move)
            
            glide()
        
        move()
    
    def create_text_popup(self, parent: tk.Tk, step: int = 1) -> None:
        """Crée un popup avec du texte."""
        popup = tk.Toplevel(parent)
        popup.title("Never Gonna ...")
        popup.attributes("-topmost", True)
        
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        popup.geometry(f"300x80+{x}+{y}")
        
        text = Config.TEXT_CONTENT[self.text_index]
        if step == 2:
            text = " GIVE YOU UP !!! "
        
        label = tk.Label(popup, text=text, bg="white", fg="black")
        label.pack(expand=True, fill="both")
        
        self.text_index = (self.text_index + 1) % len(Config.TEXT_CONTENT)
        popup.after(3000, popup.destroy)


# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

class RickrollApp:
    """Application principale."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.asset_manager = AssetManager()
        self.popup_factory = PopupFactory(self.asset_manager)
        self.sound_manager = SoundManager(self.root, self._on_second_song)
        
        self.step = 1
    
    def _on_second_song(self) -> None:
        """Callback appelé lors de la deuxième chanson."""
        self.step = 2
    
    def _create_popups_loop(self, delay: int = 1000) -> None:
        """Boucle de création des popups."""
        if random.random() > Config.TEXT_POPUP_PROBABILITY:
            self.popup_factory.create_animated_popup(self.root)
        else:
            self.popup_factory.create_text_popup(self.root, self.step)
        
        self.root.after(delay, lambda: self._create_popups_loop(delay))
    
    def run(self) -> None:
        """Lance l'application."""
        # Change le fond d'écran
        WallpaperManager.set_wallpaper(BACKGROUND_IMAGE)
        
        # Précharge les assets
        self.asset_manager.preload_gifs()
        
        # Lance la musique
        self.sound_manager.play_songs()
        
        # Lance la boucle de création des popups
        self._create_popups_loop(1000)
        
        # Lance la boucle principale Tkinter
        self.root.mainloop()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = RickrollApp()
    app.run()
