import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random

def generate_qr_code_image(tg_id, size=300):
    """Generate QR code image for a given Telegram user ID - can be used by webapp API"""
    try:
        qr_data = f"user_{tg_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image
    except Exception as e:
        return None

def create_card_style_qr(qr_data, username, size=(1200, 675), qr_color=(0, 0, 0)):
    """Create a card-style QR code with ethglobal.jpg as background"""
    try:
        bg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ethglobal.jpg')
        try:
            bg_image = Image.open(bg_path)
            bg_image = bg_image.resize(size, Image.Resampling.LANCZOS)
        except Exception:
            bg_image = Image.new('RGB', size, (14, 165, 233))
            draw = ImageDraw.Draw(bg_image)
            for y in range(size[1]):
                ratio = y / size[1]
                r = int(14 * (1 - ratio) + 42 * ratio)
                g = int(165 * (1 - ratio) + 206 * ratio)
                b = int(233 * (1 - ratio) + 204 * ratio)
                draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=0,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=qr_color, back_color='white')
        qr_size = min(size) // 3
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        card = Image.new('RGBA', size, (0, 0, 0, 0))
        if bg_image.mode != 'RGBA':
            bg_image = bg_image.convert('RGBA')
        card.paste(bg_image, (0, 0))
        qr_container_width = int(qr_size * 1.5)
        qr_container_height = int(qr_size * 1.8)
        container_x = (size[0] - qr_container_width) // 2
        container_y = (size[1] - qr_container_height) // 2
        container = Image.new('RGBA', (qr_container_width, qr_container_height), (255, 255, 255, 128))
        container_border = Image.new('RGBA', (qr_container_width, qr_container_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(container_border)
        draw.rectangle([0, 0, qr_container_width-1, qr_container_height-1], outline=(255, 255, 255, 180), width=2)
        for _ in range(100):
            x = random.randint(0, qr_container_width-1)
            y = random.randint(0, qr_container_height-1)
            radius = random.randint(1, 3)
            alpha = random.randint(5, 20)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=(255, 255, 255, alpha))
        container = Image.alpha_composite(container, container_border)
        card.paste(container, (container_x, container_y), container)
        qr_x = container_x + (qr_container_width - qr_size) // 2
        qr_y = container_y + (qr_container_height - qr_size) // 3
        card.paste(qr_img, (qr_x, qr_y))
        draw = ImageDraw.Draw(card)
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "arial.ttf",
        ]
        username_font = None
        for font_path in font_paths:
            try:
                username_font = ImageFont.truetype(font_path, 60)
                break
            except (OSError, IOError):
                continue
        if username_font is None:
            username_font = ImageFont.load_default()
        if username:
            username_text = f"@{username}" if not username.startswith('@') else username
            bbox = draw.textbbox((0, 0), username_text, font=username_font)
            username_width = bbox[2] - bbox[0]
            username_x = container_x + (qr_container_width - username_width) // 2
            username_y = qr_y + qr_size + 20
            draw.text((username_x, username_y), username_text, fill=qr_color, font=username_font)
        return card.convert('RGB')
    except Exception as e:
        return None 