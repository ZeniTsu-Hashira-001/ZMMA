# Outil "Reverse" : inverse horizontalement une image (effet miroir gauche/droite).

from PIL import Image, ImageOps
from .helpers import download_image, image_to_bytes


def reverse_image_from_url(url: str):
    """Télécharge l'image depuis l'URL, l'inverse, retourne un BytesIO."""
    img = download_image(url)
    reversed_img = ImageOps.mirror(img)  # Équivaut à FLIP_LEFT_RIGHT
    return image_to_bytes(reversed_img, fmt="PNG")