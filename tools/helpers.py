# Fonctions utilitaires partagées entre tous les outils.

import math
import io
import requests
from PIL import Image, ImageFont, ImageDraw, ImageColor


# Liste de chemins de polices à essayer (Linux / macOS / Windows / fallback).
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "arial.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]


def get_font(size: int = 40) -> ImageFont.FreeTypeFont:
    """Retourne une police TrueType si trouvée, sinon la police par défaut."""
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # Fallback ultime : police bitmap par défaut de Pillow
    return ImageFont.load_default()


def parse_color(value: str):
    """
    Convertit une chaîne de couleur en tuple RGB(A).
    Accepte : 'white', 'black', '#ffffff', '255,255,255'.
    """
    if not value:
        return (0, 0, 0)
    value = value.strip()
    # Format "r,g,b" ou "r,g,b,a"
    if "," in value:
        try:
            parts = tuple(int(p.strip()) for p in value.split(","))
            if len(parts) in (3, 4) and all(0 <= p <= 255 for p in parts):
                return parts
        except ValueError:
            pass
    # Nom de couleur ou hexadécimal
    try:
        return ImageColor.getrgb(value)
    except ValueError:
        return (0, 0, 0)  # fallback noir


def download_image(url: str) -> Image.Image:
    """Télécharge une image depuis une URL et la retourne en RGBA."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "ZenitduMultitool/1.0"})
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        return img
    except Exception as e:
        raise ValueError(f"Failed to fetch image from URL: {e}")


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> io.BytesIO:
    """Convertit une image PIL en buffer BytesIO prêt pour StreamingResponse."""
    buf = io.BytesIO()
    # Convertir en RGB si on sauvegarde en JPEG (pas d'alpha)
    if fmt.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    img.save(buf, format=fmt, quality=95)
    buf.seek(0)
    return buf


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    """
    Découpe un texte en plusieurs lignes pour qu'il tienne dans max_width.
    Retourne une liste de lignes.
    """
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def star_mask(size: tuple, points: int = 5, outer_ratio: float = 0.5, inner_ratio: float = 0.22):
    """
    Crée un masque en forme d'étoile (fond noir, étoile blanche).
    Utilisé pour l'avatar style 4.
    """
    w, h = size
    cx, cy = w / 2, h / 2
    outer_r = min(w, h) * outer_ratio
    inner_r = min(w, h) * inner_ratio

    coords = []
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = -math.pi / 2 + i * math.pi / points
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        coords.append((x, y))

    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(coords, fill=255)
    return mask