import io

from PIL import Image, ImageDraw, ImageEnhance
import base64

def image_to_openai_b64(img_fp: str) -> str:
    with Image.open(img_fp) as im:
        # Force render main image frame, drop MPO / HDR gain‑map / bad exif
        buf = io.BytesIO()
        im.convert("RGB").save(buf, format="JPEG", quality=90)
        raw = buf.getvalue()
    b64 = base64.b64encode(raw).decode("utf‑8").replace("\n","").replace("\r","").strip()
    return f"data:image/jpeg;base64,{b64}"
