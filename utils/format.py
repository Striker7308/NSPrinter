import io
import re
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

def img2openai_b64(img):
    buffer = io.BytesIO()
    if img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(buffer, format='JPEG')
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"

def extract_float(text: str):
    # match positive / negative float: -12.34 , 5 , .5 , 10.
    matches = re.findall(r"-?\d+\.?\d*|-?\.\d+", text)
    if not matches:
        return None
    return float(matches[0])