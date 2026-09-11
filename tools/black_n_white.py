# Outil "B&W" : convertit une image couleur en niveaux de gris.

from .helpers import download_image, image_to_bytes


def black_and_white_from_url(url: str):
    """Télécharge l'image, la convertit en noir et blanc, retourne un BytesIO."""
    img = download_image(url)
    bw = img.convert("L").convert("RGB")  # L = luminance, puis retour en RGB pour cohérence
    return image_to_bytes(bw, fmt="PNG")