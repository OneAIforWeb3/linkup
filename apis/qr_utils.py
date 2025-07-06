import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
    """Create a card-style QR code with ethglobal.png as background
    
    Args:
        qr_data: Data to encode in QR
        username: Telegram username to display
        size: Card size in pixels (width, height) - default 1200x675 (16:9 aspect ratio)
        qr_color: RGB tuple for QR code color (default: ETH Cannes blue)
        
    Returns:
        PIL.Image: Card image with QR code
    """
    try:
        # Load background image
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ethglobal.jpg')
        try:
            bg_image = Image.open(bg_path)
            # Resize background to fit card size while maintaining aspect ratio
            bg_image = bg_image.resize(size, Image.Resampling.LANCZOS)
        except Exception as e:
            # Create fallback gradient background
            bg_image = Image.new('RGB', size, (14, 165, 233))
            draw = ImageDraw.Draw(bg_image)
            for y in range(size[1]):
                ratio = y / size[1]
                r = int(14 * (1 - ratio) + 42 * ratio)
                g = int(165 * (1 - ratio) + 206 * ratio)
                b = int(233 * (1 - ratio) + 204 * ratio)
                draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for better design
            box_size=10,
            border=0,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image with specified color
        qr_img = qr.make_image(fill_color=qr_color, back_color='white')
        
        # Calculate QR code size and position (centered)
        qr_size = int(min(size) * 0.42)  # QR takes about 42% of the shortest dimension
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Create a new blank image with the background
        card = Image.new('RGBA', size, (0, 0, 0, 0))
        if bg_image.mode != 'RGBA':
            bg_image = bg_image.convert('RGBA')
        card.paste(bg_image, (0, 0))
        
        # Make the container bigger relative to QR
        qr_container_width = int(qr_size * 1.5)
        qr_container_height = int(qr_size * 1.5)
        
        # Calculate QR container position (centered)
        container_x = (size[0] - qr_container_width) // 2
        container_y = (size[1] - qr_container_height) // 2
        
        # Create translucent white container with rounded corners
        container = Image.new('RGBA', (qr_container_width, qr_container_height), (255, 255, 255, 0))
        mask = Image.new('L', (qr_container_width, qr_container_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        radius = 40  # corner radius
        mask_draw.rounded_rectangle([0, 0, qr_container_width, qr_container_height], radius=radius, fill=255)
        # Fill the rounded rectangle with semi-transparent white
        box = Image.new('RGBA', (qr_container_width, qr_container_height), (255, 255, 255, 170))
        container = Image.composite(box, container, mask)
        # Add blurry effect to the box
        blurred = container.filter(ImageFilter.GaussianBlur(radius=12))
        # Overlay the blurred box and then the main container for a glassy effect
        card.paste(blurred, (container_x, container_y), blurred)
        card.paste(container, (container_x, container_y), container)
        
        # Calculate QR position within container (centered horizontally, higher vertically)
        qr_x = container_x + (qr_container_width - qr_size) // 2
        qr_y = container_y + (qr_container_height - qr_size) // 3  # Place higher to leave room for text
        
        # Paste QR code onto card
        card.paste(qr_img, (qr_x, qr_y))
        
        # Add username text below QR code
        draw = ImageDraw.Draw(card)
        
        # Always use bundled font
        FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")
        try:
            username_font = ImageFont.truetype(FONT_PATH, 55)
        except (OSError, IOError):
            username_font = ImageFont.load_default()
        
        # Format the username
        if username:
            username_text = f"@{username}" if not username.startswith('@') else username
            # Get text width
            bbox = draw.textbbox((0, 0), username_text, font=username_font)
            username_width = bbox[2] - bbox[0]
            username_height = bbox[3] - bbox[1]
            # Position username just below the QR code, with a bit more padding
            username_x = container_x + (qr_container_width - username_width) // 2
            username_y = qr_y + qr_size + 32  # 32px padding below QR code
            # Add subtle shadow for better readability
            for offset in range(3, 0, -1):
                draw.text(
                    (username_x + offset, username_y + offset),
                    username_text,
                    fill=(0, 0, 0, 120),
                    font=username_font
                )
            # Main username text
            draw.text(
                (username_x, username_y),
                username_text,
                fill=qr_color,
                font=username_font
            )
        
        return card.convert('RGB')
        
    except Exception as e:
        print(f"Card QR generation failed: {e}")
        return None

