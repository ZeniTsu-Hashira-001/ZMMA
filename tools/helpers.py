# Fonctions utilitaires partagées entre tous les outils.

import math
import io
import urllib.parse
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


# Hébergeurs connus pour bloquer les IPs de datacenter (Render, AWS, etc.).
# On les fait passer par un proxy d'images public.
BLOCKED_HOSTS = ("catbox.moe", "litter.catbox.moe")

# Proxy public gratuit et fiable pour les images.
IMAGE_PROXY = "https://wsrv.nl/?url="


def get_font(size: int = 40) -> ImageFont.FreeTypeFont:
    """Retourne une police TrueType si trouvée, sinon la police par défaut."""
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
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


def _needs_proxy(url: str) -> bool:
    """Vérifie si l'URL pointe vers un hébergeur qui bloque les datacenters."""
    try:
        host = urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return False
    return any(blocked in host for blocked in BLOCKED_HOSTS)


def download_image(url: str) -> Image.Image:
    """
    Télécharge une image depuis une URL et la retourne en RGBA.
    Passe automatiquement par un proxy si l'hébergeur bloque les serveurs cloud.
    """
    original_url = url

    # Si l'hébergeur bloque les IPs cloud, on route via un proxy d'images.
    if _needs_proxy(url):
        url = IMAGE_PROXY + urllib.parse.quote(url, safe="")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, timeout=25, headers=headers)
        resp.raise_for_status()

        # Vérifier que la réponse est bien une image
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/") and "octet-stream" not in content_type:
            # Certains proxies renvoient une image sans content-type propre
            if len(resp.content) < 100:
                raise ValueError(
                    f"URL did not return an image (content-type: {content_type})"
                )

        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        return img

    except requests.exceptions.Timeout:
        raise ValueError(f"Timeout while fetching image: {original_url}")
    except requests.exceptions.ConnectionError as e:
        raise ValueError(f"Connection refused while fetching image: {original_url} ({e})")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error while fetching image: {original_url} ({e})")
    except Exception as e:
        raise ValueError(f"Failed to fetch image from URL: {e}")


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> io.BytesIO:
    """Convertit une image PIL en buffer BytesIO prêt pour StreamingResponse."""
    buf = io.BytesIO()
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
