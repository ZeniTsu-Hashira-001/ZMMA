# Outil "Welcome/Goodbye" : génère une carte de bienvenue / au revoir.
# 5 styles disponibles (voir docstring de generate_card).

from PIL import Image, ImageDraw
from .helpers import (
    get_font, parse_color, download_image,
    image_to_bytes, wrap_text, star_mask
)


def generate_card(
    background_url: str,
    avatar_url: str,
    text: str,
    text_color: str = "white",
    style: int = 1,
) -> "io.BytesIO":
    """
    Génère une carte personnalisée.

    Styles :
      1 : fond 1:1, avatar carré centré, texte SOUS l'avatar.
      2 : fond étiré (16:9), avatar carré centré, texte SOUS.
      3 : fond étiré, avatar ROND centré, texte SOUS.
      4 : fond étiré, avatar en ÉTOILE centré, texte SOUS.
      5 : fond étiré, avatar ROND centré, texte EN HAUT.
    """
    # --- Choix de la taille de fond selon le style ---
    if style == 1:
        canvas_size = (700, 700)
    else:
        canvas_size = (900, 500)

    # --- Chargement des images distantes ---
    bg = download_image(background_url).resize(canvas_size, Image.Resampling.LANCZOS)
    avatar_raw = download_image(avatar_url)

    # --- Redimensionnement de l'avatar ---
    avatar_size = 200
    avatar = avatar_raw.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

    # --- Position de l'avatar (toujours centré horizontalement) ---
    cx = canvas_size[0] // 2
    if style == 5:
        cy = canvas_size[1] // 2  # style 5 : texte en haut, avatar centré
    else:
        cy = canvas_size[1] // 2 - 20
    paste_pos = (cx - avatar_size // 2, cy - avatar_size // 2)

    # --- Application du masque (carré, rond, étoile) ---
    if style in (1, 2):
        bg.paste(avatar, paste_pos, avatar)  # carré
    elif style in (3, 5):
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
        bg.paste(avatar, paste_pos, mask)
    elif style == 4:
        mask = star_mask((avatar_size, avatar_size), points=5)
        bg.paste(avatar, paste_pos, mask)

    # --- Dessin du texte ---
    draw = ImageDraw.Draw(bg)
    font = get_font(48)
    color = parse_color(text_color)

    lines = wrap_text(draw, text, font, max_width=canvas_size[0] - 80)
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 8
    total_h = line_height * len(lines)

    if style == 5:
        # Texte EN HAUT
        y = 40
    else:
        # Texte SOUS l'avatar
        y = paste_pos[1] + avatar_size + 30

    # Si le texte dépasse le bas, on le remonte légèrement
    if y + total_h > canvas_size[1] - 20:
        y = canvas_size[1] - total_h - 20

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (canvas_size[0] - w) / 2
        # Contour noir pour lisibilité sur n'importe quel fond
        draw.text((x, y), line, font=font, fill=color,
                  stroke_width=2, stroke_fill="black")
        y += line_height

    return image_to_bytes(bg, fmt="PNG")