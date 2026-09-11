# Point d'entrée de l'API Zenitdu Multitool Maker.
# Lancement local :  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse

from tools.brat import generate_brat_image
from tools.reverse import reverse_image_from_url
from tools.black_and_white import black_and_white_from_url
from tools.welcome_goodbye import generate_card


app = FastAPI(
    title="Zenitdu Multitool Maker",
    description="Image generation & manipulation API.",
    version="1.0.0",
)


# ---------- Root ----------
@app.get("/", summary="API info")
async def root():
    return {
        "name": "Zenitdu Multitool Maker",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "brat": "/brat?text=Hello+World&background=white&textcolor=black",
            "reverse": "/reverse?url=https://example.com/image.jpg",
            "bw": "/bw?url=https://example.com/image.jpg",
            "welcome": "/welcome?background=URL&avatar=URL&text=Welcome&textcolor=white&style=1",
        },
    }


# ---------- /brat ----------
@app.get("/brat", summary="Generate a Brat-style image")
async def brat(
    text: str = Query(..., min_length=1, max_length=50,
                      description="Text to display (1-50 characters)"),
    background: str = Query("white",
                            description="Background color (name, hex, or r,g,b)"),
    textcolor: str = Query("black",
                           description="Text color (name, hex, or r,g,b)"),
):
    try:
        buf = generate_brat_image(text, background, textcolor)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brat generation failed: {e}")


# ---------- /reverse ----------
@app.get("/reverse", summary="Mirror an image horizontally")
async def reverse(
    url: str = Query(..., description="Direct URL of the source image"),
):
    try:
        buf = reverse_image_from_url(url)
        return StreamingResponse(buf, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse failed: {e}")


# ---------- /bw ----------
@app.get("/bw", summary="Convert an image to black & white")
async def bw(
    url: str = Query(..., description="Direct URL of the source image"),
):
    try:
        buf = black_and_white_from_url(url)
        return StreamingResponse(buf, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"B&W conversion failed: {e}")


# ---------- /welcome ----------
@app.get("/welcome", summary="Generate a welcome/goodbye card")
async def welcome(
    background: str = Query(..., description="Direct URL of the background image"),
    avatar: str = Query(..., description="Direct URL of the avatar image"),
    text: str = Query(..., min_length=1, max_length=20,
                      description="Text to display (1-20 characters)"),
    textcolor: str = Query("white",
                           description="Text color (name, hex, or r,g,b)"),
    style: int = Query(1, ge=1, le=5,
                       description="Card style (1 to 5)"),
):
    try:
        buf = generate_card(background, avatar, text, textcolor, style)
        return StreamingResponse(buf, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Welcome card failed: {e}")