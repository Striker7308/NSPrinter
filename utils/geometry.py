import os, io
import cv2
import numpy as np
from PIL import Image

def polygon_to_xyxy(points):
    """
    Convert a polygon point set to the smallest bounding box in xyxy format.
    Args:
        points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    Returns:
        [x1, y1, x2, y2]
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]

def transform_polygon(points, scale_x=1.0, scale_y=1.0, dx_ratio=0, dy_ratio=0):
    pts = np.array(points, dtype=float)
    center = pts.mean(axis=0)
    width = pts[:, 0].max() - pts[:, 0].min()
    height = pts[:, 1].max() - pts[:, 1].min()
    scaled = center + (pts - center) * np.array([scale_x, scale_y])
    dx, dy = width * dx_ratio, height * dy_ratio
    scaled[:, 0] += dx
    scaled[:, 1] += dy
    return scaled.astype(int).tolist()


def clean_signature_to_binary(img, output_size=None, threshold_block_size=35, min_area=50, max_area=2000):
    """
    Clean a cropped signature image: remove background, noise, and convert to binary (1-bit) image.
    The output is suitable for embedding into PDFs using fpdf.
    Args:
        image_path (str): Path to the input image (cropped signature area).
        output_size (tuple, optional): Target output size (width, height) for resizing.
                                       Example: (200, 80). Default is None (keep original size).
        threshold_block_size (int): Adaptive threshold block size. Must be an odd number.
                                    15 works well for most signatures. Adjust if strokes are broken or merged.
        min_area (int): Minimum contour area to keep. Used to filter out small noise dots.
                        50 is a good starting point. Increase to remove more noise.
    Returns:
        PIL.Image: A binary (1-bit) PIL Image object with white background and black signature strokes.
                   Returns None if an error occurs.
    """
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./cv_gray.jpg', gray)

    # 4. Apply adaptive thresholding to create binary image
    # This handles uneven lighting better than simple global threshold
    # THRESH_BINARY_INV: white strokes on black background (temporary)
    binary = cv2.adaptiveThreshold(
        gray,  # Input grayscale image
        255,  # Maximum value (white)
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive method
        cv2.THRESH_BINARY_INV,  # Binary inverse mode (strokes become white)
        threshold_block_size,  # Block size (must be odd)
        10  # Constant subtracted from mean
    )
    cv2.imwrite('./cv_binary.jpg', binary)


    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    cv2.imwrite('./cv_cleaned.jpg', cleaned)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty mask (all black)
    mask = np.zeros_like(cleaned)

    # Draw only contours that are larger than min_area
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            # Fill the contour with white (255)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            cv2.drawContours(img, [contour], -1, (0, 0, 255), 1)
            # cv2.imwrite('./cv_contours_'+str(i)+'.jpg', img)
    cv2.imwrite('./cv_contours.jpg', img)

    # 7. Convert back to PIL Image
    signed = cv2.bitwise_and(cleaned, mask)
    cv2.imwrite('./cv_signed.jpg', signed)

    # Convert OpenCV image (numpy array) to PIL Image
    final_image = Image.fromarray(cv2.bitwise_not(signed))

    # 8. Convert to 1-bit (binary) mode
    # '1' mode uses only 2 colors: black (0) and white (255)
    # This is ideal for PDF embedding and keeps file size small
    final_image = final_image.convert('1')

    # 9. Resize if output_size is specified
    if output_size is not None:
        # Use LANCZOS resampling for high quality
        final_image = final_image.resize(output_size, Image.Resampling.LANCZOS)

    return final_image

def get_barcode_center(bar):
    """计算条码包围框中心点"""
    pos = bar.position
    # 取左上角、右下角
    tl = pos.top_left
    br = pos.bottom_right
    cx = (tl.x + br.x) / 2.0
    cy = (tl.y + br.y) / 2.0
    return (cx, cy)


def format_barcodes(barcodes):
    barcode_txt = {'combined': '', 'code002026': '', 'code89': ''}
    barcodes_sorted = sorted(
        barcodes,
        key=lambda b: get_barcode_center(b)[::-1]
    )
    # for barcode in barcodes:
    #     print(barcode.text)
    barcode_txt['combined'] = next((barcode.text for barcode in barcodes if '+' in barcode.text), "")
    barcode_txt['code002026'] = next((barcode.text for barcode in barcodes if '002026' in barcode.text and '+' not in barcode.text), "")
    barcode_txt['code89'] = next((barcode.text for barcode in barcodes if '89' in barcode.text and '+' not in barcode.text), "")
    return barcode_txt, barcodes_sorted


def resize_for_doubao_(image: Image.Image, max_total_pixels=36000000) -> bytes:
    w, h = image.size
    total = w * h
    if total <= max_total_pixels:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

    # 计算缩放比例
    scale = (max_total_pixels / total) ** 0.5
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    resized.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

def resize_for_doubao(img, max_total_pixels=36000000-1000):
    w, h = img.size
    resolution = w * h
    if resolution <= max_total_pixels:
        return img

    scale = (max_total_pixels / resolution) ** 0.5
    new_w, new_h = int(w * scale), int(h * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return resized