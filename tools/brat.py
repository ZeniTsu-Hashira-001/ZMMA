# Outil "Brat" : génère une image fond coloré + texte centré.

from PIL import Image, ImageDraw
from .helpers import get_font, parse_color, image_to_bytes, wrap_text


def generate_brat_image(text: str, background: str = "white", text_color: str = "black") -> "io.BytesIO":
    """
    Génère une image carrée style "Brat" avec un texte centré.
    - text : 1 à 50 caractères.
    - background : nom de couleur ou hex ou "r,g,b".
    - text_color : idem.
    """
    size = (600, 600)
    bg_rgb = parse_color(background)
    fg_rgb = parse_color(text_color)

    img = Image.new("RGB", size, bg_rgb)
    draw = ImageDraw.Draw(img)

    # Police dynamique : plus le texte est long, plus la police est petite
    font_size = 80 if len(text) <= 20 else (60 if len(text) <= 35 else 45)
    font = get_font(font_size)

    # Découpe le texte si nécessaire (max 50 char, mais on gère les espaces longs)
    lines = wrap_text(draw, text, font, max_width=size[0] - 80)
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 10
    total_height = line_height * len(lines)

    # Centrage vertical et horizontal
    y = (size[1] - total_height) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (size[0] - w) / 2
        draw.text((x, y), line, fill=fg_rgb, font=font)
        y += line_height

    return image_to_bytes(img, fmt="PNG")