#!/usr/bin/env python3
"""
WeMeetAI Telegram Bot - Running on ROFL
A networking assistant for event attendees
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram_api import telegram_api, initialize_telegram_api, close_telegram_api
from apis.api_client import api_client
from apis.qr_utils import generate_qr_code_image, create_card_style_qr
import qrcode
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import random
import math
from typing import List, Dict
import asyncio
import re

load_dotenv()

# Get base URL for the web app from environment variable or use default
WEBAPP_BASE_URL = os.getenv("WEBAPP_BASE_URL", "https://your-api-domain.com")

def get_full_name(user):
    """Get full name from user object, fallback to first name or user ID"""
    if hasattr(user, 'first_name') and user.first_name:
        full_name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            full_name += f" {user.last_name}"
        return full_name
    return f"User {user.id if hasattr(user, 'id') else 'Unknown'}"

# QR Code Themes - Enhanced with more vibrant colors
QR_THEMES = {
    'ethcc': {
        'bg_colors': [(0, 155, 208), (42, 206, 204)],  # ETHCC blue/teal
        'pattern': 'ethcc',
        'qr_colors': [(255, 255, 255), (255, 147, 91)]  # White and light orange
    }
}

def create_gradient_background(width, height, colors):
    """Create a gradient background"""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    color1, color2 = colors
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return image

def add_pattern_overlay(image, pattern_type, opacity=30):
    """Add decorative patterns to background"""
    width, height = image.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    if pattern_type == 'tech':
        # Add circuit-like patterns
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(10, 30)
            draw.ellipse([x, y, x+size, y+size], outline=(255, 255, 255, opacity))
    
    elif pattern_type == 'crypto':
        # Add diamond/crystal patterns
        for _ in range(15):
            x = random.randint(0, width-40)
            y = random.randint(0, height-40)
            points = [(x+20, y), (x+40, y+20), (x+20, y+40), (x, y+20)]
            draw.polygon(points, outline=(255, 255, 255, opacity))
    
    elif pattern_type == 'waves':
        # Add wave patterns
        for i in range(0, width, 50):
            points = []
            for x in range(i, min(i+100, width), 10):
                y = height//2 + 30 * math.sin(x * 0.1)
                points.append((x, int(y)))
            if len(points) > 1:
                for j in range(len(points)-1):
                    draw.line([points[j], points[j+1]], fill=(255, 255, 255, opacity), width=2)
    
    elif pattern_type == 'geometric':
        # Add geometric shapes
        for _ in range(25):
            x = random.randint(0, width-30)
            y = random.randint(0, height-30)
            if random.choice([True, False]):
                draw.rectangle([x, y, x+20, y+20], outline=(255, 255, 255, opacity))
            else:
                draw.ellipse([x, y, x+20, y+20], outline=(255, 255, 255, opacity))
    
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    return image.convert('RGB')

def create_enhanced_gradient_background(width, height, colors):
    """Create an enhanced gradient background with multiple layers"""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create multiple gradient layers for richer colors
    color1, color2 = colors
    
    # Main gradient
    for y in range(height):
        ratio = y / height
        # Add some curve to the gradient for more visual interest
        curve_ratio = 0.5 * (1 + math.sin(math.pi * (ratio - 0.5)))
        
        r = int(color1[0] * (1 - curve_ratio) + color2[0] * curve_ratio)
        g = int(color1[1] * (1 - curve_ratio) + color2[1] * curve_ratio)
        b = int(color1[2] * (1 - curve_ratio) + color2[2] * curve_ratio)
        
        # Add slight variation for depth
        r = max(0, min(255, r + random.randint(-10, 10)))
        g = max(0, min(255, g + random.randint(-10, 10)))
        b = max(0, min(255, b + random.randint(-10, 10)))
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add diagonal gradient overlay for more depth
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    for x in range(width):
        ratio = x / width
        alpha = int(30 * math.sin(math.pi * ratio))  # Subtle overlay
        overlay_draw.line([(x, 0), (x, height)], fill=(255, 255, 255, alpha))
    
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    return image.convert('RGB')

def add_enhanced_pattern_overlay(image, pattern_type, opacity=40):
    """Add enhanced decorative patterns to background"""
    width, height = image.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    if pattern_type == 'tech':
        # Enhanced tech patterns with circuit-like designs
        for _ in range(30):
            x = random.randint(0, width-60)
            y = random.randint(0, height-60)
            size = random.randint(15, 40)
            
            # Circuit nodes
            draw.ellipse([x, y, x+size, y+size], outline=(255, 255, 255, opacity))
            
            # Connecting lines
            if random.choice([True, False]):
                line_length = random.randint(30, 80)
                if random.choice([True, False]):  # Horizontal
                    draw.line([(x+size, y+size//2), (x+size+line_length, y+size//2)], 
                             fill=(255, 255, 255, opacity//2), width=2)
                else:  # Vertical
                    draw.line([(x+size//2, y+size), (x+size//2, y+size+line_length)], 
                             fill=(255, 255, 255, opacity//2), width=2)
    
    elif pattern_type == 'ethcc':
        # ETHCC inspired pattern with triangular elements like the logo
        for _ in range(25):
            x = random.randint(0, width-70)
            y = random.randint(0, height-70)
            size = random.randint(30, 60)
            
            # Create triangular shapes inspired by ETHCC logo
            if random.choice([True, False]):
                # Upward pointing triangle (like top of logo)
                points = [(x+size//2, y), (x+size, y+size), (x, y+size)]
                draw.polygon(points, outline=(255, 255, 255, opacity), width=2)
            else:
                # Downward pointing triangle (like bottom of logo)
                points = [(x, y), (x+size, y), (x+size//2, y+size)]
                draw.polygon(points, outline=(255, 255, 255, opacity), width=2)
                
            # Add secondary shape for more complex pattern
            x_offset = random.randint(-20, 20)
            y_offset = random.randint(-20, 20)
            smaller_size = size // 2
            
            if random.choice([True, False, False]):  # Less frequently
                # Add hexagon shape (inspired by Ethereum)
                hex_size = smaller_size
                hex_points = [
                    (x+x_offset+hex_size//2, y+y_offset),
                    (x+x_offset+hex_size, y+y_offset+hex_size//4),
                    (x+x_offset+hex_size, y+y_offset+3*hex_size//4),
                    (x+x_offset+hex_size//2, y+y_offset+hex_size),
                    (x+x_offset, y+y_offset+3*hex_size//4),
                    (x+x_offset, y+y_offset+hex_size//4)
                ]
                draw.polygon(hex_points, outline=(255, 255, 255, opacity//2), width=1)
    
    elif pattern_type == 'crypto':
        # Enhanced crypto patterns with diamond crystals
        for _ in range(20):
            x = random.randint(0, width-60)
            y = random.randint(0, height-60)
            size = random.randint(20, 50)
            
            # Diamond shape
            points = [(x+size//2, y), (x+size, y+size//2), (x+size//2, y+size), (x, y+size//2)]
            draw.polygon(points, outline=(255, 255, 255, opacity), width=2)
            
            # Inner diamond
            inner_offset = size // 4
            inner_points = [(x+size//2, y+inner_offset), (x+size-inner_offset, y+size//2), 
                          (x+size//2, y+size-inner_offset), (x+inner_offset, y+size//2)]
            draw.polygon(inner_points, outline=(255, 255, 255, opacity//2))
    
    elif pattern_type == 'waves':
        # Enhanced wave patterns
        wave_count = 8
        for i in range(wave_count):
            amplitude = random.randint(20, 40)
            frequency = random.uniform(0.02, 0.05)
            phase = random.uniform(0, 2 * math.pi)
            y_offset = (height // wave_count) * i
            
            points = []
            for x in range(0, width, 5):
                y = y_offset + amplitude * math.sin(frequency * x + phase)
                points.append((x, int(y)))
            
            for j in range(len(points)-1):
                draw.line([points[j], points[j+1]], fill=(255, 255, 255, opacity//2), width=3)
    
    elif pattern_type == 'geometric':
        # Enhanced geometric patterns
        for _ in range(35):
            x = random.randint(0, width-40)
            y = random.randint(0, height-40)
            size = random.randint(15, 35)
            shape_type = random.choice(['rect', 'circle', 'triangle'])
            
            if shape_type == 'rect':
                draw.rectangle([x, y, x+size, y+size], outline=(255, 255, 255, opacity), width=2)
            elif shape_type == 'circle':
                draw.ellipse([x, y, x+size, y+size], outline=(255, 255, 255, opacity), width=2)
            else:  # triangle
                points = [(x+size//2, y), (x+size, y+size), (x, y+size)]
                draw.polygon(points, outline=(255, 255, 255, opacity), width=2)
    
    elif pattern_type == 'nature':
        # Nature-inspired patterns for forest theme
        for _ in range(25):
            x = random.randint(0, width-50)
            y = random.randint(0, height-50)
            
            # Draw leaf-like shapes
            size = random.randint(20, 40)
            # Leaf outline
            points = [(x, y+size//2), (x+size//4, y), (x+size//2, y+size//4), 
                     (x+3*size//4, y), (x+size, y+size//2), (x+3*size//4, y+size),
                     (x+size//2, y+3*size//4), (x+size//4, y+size)]
            
            draw.polygon(points, outline=(255, 255, 255, opacity//2))
    
    else:  # clean/minimal
        # Subtle dot pattern for minimal theme
        for _ in range(40):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 6)
            draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, opacity//3))
    
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    return image.convert('RGB')

def add_decorative_elements(draw, size, theme_config):
    """Add sophisticated decorative elements to the QR code"""
    # Enhanced corner decorations with theme-specific styling
    corner_size = int(size * 0.06)  # Proportional to canvas size
    line_width = max(3, int(size * 0.004))
    
    # Corner positions with better spacing
    margin = int(size * 0.03)
    corners = [
        (margin, margin),  # Top-left
        (size - margin - corner_size, margin),  # Top-right
        (margin, size - margin - corner_size),  # Bottom-left
        (size - margin - corner_size, size - margin - corner_size)  # Bottom-right
    ]
    
    for i, (x, y) in enumerate(corners):
        # Create different corner styles based on theme
        if theme_config.get('pattern') == 'ethcc':
            # ETHCC style corners with triangular elements
            if i == 0:  # Top-left
                # Create a triangular corner decoration
                triangle_points = [
                    (x, y),
                    (x + corner_size, y),
                    (x, y + corner_size)
                ]
                draw.polygon(triangle_points, outline=(255, 255, 255, 200), width=line_width)
                # Inner detail
                smaller_size = corner_size // 2
                smaller_triangle = [
                    (x + 4, y + 4),
                    (x + smaller_size, y + 4),
                    (x + 4, y + smaller_size)
                ]
                draw.polygon(smaller_triangle, outline=(255, 255, 255, 150), width=line_width//2)
            elif i == 1:  # Top-right
                # Create a triangular corner decoration
                triangle_points = [
                    (x + corner_size, y),
                    (x + corner_size, y + corner_size),
                    (x, y)
                ]
                draw.polygon(triangle_points, outline=(255, 255, 255, 200), width=line_width)
                # Inner detail
                smaller_size = corner_size // 2
                smaller_triangle = [
                    (x + corner_size - 4, y + 4),
                    (x + corner_size - 4, y + smaller_size),
                    (x + corner_size - smaller_size, y + 4)
                ]
                draw.polygon(smaller_triangle, outline=(255, 255, 255, 150), width=line_width//2)
            elif i == 2:  # Bottom-left
                # Create a triangular corner decoration
                triangle_points = [
                    (x, y + corner_size),
                    (x + corner_size, y + corner_size),
                    (x, y)
                ]
                draw.polygon(triangle_points, outline=(255, 255, 255, 200), width=line_width)
                # Inner detail
                smaller_size = corner_size // 2
                smaller_triangle = [
                    (x + 4, y + corner_size - 4),
                    (x + smaller_size, y + corner_size - 4),
                    (x + 4, y + corner_size - smaller_size)
                ]
                draw.polygon(smaller_triangle, outline=(255, 255, 255, 150), width=line_width//2)
            else:  # Bottom-right
                # Create a triangular corner decoration
                triangle_points = [
                    (x + corner_size, y),
                    (x + corner_size, y + corner_size),
                    (x, y + corner_size)
                ]
                draw.polygon(triangle_points, outline=(255, 255, 255, 200), width=line_width)
                # Inner detail
                smaller_size = corner_size // 2
                smaller_triangle = [
                    (x + corner_size - 4, y + corner_size - 4),
                    (x + corner_size - 4, y + corner_size - smaller_size),
                    (x + corner_size - smaller_size, y + corner_size - 4)
                ]
                draw.polygon(smaller_triangle, outline=(255, 255, 255, 150), width=line_width//2)
        elif theme_config.get('pattern') in ['tech', 'crypto']:
            # Tech/crypto: Square corners with inner details
            draw.rectangle([x, y, x + corner_size, y + corner_size], 
                         outline=(255, 255, 255, 200), width=line_width)
            # Inner square
            inner_margin = corner_size // 4
            draw.rectangle([x + inner_margin, y + inner_margin, 
                          x + corner_size - inner_margin, y + corner_size - inner_margin], 
                         outline=(255, 255, 255, 150), width=line_width//2)
        else:
            # Other themes: Circular corners
            draw.ellipse([x, y, x + corner_size, y + corner_size], 
                        outline=(255, 255, 255, 200), width=line_width)
            # Inner circle
            inner_margin = corner_size // 4
            draw.ellipse([x + inner_margin, y + inner_margin, 
                         x + corner_size - inner_margin, y + corner_size - inner_margin], 
                        outline=(255, 255, 255, 150), width=line_width//2)
    
    # Add subtle border frame - customized by theme
    frame_margin = int(size * 0.01)
    if theme_config.get('pattern') == 'ethcc':
        # For ETHCC, add a border frame with triangular corners
        # Draw border lines
        line_width = 3
        # Top line
        draw.line([(frame_margin + corner_size, frame_margin), 
                  (size - frame_margin - corner_size, frame_margin)], 
                 fill=(255, 255, 255, 100), width=line_width)
        # Right line
        draw.line([(size - frame_margin, frame_margin + corner_size), 
                  (size - frame_margin, size - frame_margin - corner_size)], 
                 fill=(255, 255, 255, 100), width=line_width)
        # Bottom line
        draw.line([(frame_margin + corner_size, size - frame_margin), 
                  (size - frame_margin - corner_size, size - frame_margin)], 
                 fill=(255, 255, 255, 100), width=line_width)
        # Left line
        draw.line([(frame_margin, frame_margin + corner_size), 
                  (frame_margin, size - frame_margin - corner_size)], 
                 fill=(255, 255, 255, 100), width=line_width)
    else:
        # Standard border for other themes
        draw.rectangle([frame_margin, frame_margin, size - frame_margin, size - frame_margin], 
                      outline=(255, 255, 255, 100), width=2)

def create_themed_qr(qr_data, username, event_name=None, theme='ethcc', size=1000):
    """Create a themed QR code with username and optional event name"""
    try:
        
        # Get theme configuration
        theme_config = QR_THEMES.get(theme, QR_THEMES['ethcc'])
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for better design
            box_size=10,
            border=0,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image with custom colors
        qr_img = qr.make_image(fill_color='black', back_color='white')
        
        # Create main canvas with padding
        canvas = Image.new('RGB', (size, size), 'white')
        
        # Create enhanced gradient background
        bg = create_enhanced_gradient_background(size, size, theme_config['bg_colors'])
        
        # Add enhanced pattern overlay
        bg = add_enhanced_pattern_overlay(bg, theme_config['pattern'])
        
        # Paste background
        canvas.paste(bg, (0, 0))
        
        # Calculate QR code size and position with better spacing
        qr_size = int(size * 0.4)  # QR takes 40% of the shortest dimension
        qr_x = (size - qr_size) // 2
        
        # Dynamic positioning based on whether event name exists
        if event_name:
            qr_y = int(size * 0.35)  # Lower position when event name exists
        else:
            qr_y = int(size * 0.28)  # Higher position when no event name, moved up to make room for username below
        
        # Resize and paste QR code
        qr_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Create enhanced white background for QR with shadow effect
        qr_bg_size = qr_size + 60
        qr_bg = Image.new('RGBA', (qr_bg_size, qr_bg_size), (0, 0, 0, 0))
        
        # Add shadow
        shadow_offset = 8
        for i in range(shadow_offset):
            shadow_alpha = int(40 * (shadow_offset - i) / shadow_offset)
            shadow_bg = Image.new('RGBA', (qr_bg_size, qr_bg_size), (0, 0, 0, shadow_alpha))
            qr_bg = Image.alpha_composite(qr_bg, shadow_bg)
        
        # Add white background with rounded corners effect
        white_bg = Image.new('RGBA', (qr_bg_size, qr_bg_size), (255, 255, 255, 250))
        qr_bg.paste(white_bg, (0, 0), white_bg)
        
        # Paste QR code
        qr_bg.paste(qr_resized, (30, 30))
        
        # Convert canvas to RGBA for blending
        canvas = canvas.convert('RGBA')
        canvas.paste(qr_bg, (qr_x - 30, qr_y - 30), qr_bg)
        
        # Enhanced text rendering
        draw = ImageDraw.Draw(canvas)
        
        # Try to load better fonts with different sizes
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "arial.ttf",  # Windows
            ]
            
            # INCREASED FONT SIZES for better visibility
            title_font = None
            username_font = None
            event_font = None
            
            for font_path in font_paths:
                try:
                    title_font = ImageFont.truetype(font_path, 85)  # Larger for title
                    username_font = ImageFont.truetype(font_path, 72)  # INCREASED for username
                    event_font = ImageFont.truetype(font_path, 60)  # Larger for event
                    break
                except (OSError, IOError):
                    continue
            
            # Fallback to default if no fonts found
            if username_font is None:
                title_font = ImageFont.load_default()
                username_font = ImageFont.load_default()
                event_font = ImageFont.load_default()
                
        except:
            title_font = ImageFont.load_default()
            username_font = ImageFont.load_default()
            event_font = ImageFont.load_default()
        
        # Add event name at top with better positioning
        if event_name:
            event_text = f"🎪 {event_name.upper()}"
            bbox = draw.textbbox((0, 0), event_text, font=event_font)
            event_width = bbox[2] - bbox[0]
            event_x = (size - event_width) // 2
            event_y = int(size * 0.08)  # Top positioning with percentage
            
            # Enhanced text shadow with multiple layers
            for offset in range(4, 0, -1):
                shadow_alpha = int(120 * offset / 4)
                draw.text((event_x + offset, event_y + offset), event_text, 
                         fill=(0, 0, 0, shadow_alpha), font=event_font)
            
            # Main event text with gradient effect simulation
            draw.text((event_x, event_y), event_text, fill=(255, 255, 255, 255), font=event_font)
        
        # Add username BELOW the QR code with improved visibility
        username_text = f"@{username}" if not username.startswith('@') else username
        
        bbox = draw.textbbox((0, 0), username_text, font=username_font)
        username_width = bbox[2] - bbox[0]
        username_x = (size - username_width) // 2
        
        # Position username just below the QR code, with small padding
        username_y = qr_y + qr_size + 18  # 18px padding below QR code
        
        # Enhanced username text shadow for better readability
        for offset in range(4, 0, -1):
            shadow_alpha = int(160 * offset / 4)  # Increased shadow opacity
            draw.text((username_x + offset, username_y + offset), username_text, 
                     fill=(0, 0, 0, shadow_alpha), font=username_font)
        
        # Main username text
        draw.text((username_x, username_y), username_text, fill=(255, 255, 255, 255), font=username_font)
        
        # Add decorative elements
        add_decorative_elements(draw, size, theme_config)
        
        # Add ETHCC logo in top right corner if theme is 'ethcc'
        if theme == 'ethcc':
            # Define the logo size - make it prominent but not overwhelming
            logo_size = int(size * 0.2)  # 20% of the canvas width
            
            # Create a simplified ETHCC logo using triangular shapes
            # Top triangle (blue)
            logo_x = int(size * 0.75)  # Position in top right area
            logo_y = int(size * 0.1)  # Position in top right area
            
            # Triangle dimensions
            triangle_height = int(logo_size * 0.8)
            triangle_width = int(logo_size * 0.8)
            
            # Draw the triangular logo inspired by ETHCC
            # Top triangle (blue)
            top_triangle = [
                (logo_x + triangle_width//2, logo_y),
                (logo_x + triangle_width, logo_y + triangle_height),
                (logo_x, logo_y + triangle_height)
            ]
            draw.polygon(top_triangle, fill=(0, 155, 208, 220))  # ETHCC blue
            
            # Bottom triangle (teal)
            bottom_triangle = [
                (logo_x, logo_y + triangle_height - triangle_height//3),
                (logo_x + triangle_width, logo_y + triangle_height - triangle_height//3),
                (logo_x + triangle_width//2, logo_y + triangle_height*2 - triangle_height//3)
            ]
            draw.polygon(bottom_triangle, fill=(42, 206, 204, 220))  # ETHCC teal
            
            # Add logo outline for better visibility
            draw.line(top_triangle + [top_triangle[0]], fill=(255, 255, 255, 180), width=3)
            draw.line(bottom_triangle + [bottom_triangle[0]], fill=(255, 255, 255, 180), width=3)
            
            # Add "ETHCC" text below logo if space allows
            if not event_name:
                ethcc_text = "ETHCC"
                ethcc_font = username_font
                bbox = draw.textbbox((0, 0), ethcc_text, font=ethcc_font)
                ethcc_width = bbox[2] - bbox[0]
                ethcc_x = logo_x + triangle_width//2 - ethcc_width//2
                ethcc_y = logo_y + triangle_height*2 + 10
                
                # Draw ETHCC text with shadow
                for offset in range(3, 0, -1):
                    shadow_alpha = int(100 * offset / 3)
                    draw.text((ethcc_x + offset, ethcc_y + offset), ethcc_text, 
                             fill=(0, 0, 0, shadow_alpha), font=ethcc_font)
                draw.text((ethcc_x, ethcc_y), ethcc_text, fill=(255, 255, 255, 220), font=ethcc_font)
            
        # Convert back to RGB for saving
        canvas = canvas.convert('RGB')
        
        return canvas
    except Exception as e:
        logger.error(f"Error creating themed QR code: {e}")
        return None

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database helper functions
def db_user_to_profile(db_user):
    """Convert database user format to bot profile format"""
    if not db_user:
        return None
    
    # Handle created_at field - could be string or datetime object
    created_at_str = None
    if db_user.get('created_at'):
        created_at = db_user['created_at']
        if hasattr(created_at, 'isoformat'):
            created_at_str = created_at.isoformat()
        else:
            created_at_str = str(created_at)
    
    return {
        'user_id': db_user['user_id'],
        'name': db_user['display_name'] or 'Unknown',
        'username': db_user['username'] or 'unknown',
        'role': db_user['role'] or 'Not specified',
        'project': db_user['project_name'] or 'Unknown Project',
        'bio': db_user['description'] or 'WeMeetAI User',
        'telegram_id': db_user['tg_id'],
        'profile_image_url': db_user.get('profile_image_url'),
        'created_at': created_at_str
    }

def profile_to_db_user(profile, tg_id):
    """Convert bot profile format to database user format"""
    return {
        'tg_id': tg_id,
        'username': profile.get('username'),
        'display_name': profile.get('name'),
        'project_name': profile.get('project'),
        'role': profile.get('role'),
        'description': profile.get('bio'),
        'profile_image_url': profile.get('profile_image_url')
    }

async def get_user_profile(tg_id):
    """Get user profile from database"""
    try:
        result = api_client.get_user_by_tg_id(tg_id)
        if result and 'user' in result:
            return db_user_to_profile(result['user'])
        return None
    except Exception as e:
        logger.error(f"Error getting user profile from API: {e}")
        return None

async def create_or_update_user_profile(tg_id, profile_data):
    """Create or update user profile in database"""
    try:
        # Check if user exists
        existing_user = await get_user_profile(tg_id)
        
        if existing_user:
            # Update existing user
            user_id = existing_user['user_id']
            update_data = profile_to_db_user(profile_data, tg_id)
            # Remove tg_id from update data as it shouldn't be updated
            update_data.pop('tg_id', None)
            result = api_client.update_user(user_id, **update_data)
            return result is not None
        else:
            # Create new user
            create_data = profile_to_db_user(profile_data, tg_id)
            logger.info(f"Creating user with data: {create_data}")
            result = api_client.create_user(**create_data)
            return result is not None and 'user_id' in result
    except Exception as e:
        logger.error(f"Error creating/updating user profile in API: {e}")
        return False

# In-memory storage for temporary data (connections will be handled differently)
connection_requests = {}
user_notes = {}

async def get_user_connections(user_id: int) -> List[Dict]:
    """Get user connections from database"""
    try:
        # Get user database ID first
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            return []
        
        db_user_id = user_profile['user_id']
        result = api_client.get_user_groups(db_user_id)
        
        if result and 'groups' in result:
            # Convert to connection format
            connections = []
            for group in result['groups']:
                if group['other_user']:
                    connection = {
                        'user_id': group['other_user']['user_id'],
                        'tg_id': group['other_user']['tg_id'],
                        'name': group['other_user']['display_name'],
                        'username': group['other_user']['username'],
                        'role': group['other_user']['role'],
                        'project': group['other_user']['project_name'],
                        'bio': group['other_user']['description'],
                        'group_id': group['group_id'],
                        'group_link': group['group_link'],
                        'event_name': group['event_name']
                    }
                    connections.append(connection)
            return connections
        
        return []
    except Exception as e:
        logger.error(f"Error getting user connections from database: {e}")
        return []

async def create_connection_in_database(user_id: int, target_user_id: int, group_link: str = None, event_name: str = "ETH Cannes") -> bool:
    """Create a connection by storing a group in the database"""
    try:
        # Get user database IDs
        user_profile = await get_user_profile(user_id)
        target_profile = await get_user_profile(target_user_id)
        
        if not user_profile or not target_profile:
            logger.error(f"Could not find profiles for users {user_id} and {target_user_id}")
            return False
        
        db_user_id = user_profile['user_id']
        db_target_user_id = target_profile['user_id']
        
        # Use placeholder only when no link is provided
        final_link = group_link
        if final_link is None:
            final_link = "https://t.me/linkup_temp"
            
        logger.info(f"Creating connection with link: {final_link}")
        
        # Create group in database
        result = api_client.create_group(
            group_link=final_link,
            user1_id=db_user_id,
            user2_id=db_target_user_id,
            event_name=event_name
        )
        
        if result and 'group_id' in result:
            logger.info(f"Created connection group {result['group_id']} between users {user_id} and {target_user_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error creating connection in database: {e}")
        return False

async def check_connection_exists(user_id: int, target_user_id: int) -> bool:
    """Check if connection exists between two users"""
    try:
        # First check connections in the normal direction
        connections = await get_user_connections(user_id)
        for connection in connections:
            if connection['tg_id'] == target_user_id:
                logger.info(f"Found existing connection between {user_id} and {target_user_id}")
                return True
        
        # Also check connections in the reverse direction
        # This is important because connections are bidirectional
        target_connections = await get_user_connections(target_user_id)
        for connection in target_connections:
            if connection['tg_id'] == user_id:
                logger.info(f"Found existing reverse connection between {target_user_id} and {user_id}")
                return True
                
        logger.info(f"No existing connection found between {user_id} and {target_user_id}")
        return False
    except Exception as e:
        logger.error(f"Error checking connection existence: {e}")
        return False

def escape_markdown(text):
    """Escape Telegram Markdown special characters in a string."""
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message and handle deep link parameters"""
    user_name = get_full_name(update.effective_user)
    user_id = update.effective_user.id
    safe_user_name = escape_markdown(user_name)
    # Get Telegram profile photo URL if available
    profile_image_url = None
    if update.effective_user:
        # Telegram User.photo is a UserProfilePhotos object, but not always available
        # If using python-telegram-bot v20+, you need to fetch it via get_user_profile_photos
        try:
            photos = await context.bot.get_user_profile_photos(user_id, limit=1)
            logger.info(f"Profile photos response: total_count={photos.total_count}, photos={photos.photos}")
            if photos.total_count > 0:
                # Store only the file_id instead of the full URL for security
                profile_image_url = photos.photos[0][0].file_id
                logger.info(f"Successfully fetched profile photo file_id: {profile_image_url}")
            else:
                logger.info(f"No profile photo found for user {user_id}")
        except Exception as e:
            logger.warning(f"Could not fetch profile photo: {e}")
    
    logger.info(f"Profile image file_id for user {user_id}: {profile_image_url}")
    
    # Handle deep link parameters (from QR code scan)
    if context.args and len(context.args) > 0:
        logger.info(f"Start command received with args: {context.args}")
        
        if context.args[0].startswith("user_"):
            try:
                target_user_id = int(context.args[0].replace("user_", ""))
                logger.info(f"Processing QR scan: user {user_id} scanning user {target_user_id}")
                
                # Show immediate processing message
                processing_message = await update.message.reply_text(
                    "🔍 **Processing QR Code...**\n\n"
                    "Creating your connection right away...",
                    parse_mode='Markdown'
                )
                
                # Create basic profile if user doesn't have one
                user_profile = await get_user_profile(user_id)
                if not user_profile:
                    username = update.effective_user.username or user_name.replace(' ', '').lower()
                    basic_profile = {
                        'name': user_name,
                        'username': username,
                        'role': 'Not specified',
                        'project': f"{user_name}'s Project",
                        'bio': 'WeMeetAI User',
                        'profile_image_url': profile_image_url
                    }
                    success = await create_or_update_user_profile(user_id, basic_profile)
                    if success:
                        user_profile = await get_user_profile(user_id)
                        logger.info(f"Created basic profile for scanning user {user_id}")
                    else:
                        logger.error(f"Failed to create basic profile for user {user_id}")
                        await processing_message.edit_text("❌ Failed to create your profile. Please try again.")
                        return
                
                # Check if target user exists in profiles
                target_profile = await get_user_profile(target_user_id)
                if not target_profile:
                    logger.warning(f"Target user {target_user_id} not found in profiles")
                    await processing_message.edit_text(
                        "❌ **User Not Found**\n\n"
                        "The person whose QR code you scanned hasn't set up their WeMeetAI profile yet.\n\n"
                        "Please ask them to:\n"
                        "1. Start the bot: /start\n"
                        "2. Set up their profile: /profile\n"
                        "3. Generate a new QR code: /myqr\n\n"
                        "Then you can scan their QR code to connect!"
                    )
                    return
                
                if target_user_id == user_id:
                    await processing_message.edit_text("❌ You cannot connect with yourself!")
                    return
                
                logger.info(f"Connecting {user_profile['name']} with {target_profile['name']}")
                
                # Update the processing message with user info while we check for connection
                await processing_message.edit_text(
                    f"🔍 **Processing Connection...**\n\n"
                    f"Connecting with {escape_markdown(target_profile['name'])}...\n"
                    f"Creating your networking group...",
                    parse_mode='Markdown'
                )
                
                # Check if already connected (using database instead of in-memory)
                connection_exists = await check_connection_exists(user_id, target_user_id)
                if connection_exists:
                    # Get connections to find existing group link
                    connections = await get_user_connections(user_id)
                    group_link = None
                    for connection in connections:
                        if connection['tg_id'] == target_user_id and connection.get('group_link'):
                            group_link = connection['group_link']
                            break
                    
                    # If we have a group link, show "Go to Group" button
                    if group_link:
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("🚀 Go to Group", url=group_link)],
                            [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{target_user_id}")]
                        ])
                        
                        message = f"✅ **Already Connected with {escape_markdown(target_profile['name'])}!**\n\n"
                        message += f"👤 **{escape_markdown(target_profile['name'])}**\n"
                        message += f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
                        message += f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
                        message += f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
                        message += f"You already have a group chat. Click below to go to your existing group!"
                        
                        await processing_message.edit_text(message, reply_markup=keyboard, parse_mode='Markdown')
                    else:
                        # Connected but no group link found
                        await processing_message.edit_text(
                            f"✅ **Already Connected with {escape_markdown(target_profile['name'])}!**\n\n"
                            f"You're already connected, but no group chat was found.\n"
                            f"Use /creategroup {target_user_id} to create a new group chat."
                        )
                    return
                
                # Create group immediately instead of showing option
                logger.info(f"Creating group immediately for users {user_id} and {target_user_id}")
                await create_and_show_group_with_message(processing_message, context, user_id, target_user_id)
                return
                
            except (ValueError, IndexError) as e:
                logger.error(f"Error processing QR scan parameter: {e}")
                await update.message.reply_text(
                    "❌ **Invalid QR Code**\n\n"
                    "The QR code you scanned doesn't seem to be a valid WeMeetAI QR code.\n\n"
                    "Please make sure you're scanning a QR code generated by this bot."
                )
                return
            except Exception as e:
                logger.error(f"Unexpected error in QR scan processing: {e}")
                await update.message.reply_text(
                    "❌ **Error Processing QR Code**\n\n"
                    "Something went wrong while processing the QR code. Please try again."
                )
                return
    
    # Normal welcome message with enhanced options
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 My QR Code", callback_data="generate_qr")],
        [InlineKeyboardButton("✏️ Update Profile", callback_data="update_profile"),
         InlineKeyboardButton("👥 My Connections", callback_data="view_connections")],
        [InlineKeyboardButton("🚀 Launch Web App", web_app=WebAppInfo(url=f"{WEBAPP_BASE_URL}"))]
    ])

    welcome_text = (
        f"🎉 Welcome to WeMeetAI, {escape_markdown(user_name)}!\n\n"
        "Your personal networking assistant for events.\n\n"


        "Use the buttons below for fast access to common features!"
    )
    await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Profile setup"""
    await update.message.reply_text(
        "Send your profile in format:\n"
        "`Name | Role | Project | Bio`\n\n"
        "Example: `John Doe | VC | TechFund | Looking for AI startups`",
        parse_mode='Markdown'
    )
    context.user_data['awaiting_profile'] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile input and other text messages"""
    if context.user_data.get('awaiting_profile'):
        # Handle profile update
        text = update.message.text.strip()
        parts = [part.strip() for part in text.split('|')]
        
        if len(parts) == 4:
            name, role, project, bio = parts
            user_id = update.effective_user.id
            # Try to get Telegram profile photo URL
            profile_image_url = None
            if update.effective_user:
                try:
                    photos = await context.bot.get_user_profile_photos(user_id, limit=1)
                    if photos.total_count > 0:
                        file = await context.bot.get_file(photos.photos[0][0].file_id)
                        profile_image_url = file.file_path
                except Exception as e:
                    logger.warning(f"Could not fetch profile photo: {e}")
            profile_data = {
                'name': name,
                'username': update.effective_user.username or name.replace(' ', '').lower(),
                'role': role,
                'project': project,
                'bio': bio,
                'profile_image_url': profile_image_url
            }
            success = await create_or_update_user_profile(user_id, profile_data)
            
            if success:
                await update.message.reply_text(
                    f"✅ **Profile Updated!**\n\n"
                    f"👤 **Name:** {escape_markdown(name)}\n"
                    f"🏢 **Role:** {escape_markdown(role)}\n"
                    f"🚀 **Project:** {escape_markdown(project)}\n"
                    f"💬 **Bio:** {escape_markdown(bio)}\n\n"
                    f"Perfect! You can now generate QR codes and start networking.",
                    parse_mode='Markdown'
                )
                context.user_data['awaiting_profile'] = False
            else:
                await update.message.reply_text(
                    "❌ **Failed to update profile**\n\n"
                    "There was an error saving your profile. Please try again."
                )
        else:
            await update.message.reply_text(
                "❌ Invalid format. Please use:\n\n"
                "**Name | Role | Project | Bio**\n\n"
                "Example:\n"
                "`John Doe | VC | TechFund | Looking for AI startups`",
                parse_mode='Markdown'
            )
    else:
        # If user presses the persistent Start button, show available commands
        if update.message.text.strip().lower() == "start":
            menu_text = """
🎉 Welcome to WeMeetAI!

Your personal networking assistant for events.

📱 *Quick Actions:*
Use the buttons below for fast access to common features!
            """
            await update.message.reply_text(menu_text, parse_mode='Markdown')
            return
        # ... existing code ...

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code (works with or without full profile)"""
    user_id = update.effective_user.id
    user_name = get_full_name(update.effective_user)
    
    # Create basic profile if user doesn't have one
    profile = await get_user_profile(user_id)
    if not profile:
        username = update.effective_user.username or user_name.replace(' ', '').lower()
        basic_profile = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'WeMeetAI User',
            'profile_image_url': profile_image_url
        }
        success = await create_or_update_user_profile(user_id, basic_profile)
        if success:
            profile = await get_user_profile(user_id)
        else:
            await update.message.reply_text("❌ Failed to create your profile. Please try again.")
            return
    
    # Use Telegram deep link format that works with all QR scanners
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        # Fallback to user ID only
        qr_data = f"LinkUp://user/{user_id}"
    
    try:
        # Use the card-style QR code generator
        username = profile.get('username', user_name.replace(' ', '').lower())
        card_qr = create_card_style_qr(qr_data, username)
        
        if card_qr:
            bio = io.BytesIO()
            card_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"📱 **Your ETHCC QR Card**\n\n"
            caption += f"👤 **Your Profile:**\n"
            caption += f"{escape_markdown(profile['name'])} | {escape_markdown(profile['role'])} | {escape_markdown(profile['project'])}\n"
            caption += f"{escape_markdown(profile['bio'])}\n\n"
            caption += f"💡 **Tip:** Show this QR card at events to connect with others!"
            
            await update.message.reply_photo(
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            # Fallback to simple QR if card generation fails
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            bio = io.BytesIO()
            qr_image.save(bio, format='PNG')
            bio.seek(0)
            
            # Send QR code image
            await update.message.reply_photo(
                photo=bio,
                caption=f"📱 **Your QR Code**\n\n"
                       f"👤 **Your Profile:**\n"
                       f"{escape_markdown(profile['name'])} | {escape_markdown(profile['role'])} | {escape_markdown(profile['project'])}\n"
                       f"{escape_markdown(profile['bio'])}\n\n"
                       f"💡 **Your QR code is ready to share!**",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        # Fallback to text
        await update.message.reply_text(
            f"📱 Your QR Code:\n\n"
            f"`{qr_data}`\n\n"
            f"👤 Your Profile:\n"
            f"{escape_markdown(profile['name'])} | {escape_markdown(profile['role'])} | {escape_markdown(profile['project'])}\n"
            f"{escape_markdown(profile['bio'])}", 
            parse_mode='Markdown'
        )

async def generate_themed_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a themed, personalized QR code"""
    user_id = update.effective_user.id
    user_name = get_full_name(update.effective_user)
    
    # Create basic profile if user doesn't have one
    profile = await get_user_profile(user_id)
    if not profile:
        username = update.effective_user.username or user_name.replace(' ', '').lower()
        basic_profile = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'WeMeetAI User',
            'profile_image_url': profile_image_url
        }
        success = await create_or_update_user_profile(user_id, basic_profile)
        if success:
            profile = await get_user_profile(user_id)
        else:
            await update.message.reply_text("❌ Failed to create your profile. Please try again.")
            return
    
    # Parse command arguments
    event_name = None
    theme = 'ethcc'  # Default theme
    
    if context.args:
        for arg in context.args:
            if arg.startswith('event:'):
                event_name = arg.replace('event:', '').strip()
            elif arg.startswith('theme:'):
                theme = arg.replace('theme:', '').strip().lower()
    
    # Validate theme
    if theme not in QR_THEMES:
        available_themes = ', '.join(QR_THEMES.keys())
        await update.message.reply_text(
            f"❌ **Invalid theme:** `{theme}`\n\n"
            f"**Available themes:** {available_themes}\n\n"
            f"**Use /myqr for ETHCC-themed QR codes**",
            parse_mode='Markdown'
        )
        return
    
    # Get QR data
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        qr_data = f"LinkUp://user/{user_id}"
    
    # Generate username for QR
    username = profile.get('username', profile['name'].replace(' ', '').lower())
    
    await update.message.reply_text("🎨 **Creating your themed QR code...** ⏳")
    
    try:
        # Create themed QR
        themed_qr = create_themed_qr(qr_data, username, event_name, theme)
        
        if themed_qr:
            bio = io.BytesIO()
            themed_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"🎨 **Your Themed QR Code**\n\n"
            if event_name:
                caption += f"🎪 **Event:** {escape_markdown(event_name.upper())}\n"
            caption += f"🎯 **Theme:** {escape_markdown(theme.title())}\n"
            caption += f"👤 **Profile:** {escape_markdown(profile['name'])}\n"
            caption += f"🏢 **Role:** {escape_markdown(profile['role'])}\n"
            caption += f"🚀 **Project:** {escape_markdown(profile['project'])}\n\n"
            caption += f"💡 **Show this personalized QR code at events to stand out!**\n\n"
            caption += f"🎨 **ETHCC Official Theme**"
            
            await update.message.reply_photo(
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Delete the generating message
            await update.message.delete()
        else:
            # Fallback if themed QR creation fails
            await update.message.reply_text(
                "❌ **Themed QR creation failed**\n\n"
                "Use `/myqr` for a basic QR code instead."
            )
            
    except Exception as e:
        logger.error(f"Themed QR code generation failed: {e}")
        await update.message.reply_text(
            "❌ **Themed QR creation failed**\n\n"
            f"Error: {str(e)}\n\n"
            "Use `/myqr` for a basic QR code instead."
        )

async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle QR code scan"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "📱 **QR Code Scanner**\n\n"
            "Usage: `/scan [QR_CODE_DATA]`\n\n"
            "Examples:\n"
            "• `/scan https://t.me/your_bot?start=user_5094393032`\n"
            "• `/scan LinkUp://user/5094393032`\n"
            "• `/scan 5094393032` (just the user ID)\n\n"
            "💡 **In a real app, this would use your camera to scan QR codes automatically!**"
        )
        return
    
    qr_input = ' '.join(context.args)
    
    # Show immediate processing message
    processing_message = await update.message.reply_text(
        "🔍 **Processing QR Code...**\n\n"
        "Creating your connection right away...",
        parse_mode='Markdown'
    )
    
    # Extract user ID from QR code
    target_user_id = None
    
    if qr_input.startswith("LinkUp://user/"):
        try:
            target_user_id = int(qr_input.replace("LinkUp://user/", ""))
        except ValueError:
            await processing_message.edit_text("❌ Invalid QR code format")
            return
    elif "?start=user_" in qr_input:
        # Handle Telegram deep link format
        try:
            start_param = qr_input.split("?start=user_")[1]
            target_user_id = int(start_param)
        except (IndexError, ValueError):
            await processing_message.edit_text("❌ Invalid QR code format")
            return
    else:
        # Try to parse as direct user ID
        try:
            target_user_id = int(qr_input)
        except ValueError:
            await processing_message.edit_text("❌ Invalid QR code format")
            return
    
    # Check if target user exists
    target_profile = await get_user_profile(target_user_id)
    if not target_profile:
        await processing_message.edit_text("❌ User not found or hasn't set up profile")
        return
    
    if target_user_id == user_id:
        await processing_message.edit_text("❌ You cannot connect with yourself!")
        return
    
    # Update the processing message with user info while we check for connection
    await processing_message.edit_text(
        f"🔍 **Processing Connection...**\n\n"
        f"Connecting with {escape_markdown(target_profile['name'])}...\n"
        f"Creating your networking group...",
        parse_mode='Markdown'
    )
    
    # Check if already connected
    connection_exists = await check_connection_exists(user_id, target_user_id)
    if connection_exists:
        # Get connections to find existing group link
        connections = await get_user_connections(user_id)
        group_link = None
        for connection in connections:
            if connection['tg_id'] == target_user_id and connection.get('group_link'):
                group_link = connection['group_link']
                break
        
        # If we have a group link, show "Go to Group" button
        if group_link:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Go to Group", url=group_link)],
                [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{target_user_id}")]
            ])
            
            message = f"✅ **Already Connected with {escape_markdown(target_profile['name'])}!**\n\n"
            message += f"👤 **{escape_markdown(target_profile['name'])}**\n"
            message += f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
            message += f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
            message += f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
            message += f"You already have a group chat. Click below to go to your existing group!"
            
            await processing_message.edit_text(message, reply_markup=keyboard, parse_mode='Markdown')
        else:
            # Connected but no group link found
            await processing_message.edit_text(
                f"✅ **Already Connected with {escape_markdown(target_profile['name'])}!**\n\n"
                f"You're already connected, but no group chat was found.\n"
                f"Use /creategroup {target_user_id} to create a new group chat."
            )
        return
    
    # Create group immediately
    await create_and_show_group_with_message(processing_message, context, user_id, target_user_id)

async def create_and_show_group_with_message(processing_message, context, user_id: int, target_user_id: int):
    """Create Telegram group immediately when users scan QR codes and show join buttons, using existing message"""
    user_profile = await get_user_profile(user_id)
    target_profile = await get_user_profile(target_user_id)
    
    if not user_profile or not target_profile:
        await processing_message.edit_text("❌ Error retrieving user profiles. Please try again.")
        return
    
    # Limit each name to 22 characters, add '...' if longer
    def short_name(name):
        return name if len(name) <= 22 else name[:22] + '...'
    user_name_short = short_name(user_profile['name'])
    target_name_short = short_name(target_profile['name'])
    # Create group title and description
    group_title = f"🤝 {user_name_short} ↔ {target_name_short}"
    group_description = f"WeMeetAI networking group for {user_profile['name']} ({user_profile['role']}) and {target_profile['name']} ({target_profile['role']})"
    
    try:
        # Create empty group with Telegram API
        if telegram_api.is_initialized:
            # Create empty group and get invite link
            group_info = await telegram_api.create_group(
                group_title=group_title,
                description=group_description
            )
            
            if not group_info or not group_info.get('invite_link'):
                logger.error("Failed to create Telegram group or get invite link")
                raise Exception("Telegram group creation failed")
            
            # Get user database IDs for database connection
            db_user_id = user_profile['user_id']
            db_target_user_id = target_profile['user_id']
            
            # Create the connection in database with real group link
            result = api_client.create_group(
                group_link=group_info['invite_link'],
                user1_id=db_user_id,
                user2_id=db_target_user_id,
                event_name="ETH Cannes"
            )
            
            if result and 'group_id' in result:
                logger.info(f"Created connection group {result['group_id']} between users {user_id} and {target_user_id}")
                
                # Show join button to scanning user
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Join Group", url=group_info['invite_link'])],
                    [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{target_user_id}")]
                ])
                
                success_message = f"🎉 **Group Created Successfully!**\n\n"
                success_message += f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                success_message += f"**Members:** {group_info['member_count']}\n\n"
                success_message += f"**Instructions:**\n"
                success_message += f"1. Click the button below to join\n"
                success_message += f"2. {escape_markdown(target_profile['name'])} will receive their invite link\n"
                success_message += f"3. Start networking! 🚀\n\n"
                success_message += f"💡 **This group is private and secure**"
                
                await context.bot.send_message(
                    chat_id=processing_message.chat_id,
                    text=success_message,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                # Send join button to target user
                try:
                    target_keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("🚀 Join Group", url=group_info['invite_link'])],
                        [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{user_id}")]
                    ])
                    
                    target_message = f"🎉 **New Connection from {escape_markdown(user_profile['name'])}!**\n\n"
                    target_message += f"👤 **{escape_markdown(user_profile['name'])}**\n"
                    target_message += f"🏢 **Role:** {escape_markdown(user_profile['role'])}\n"
                    target_message += f"🚀 **Project:** {escape_markdown(user_profile['project'])}\n"
                    target_message += f"💬 **Bio:** {escape_markdown(user_profile['bio'])}\n\n"
                    target_message += f"A group has been created! Click below to join."
                    
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=target_message,
                        reply_markup=target_keyboard,
                        parse_mode='Markdown'
                    )
                    logger.info(f"Sent group join link to user {target_user_id}")
                except Exception as e:
                    logger.error(f"Failed to send group join link to user {target_user_id}: {e}")
                
                return  # Successfully created group
            else:
                logger.error("Failed to create database connection")
                raise Exception("Database connection creation failed")
        
        # Fallback if API fails
        raise Exception("Telegram API group creation failed")
        
    except Exception as e:
        logger.error(f"Group creation failed: {e}")
        
        # Fallback to connection without auto group
        await processing_message.edit_text(
            f"🎉 **Connected with {escape_markdown(target_profile['name'])}!**\n\n"
            f"👤 **{escape_markdown(target_profile['name'])}**\n"
            f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
            f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
            f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
            f"❌ **Automatic group creation failed**\n\n"
            f"Use /creategroup {target_user_id} to try creating a group manually."
        )
        
        # Still notify the target user about the connection
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎉 **New Connection from {escape_markdown(user_profile['name'])}!**\n\n"
                     f"👤 **{escape_markdown(user_profile['name'])}**\n"
                     f"🏢 **Role:** {escape_markdown(user_profile['role'])}\n"
                     f"🚀 **Project:** {escape_markdown(user_profile['project'])}\n"
                     f"💬 **Bio:** {escape_markdown(user_profile['bio'])}\n\n"
                     f"You've been connected! Use /myconnections to see all your connections."
            )
        except Exception as e:
            logger.error(f"Failed to notify target user {target_user_id}: {e}")

async def generate_qr_from_callback(query, context):
    """Generate QR code from callback query"""
    user_id = query.from_user.id
    user_name = get_full_name(query.from_user)
    
    # Get user profile
    profile = await get_user_profile(user_id)
    
    if not profile:
        # Create basic profile if user doesn't exist
        username = query.from_user.username or user_name.replace(' ', '').lower()
        
        # Get Telegram profile photo URL if available
        profile_image_url = None
        if query.from_user:
            try:
                photos = await context.bot.get_user_profile_photos(user_id, limit=1)
                logger.info(f"Profile photos response: total_count={photos.total_count}, photos={photos.photos}")
                if photos.total_count > 0:
                    # Store only the file_id instead of the full URL for security
                    profile_image_url = photos.photos[0][0].file_id
                    logger.info(f"Successfully fetched profile photo file_id: {profile_image_url}")
                else:
                    logger.info(f"No profile photo found for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not fetch profile photo: {e}")
        
        logger.info(f"Profile image file_id for user {user_id}: {profile_image_url}")
        
        basic_profile = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'WeMeetAI User',
            'profile_image_url': profile_image_url
        }
        success = await create_or_update_user_profile(user_id, basic_profile)
        if success:
            profile = await get_user_profile(user_id)
        else:
            await query.edit_message_text("❌ Failed to create your profile. Please try again.")
            return
    
    # Get QR data
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        # Fallback to user ID only
        qr_data = f"LinkUp://user/{user_id}"
    
    # Show "generating" message
    await query.edit_message_text("�� **Creating your QR card...** ⏳")
    
    try:
        # Use the card-style QR code generator
        username = profile.get('username', user_name.replace(' ', '').lower())
        card_qr = create_card_style_qr(qr_data, username)
        
        if card_qr:
            bio = io.BytesIO()
            card_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"📱 **Your ETHCC QR Card**\n\n"
            caption += f"👤 **Your Profile:**\n"
            caption += f"{escape_markdown(profile['name'])} | {escape_markdown(profile['role'])} | {escape_markdown(profile['project'])}\n"
            caption += f"{escape_markdown(profile['bio'])}\n\n"
            caption += f"💡 **Tip:** Show this QR card at events to connect with others!"
            
            # Send as new message to preserve quality
            await context.bot.send_photo(
                chat_id=user_id,
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Update the original message to show success
            await query.edit_message_text("✅ **Your QR card has been generated!** Check your messages.", parse_mode='Markdown')
            
        else:
            # Fallback to basic QR if card generation fails
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            bio = io.BytesIO()
            qr_image.save(bio, format='PNG')
            bio.seek(0)
            
            caption = f"📱 **Your QR Code**\n\n"
            caption += f"👤 **Your Profile:**\n"
            caption += f"{profile['name']} | {profile['role']} | {profile['project']}\n"
            caption += f"{profile['bio']}"
            
            # Send as new message
            await context.bot.send_photo(
                chat_id=user_id,
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Update original message
            await query.edit_message_text("✅ **Your QR code has been generated!** Check your messages.", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"QR code generation from callback failed: {e}")
        await query.edit_message_text(
            "❌ **QR Code generation failed**\n\n"
            "Please try the /myqr command instead."
        )
# QR color options
QR_COLORS = {
    'blue': (0, 155, 208),  # ETH Cannes blue
    'purple': (147, 51, 234),  # Vibrant purple
    'orange': (251, 146, 60),  # Vibrant orange
    'green': (34, 197, 94),  # Vibrant green
    'red': (239, 68, 68),  # Vibrant red
}


async def show_themed_qr_menu(query, context):
    """Show themed QR code menu"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Blue QR", callback_data="qr_color_blue")],
        [InlineKeyboardButton("🟣 Purple QR", callback_data="qr_color_purple"),
         InlineKeyboardButton("🟠 Orange QR", callback_data="qr_color_orange")],
        [InlineKeyboardButton("🟢 Green QR", callback_data="qr_color_green"),
         InlineKeyboardButton("🔴 Red QR", callback_data="qr_color_red")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
    ])
    
    await query.edit_message_text(
        "🎨 **Choose Your QR Color**\n\n"
        "Select a color for your ETHCC QR code:\n\n"
        "🔵 **Blue** - ETH Cannes official blue\n"
        "🟣 **Purple** - Vibrant purple\n"
        "🟠 **Orange** - Vibrant orange\n"
        "🟢 **Green** - Vibrant green\n"
        "🔴 **Red** - Vibrant red\n\n"
        "💡 **Tip:** Share your QR code at events to connect!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Callback received: {query.data}")
    
    # Handle QR code generation
    if query.data == "generate_qr":
        await generate_qr_from_callback(query, context)
        return
    
    # Handle QR color selection
    elif query.data.startswith("qr_color_"):
        color_name = query.data.replace("qr_color_", "")
        await generate_qr_with_color(query, context, color_name)
        return
    
    # Handle profile update
    elif query.data == "update_profile":
        await update_profile_from_callback(query, context)
        return
    
    # Handle view connections
    elif query.data == "view_connections":
        user_id = query.from_user.id
        connections = await get_user_connections(user_id)
        
        if not connections:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="📭 **No connections yet**\n\n"
                     "Scan QR codes at events to connect with others!\n\n"
                     "Generate your own QR code with /myqr and share it.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📱 Get My QR", callback_data="generate_qr"),
                    InlineKeyboardButton("◀️ Back", callback_data="back_to_start")
                ]])
            )
            return
        
        # Build connections message
        connection_list = "🤝 *Your Connections:*\n\n"
        for i, connection in enumerate(connections, 1):
            username = connection.get('username', '')
            if username:
                name_display = f"[{escape_markdown(connection['name'])}](https://t.me/{username})"
            else:
                name_display = f"{escape_markdown(connection['name'])}"
            # Only show role if it's available and not empty
            if connection.get('role') and connection['role'].strip() and connection['role'] != 'Not specified':
                connection_list += f"{i}. {name_display} - {escape_markdown(connection['role'])} - {escape_markdown(connection['project'])}\n"
            else:
                connection_list += f"{i}. {name_display} - {escape_markdown(connection['project'])}\n"
            # Show group chat as a Markdown link if available
            if connection.get('group_link'):
                group_link = connection['group_link']
                connection_list += f"   👥 [Group Chat]({group_link})\n"
            if connection.get('event_name'):
                connection_list += f"   📍 Event: {escape_markdown(connection['event_name'])}\n"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=connection_list,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        return
        
    # Handle create group menu
    elif query.data == "create_group_menu":
        user_id = query.from_user.id
        connections = await get_user_connections(user_id)
        
        if not connections:
            await query.edit_message_text(
                "📭 **No connections found!**\n\n"
                "You need to connect with someone first before creating a group.\n"
                "Use /myqr to share your QR code and connect with others!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Back", callback_data="view_connections")
                ]])
            )
            return
        
        # Build connection list for group creation
        message = "👥 **Create Group with Connections**\n\n"
        message += "Select connections to add to your group:\n\n"
        
        group_buttons = []
        for i, connection in enumerate(connections, 1):
            # Only show role if it's available and not empty
            if connection.get('role') and connection['role'].strip() and connection['role'] != 'Not specified':
                message += f"{i}. **{escape_markdown(connection['name'])}** - {escape_markdown(connection['role'])}\n"
            else:
                message += f"{i}. **{escape_markdown(connection['name'])}** - {escape_markdown(connection['project'])}\n"
            
            # Create button for each connection
            group_buttons.append([
                InlineKeyboardButton(
                    f"➕ {connection['name']}",
                    callback_data=f"create_group_{connection['tg_id']}"
                )
            ])
        
        # Add back button
        group_buttons.append([
            InlineKeyboardButton("◀️ Back", callback_data="view_connections")
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(group_buttons),
            parse_mode='Markdown'
        )
        return
    
    elif query.data.startswith("view_profile_"):
        # Handle profile viewing
        target_user_id = int(query.data.replace("view_profile_", ""))
        await view_user_profile(query, context, target_user_id, send_new_message=True)
        return
    
    elif query.data == "back_to_start":
        # Handle back to start menu
        user_name = get_full_name(query.from_user)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 My QR Code", callback_data="generate_qr")],
            [InlineKeyboardButton("✏️ Update Profile", callback_data="update_profile"),
             InlineKeyboardButton("👥 My Connections", callback_data="view_connections")],
            [InlineKeyboardButton("🚀 Launch Web App", web_app=WebAppInfo(url=f"{WEBAPP_BASE_URL}/react-webapp/build/"))]
        ])
        
        welcome_text = (
            f"🎉 Welcome to WeMeetAI, {escape_markdown(user_name)}!\n\n"
            "Your personal networking assistant for events.\n\n"
 

            "📱 *Quick Actions:*\n"
            "Use the buttons below for fast access to common features!"
        )
        await query.edit_message_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')
        return
        
    elif query.data.startswith("create_group_"):
        # Handle auto group creation using actual Telegram API
        target_user_id = int(query.data.replace("create_group_", ""))
        user_id = query.from_user.id
        
        user_profile = await get_user_profile(user_id)
        target_profile = await get_user_profile(target_user_id)
        
        if not user_profile or not target_profile:
            await query.edit_message_text("❌ Error retrieving user profiles. Please try again.")
            return
        
        try:
            # Create actual Telegram group using Telegram API (pyrogram)
            group_title = f"🤝 {user_profile['name']} ↔ {target_profile['name']}"
            group_description = f"Networking group for {user_profile['name']} ({user_profile['role']}) and {target_profile['name']} ({target_profile['role']})"
            
            # Show progress
            await query.edit_message_text("🏗️ **Creating your networking group...** ⏳")
            
            # Use the Telegram API client to create group
            if telegram_api.is_initialized:
                group_info = await telegram_api.create_group(
                    group_title=group_title,
                    user_ids=[target_user_id,user_id],
                    description=group_description
                )
                
                if group_info:
                    # Group created successfully - Send invite links via BOT
                    success_message = f"🎉 **Group Created Successfully!**\n\n"
                    success_message += f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                    success_message += f"**Members:** {group_info['member_count']}\n"
                    success_message += f"**Invite Link:** {group_info['invite_link']}\n\n"
                    success_message += f"**Instructions:**\n"
                    success_message += f"1. Click the link above to join\n"
                    success_message += f"2. {escape_markdown(target_profile['name'])} will receive their invite link\n"
                    success_message += f"3. Start networking! 🚀\n\n"
                    success_message += f"💡 **This group is private and secure**"
                    
                    await query.edit_message_text(success_message)
                    
                    # Send invite link to the target user
                    try:
                        await telegram_api.send_group_invite(
                            user_id=target_user_id,
                            group_info=group_info,
                            sender_name=user_profile['name']
                        )
                    except Exception as notify_error:
                        logger.error(f"Could not send invite to target user: {notify_error}")
                        # Fallback: send via bot
                        try:
                            await context.bot.send_message(
                                chat_id=target_user_id,
                                text=f"🎉 **You've been invited to a networking group!**\n\n"
                                     f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                                     f"**Created by:** {escape_markdown(user_profile['name'])} ({escape_markdown(user_profile['role'])})\n\n"
                                     f"🔗 **Join here:** {group_info['invite_link']}\n\n"
                                     f"💡 **About {escape_markdown(user_profile['name'])}:**\n"
                                     f"🏢 Role: {escape_markdown(user_profile['role'])}\n"
                                     f"🚀 Project: {escape_markdown(user_profile['project'])}\n"
                                     f"💬 Bio: {escape_markdown(user_profile['bio'])}\n\n"
                                     f"Click the link to join and start networking! 🚀\n\n"
                                     f"💾 **This connection is saved in your WeMeetAI profile.**"
                            )
                        except Exception as bot_error:
                            logger.error(f"Failed to send bot message to user {target_user_id}: {bot_error}")
                    
                    return  # Successfully created group, exit function
                
                # If we get here, group creation failed
                raise Exception("Telegram API group creation failed")
            
        except Exception as e:
            logger.error(f"Group creation failed: {e}")
            
            # Fallback to manual instructions if API fails
            fallback_message = f"❌ **Auto group creation failed**\n\n"
            fallback_message += f"Don't worry! Here are manual instructions:\n\n"
            fallback_message += f"**Group Name:** {group_title}\n\n"
            fallback_message += f"**Manual Setup:**\n"
            fallback_message += f"1. Create new group in Telegram\n"
            fallback_message += f"2. Add: {target_profile['name']}\n"
            fallback_message += f"3. Set name: {group_title}\n"
            fallback_message += f"4. Start networking! 🚀\n\n"
            fallback_message += f"💡 **Alternative:** Use the buttons below"
            
            # Create inline keyboard with working alternatives
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Share Contact Info", callback_data=f"share_contact_{target_user_id}")],
                [InlineKeyboardButton("💬 Start Direct Chat", url=f"tg://user?id={target_user_id}")]
            ])
            
            await query.edit_message_text(fallback_message, reply_markup=keyboard)
        
    elif query.data.startswith("manual_setup_"):
        # Handle manual setup instructions (kept as fallback)
        target_user_id = int(query.data.replace("manual_setup_", ""))
        user_id = query.from_user.id
        
        user_profile = await get_user_profile(user_id)
        target_profile = await get_user_profile(target_user_id)
        
        if not user_profile or not target_profile:
            await query.edit_message_text("❌ Error retrieving user profiles. Please try again.")
            return
        group_title = f"🤝 {user_profile['name']} ↔ {target_profile['name']}"
        
        manual_instructions = f"📋 **Manual Group Setup Guide**\n\n"
        manual_instructions += f"**Group Name:** {group_title}\n\n"
        manual_instructions += f"**Step-by-step instructions:**\n"
        manual_instructions += f"1️⃣ Open Telegram\n"
        manual_instructions += f"2️⃣ Tap 'New Group'\n"
        manual_instructions += f"3️⃣ Add contacts:\n"
        manual_instructions += f"   • Search for: {target_profile['name']}\n"
        manual_instructions += f"   • Or username: @{target_profile.get('username', 'user')}\n"
        manual_instructions += f"   • Or forward this message to them\n"
        manual_instructions += f"4️⃣ Set group name: {group_title}\n"
        manual_instructions += f"5️⃣ Tap 'Create' and start networking! 🚀\n\n"
        manual_instructions += f"💡 **Pro tip:** Both users will get notifications about this group!"
        
        await query.edit_message_text(manual_instructions)
        
    elif query.data.startswith("share_contact_"):
        # Handle contact sharing
        target_user_id = int(query.data.replace("share_contact_", ""))
        user_id = query.from_user.id
        
        user_profile = await get_user_profile(user_id)
        target_profile = await get_user_profile(target_user_id)
        
        if not user_profile or not target_profile:
            await query.edit_message_text("❌ Error retrieving user profiles. Please try again.")
            return
        
        contact_info = f"📞 **Contact Information Exchange**\n\n"
        contact_info += f"**Your Connection:**\n"
        contact_info += f"👤 **Name:** {target_profile['name']}\n"
        contact_info += f"🏢 **Role:** {target_profile['role']}\n"
        contact_info += f"🚀 **Project:** {target_profile['project']}\n"
        contact_info += f"💬 **Bio:** {target_profile['bio']}\n"
        contact_info += f"🆔 **Telegram ID:** `{target_user_id}`\n\n"
        contact_info += f"**To create a group:**\n"
        contact_info += f"1. Start a new group in Telegram\n"
        contact_info += f"2. Search for: {target_profile['name']}\n"
        contact_info += f"3. Or forward this message to them\n"
        contact_info += f"4. Add them to your group! 🚀"
        
        await query.edit_message_text(contact_info)
        
    elif query.data.startswith("join_group_"):
        target_user_id = int(query.data.replace("join_group_", ""))
        target_profile = await get_user_profile(target_user_id)
        # Find group link for this connection
        user_id = query.from_user.id
        connections = await get_user_connections(user_id)
        group_link = None
        for connection in connections:
            if connection['tg_id'] == target_user_id and connection.get('group_link'):
                group_link = connection['group_link']
                break
        success_message = (
            f"✅ **Group Joined Successfully!**\n\n"
            f"You can now chat in your group with **{escape_markdown(target_profile['name'])}**.\n\n"
            f"Click below to open the group."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 View Group", url=group_link)],
            [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{target_user_id}")]
        ])
        await query.message.reply_text(success_message, reply_markup=keyboard, parse_mode='Markdown', disable_web_page_preview=True)
        return
    
    elif query.data.startswith("view_profile_"):
        # Always send a new message for view_profile
        target_user_id = int(query.data.replace("view_profile_", ""))
        await view_user_profile(query, context, target_user_id, send_new_message=True)
        return
    
    else:
        # For any other callbacks, show instant connections message
        await query.edit_message_text(
            "🚀 **WeMeetAI now uses instant connections!**\n\n"
            "Just scan QR codes or use /connect for immediate connections.\n"
            "No more waiting for approvals! 🎉"
        )

async def list_connections(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List user connections"""
    user_id = update.effective_user.id
    
    # Get connections from database instead of in-memory storage
    connections = await get_user_connections(user_id)
    
    if not connections:
        await update.message.reply_text("📭 No connections yet")
        return
    
    connection_list = "🤝 **Your Connections:**\n\n"
    
    for i, connection in enumerate(connections, 1):
        username = connection.get('username', '')
        if username:
            name_display = f"[{escape_markdown(connection['name'])}](https://t.me/{username})"
        else:
            name_display = f"{escape_markdown(connection['name'])}"
        # Only show role if it's available and not empty
        if connection.get('role') and connection['role'].strip() and connection['role'] != 'Not specified':
            connection_list += f"{i}. {name_display} - {escape_markdown(connection['role'])} - {escape_markdown(connection['project'])}\n"
        else:
            connection_list += f"{i}. {name_display} - {escape_markdown(connection['project'])}\n"
        # Show group chat as a Markdown link if available
        if connection.get('group_link'):
            group_link = connection['group_link']
            connection_list += f"   👥 [Group Chat]({group_link})\n"
        if connection.get('event_name'):
            connection_list += f"   📍 Event: {escape_markdown(connection['event_name'])}\n"
        connection_list += "\n"
    await update.message.reply_text(connection_list, parse_mode='Markdown', disable_web_page_preview=True)

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a group with connections using Telegram API"""
    user_id = update.effective_user.id
    
    # Get connections from database instead of in-memory storage  
    connections = await get_user_connections(user_id)
    
    if not connections:
        await update.message.reply_text(
            "📭 **No connections found!**\n\n"
            "You need to connect with someone first before creating a group.\n"
            "Use /myqr to share your QR code and connect with others!"
        )
        return
    
    if not context.args:
        # Show available connections
        connection_list = "👥 **Create Group with Connections**\n\n"
        connection_list += "Available connections:\n"
        
        for i, connection in enumerate(connections, 1):
            connection_list += f"{i}. {connection['name']} (TG ID: {connection['tg_id']})\n"
        
        connection_list += f"\n💡 **Usage:** `/creategroup [tg_id1] [tg_id2] ...`\n"
        connection_list += f"**Example:** `/creategroup {connections[0]['tg_id'] if connections else 'TG_ID'}`"
        
        await update.message.reply_text(connection_list)
        return
    
    # Parse user IDs (these are telegram IDs, not database IDs)
    try:
        target_tg_ids = [int(arg) for arg in context.args]
    except ValueError:
        await update.message.reply_text("❌ Invalid user IDs. Please use numbers only.")
        return
    
    # Verify all users are connections
    connected_tg_ids = [connection['tg_id'] for connection in connections]
    for target_tg_id in target_tg_ids:
        if target_tg_id not in connected_tg_ids:
            await update.message.reply_text(f"❌ User {target_tg_id} is not in your connections.")
            return
    
    # Create group name and description
    user_profile = await get_user_profile(user_id)
    if not user_profile:
        await update.message.reply_text("❌ Your profile not found. Please set up your profile first.")
        return
    
    all_tg_ids = [user_id] + target_tg_ids
    group_members = []
    
    # Add current user
    group_members.append(f"{user_profile['name']} ({user_profile['project']})")
    
    # Add connected users
    for target_tg_id in target_tg_ids:
        for connection in connections:
            if connection['tg_id'] == target_tg_id:
                group_members.append(f"{connection['name']} ({connection['project']})")
                break
    
    group_name = f"WeMeetAI: {' & '.join(group_members[:3])}"
    if len(group_members) > 3:
        group_name += f" + {len(group_members) - 3} others"
    
    # Create group description
    group_description = f"WeMeetAI networking group created by {user_profile['name']}\n\n"
    group_description += "Members:\n"
    group_description += f"• {user_profile['name']} - {user_profile['role']} at {user_profile['project']}\n"
    for target_tg_id in target_tg_ids:
        for connection in connections:
            if connection['tg_id'] == target_tg_id:
                group_description += f"• {connection['name']} - {connection['role']} at {connection['project']}\n"
                break
    
    # Send processing message
    processing_message = await update.message.reply_text(
        "⏳ **Creating your group...**\n\n"
        f"Group: {group_name}\n"
        f"Members: {len(all_tg_ids)}\n\n"
        "This may take a few seconds..."
    )
    
    try:
        # Attempt to create group using Telegram API
        if telegram_api.is_initialized:
            logger.info(f"Attempting to create group '{group_name}' with users: {target_tg_ids}")
            
            group_info = await telegram_api.create_group(
                group_title=group_name,
                user_ids=target_tg_ids,
                description=group_description
            )
            
            if group_info:
                # Group created successfully! Now store it in database
                # Update existing connections with the new group link
                for target_tg_id in target_tg_ids:
                    connection_updated = await create_connection_in_database(
                        user_id, target_tg_id, 
                        group_link=group_info['invite_link'],
                        event_name="ETH Cannes"
                    )
                    if connection_updated:
                        logger.info(f"Updated connection with group link for users {user_id} and {target_tg_id}")
                
                success_message = f"🎉 **Group Created Successfully!**\n\n"
                success_message += f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                success_message += f"**Members:** {group_info['member_count']}\n"
                success_message += f"**Invite Link:** {group_info['invite_link']}\n\n"
                success_message += f"✅ All members have been notified and can join using the link above!\n\n"
                success_message += f"💾 **Group saved to database for future reference.**"
                
                await processing_message.edit_text(success_message)
                
                # Send invite links to all target users
                for target_tg_id in target_tg_ids:
                    try:
                        await telegram_api.send_group_invite(
                            user_id=target_tg_id,
                            group_info=group_info,
                            sender_name=user_profile['name']
                        )
                        logger.info(f"Sent group invite to user {target_tg_id}")
                    except Exception as e:
                        logger.error(f"Failed to send invite to user {target_tg_id}: {e}")
                        # Fallback: send via bot
                        try:
                            await context.bot.send_message(
                                chat_id=target_tg_id,
                                text=f"🎉 **Group Invitation**\n\n"
                                     f"{escape_markdown(user_profile['name'])} created a group: **{escape_markdown(group_info['group_title'])}**\n\n"
                                     f"🔗 **Join here:** {group_info['invite_link']}\n\n"
                                     f"💡 **About {escape_markdown(user_profile['name'])}:**\n"
                                     f"🏢 Role: {escape_markdown(user_profile['role'])}\n"
                                     f"🚀 Project: {escape_markdown(user_profile['project'])}\n"
                                     f"💬 Bio: {escape_markdown(user_profile['bio'])}\n\n"
                                     f"Click the link to join and start networking! 🚀\n\n"
                                     f"💾 **This connection is saved in your WeMeetAI profile.**"
                            )
                        except Exception as bot_e:
                            logger.error(f"Failed to send bot message to user {target_tg_id}: {bot_e}")
                
                return
            else:
                logger.warning("Telegram API group creation failed, falling back to manual instructions")
        else:
            logger.warning("Telegram API not initialized, falling back to manual instructions")
    
    except Exception as e:
        logger.error(f"Error creating group with Telegram API: {e}")
    
    # Fallback to manual instructions
    await processing_message.edit_text(
        "⚠️ **Automatic group creation unavailable**\n\n"
        "Providing manual setup instructions instead..."
    )
    
    # Provide manual group creation instructions
    instructions = f"📝 **Manual Group Creation Instructions**\n\n"
    instructions += f"**Suggested Group Name:** {escape_markdown(group_name)}\n\n"
    instructions += f"**To create the group manually:**\n"
    instructions += f"1. Create a new group in Telegram\n"
    instructions += f"2. Add these members:\n"
    
    instructions += f"   • {escape_markdown(user_profile['name'])} (@{escape_markdown(user_profile.get('username', f'UserID: {user_id}'))})\n"
    for target_tg_id in target_tg_ids:
        for connection in connections:
            if connection['tg_id'] == target_tg_id:
                username = connection.get('username', f'UserID: {target_tg_id}')
                instructions += f"   • {escape_markdown(connection['name'])} (@{escape_markdown(username)})\n"
                break
    
    instructions += f"\n3. Set group name: {escape_markdown(group_name)}\n"
    instructions += f"4. Start networking! 🚀\n\n"
    instructions += f"💡 **Tip:** Copy this message and share it with all members!"
    
    await update.message.reply_text(instructions)
    
    # Notify all target users
    for target_tg_id in target_tg_ids:
        try:
            await context.bot.send_message(
                chat_id=target_tg_id,
                text=f"👥 **Group Invitation**\n\n"
                     f"{escape_markdown(user_profile['name'])} wants to create a group:\n"
                     f"**{escape_markdown(group_name)}**\n\n"
                     f"You'll receive group creation instructions from them!"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {target_tg_id}: {e}")

async def initialize_app(application):
    """Initialize the application and Telegram API client"""
    # Initialize Telegram API client
    logger.info("Initializing Telegram API client...")
    api_success = await initialize_telegram_api()
    
    if api_success:
        logger.info("✅ Telegram API client initialized - Group creation available!")
    else:
        logger.warning("⚠️ Telegram API client failed to initialize - Using fallback mode")
    
    # Log ETHCC theme information
    logger.info("🔷 ETHCC theme active - QR codes will use ETHCC styling by default")
    print("\033[96m" + "ETHCC theme enabled! QR codes will use the official ETHCC colors and design." + "\033[0m")
    
    return api_success

async def shutdown_app(application):
    """Cleanup function"""
    logger.info("Shutting down Telegram API client...")
    await close_telegram_api()

async def launch_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Launch the web app"""
    # Use the React-based Telegram Mini App
    # Make sure to use a publicly accessible URL
    webapp_url = os.getenv("WEBAPP_BASE_URL", "https://your-domain.com")
    
    # Remove any trailing slashes
    if webapp_url.endswith('/'):
        webapp_url = webapp_url[:-1]
    
    # Log the URL being used
    logging.info(f"Launching webapp with URL: {webapp_url}")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Launch LinkUp App", web_app=WebAppInfo(url=webapp_url))]
    ])
    
    await update.message.reply_text(
        "📱 **LinkUp Web App**\n\n"
        "Click the button below to launch the LinkUp web app with a modern interface for:\n\n"
        "• Profile management\n"
        "• QR code generation\n"
        "• Connection tracking\n"
        "• Group creation\n\n"
        "The app will open directly within Telegram!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def update_profile_from_callback(query, context):
    """Handle profile update from callback"""
    await query.edit_message_text(
        "✏️ **Update Your Profile**\n\n"
        "Send your profile in format:\n"
        "`Name | Role | Project | Bio`\n\n"
        "Example: John Doe | VC | TechFund | Looking for AI startups",
        parse_mode='Markdown'
    )
    context.user_data['awaiting_profile'] = True

async def create_instant_group(query, context, target_user_id):
    """Create group immediately after QR scan"""
    user_id = query.from_user.id
    user_profile = await get_user_profile(user_id)
    target_profile = await get_user_profile(target_user_id)
    
    if not user_profile or not target_profile:
        await query.edit_message_text("❌ Error retrieving user profiles. Please try again.")
        return
    
    # Check if connection already exists
    connection_exists = await check_connection_exists(user_id, target_user_id)
    if connection_exists:
        # User already has a connection, inform them
        await query.edit_message_text(
            f"✅ **Already Connected!**\n\n"
            f"You're already connected with {escape_markdown(target_profile['name'])}.\n"
            f"Use /myconnections to see all your connections."
        )
        return
    
    # Create group name: Project (UserA) <-> Project (UserB)
    group_title = f"{user_profile['project']} <-> {target_profile['project']}"
    group_description = f"WeMeetAI networking group: {user_profile['name']} & {target_profile['name']}"
    
    await query.edit_message_text("🏗️ **Creating your networking group...** ⏳")
    
    try:
        # Use Telegram API to create empty group with invite link
        if telegram_api.is_initialized:
            # Get user database IDs for database connection
            db_user_profile = await get_user_profile(user_id)
            db_target_profile = await get_user_profile(target_user_id)
            
            if not db_user_profile or not db_target_profile:
                logger.error(f"Could not find database profiles for users {user_id} and {target_user_id}")
                raise Exception("Failed to retrieve database profiles")
            
            db_user_id = db_user_profile['user_id']
            db_target_user_id = db_target_profile['user_id']
            
            # Create empty group and get invite link
            group_info = await telegram_api.create_group(
                group_title=group_title,
                description=group_description
            )
            
            if not group_info or not group_info.get('invite_link'):
                logger.error("Failed to create Telegram group or get invite link")
                raise Exception("Telegram group creation failed")
            
            # Now create the connection in database with real group link
            result = api_client.create_group(
                group_link=group_info['invite_link'],
                user1_id=db_user_id,
                user2_id=db_target_user_id,
                event_name="ETH Cannes"
            )
            
            if result and 'group_id' in result:
                logger.info(f"Created connection group {result['group_id']} between users {user_id} and {target_user_id}")
                
                # Send response with group info
                success_message = f"🎉 **Group Created Successfully!**\n\n"
                success_message += f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                success_message += f"**Members:** {group_info['member_count']}\n\n"
                success_message += f"**Instructions:**\n"
                success_message += f"1. Click the button below to join\n"
                success_message += f"2. {escape_markdown(target_profile['name'])} will receive their invite link\n"
                success_message += f"3. Start networking! 🚀\n\n"
                success_message += f"💡 **This group is private and secure**"
                
                await query.edit_message_text(success_message)
                
                # Send invite link to target user via BOT (not API user)
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"🎉 **You've been invited to a networking group!**\n\n"
                             f"**Group:** {escape_markdown(group_info['group_title'])}\n"
                             f"**Created by:** {escape_markdown(user_profile['name'])} ({escape_markdown(user_profile['role'])})\n\n"
                             f"🔗 **Join here:** {group_info['invite_link']}\n\n"
                             f"💡 **About {escape_markdown(user_profile['name'])}:**\n"
                             f"🏢 Role: {escape_markdown(user_profile['role'])}\n"
                             f"🚀 Project: {escape_markdown(user_profile['project'])}\n"
                             f"💬 Bio: {escape_markdown(user_profile['bio'])}\n\n"
                             f"Click the link to join and start networking! 🚀\n\n"
                             f"💾 **This connection is saved in your WeMeetAI profile.**"
                    )
                    logger.info(f"Bot sent group invite to user {target_user_id}")
                except Exception as e:
                    logger.error(f"Failed to send bot invite to user {target_user_id}: {e}")
                
                return  # Successfully created group
            else:
                logger.error("Failed to create database connection")
                raise Exception("Database connection creation failed")
        
        # Fallback if API fails
        raise Exception("Telegram API group creation failed")
        
    except Exception as e:
        logger.error(f"Group creation failed: {e}")
        
        # Fallback to manual instructions
        fallback_message = f"❌ **Auto group creation failed**\n\n"
        fallback_message += f"Don't worry! Here are manual instructions:\n\n"
        fallback_message += f"**Group Name:** {group_title}\n\n"
        fallback_message += f"**Manual Setup:**\n"
        fallback_message += f"1. Create new group in Telegram\n"
        fallback_message += f"2. Add: {target_profile['name']}\n"
        fallback_message += f"3. Set name: {group_title}\n"
        fallback_message += f"4. Start networking! 🚀\n\n"
        fallback_message += f"💾 **Your connection is still saved in the database.**"
        
        await query.edit_message_text(fallback_message)

async def view_user_profile(query, context, target_user_id, send_new_message=False):
    """View user profile details"""
    target_profile = await get_user_profile(target_user_id)
    
    if not target_profile:
        await query.edit_message_text("❌ User profile not found.")
        return
    
    # Get connection info to check for group link
    user_id = query.from_user.id
    connections = await get_user_connections(user_id)
    group_link = None
    for connection in connections:
        if connection['tg_id'] == target_user_id and connection.get('group_link'):
            group_link = connection['group_link']
            break
    
    profile_message = f"👤 **Profile: {escape_markdown(target_profile['name'])}**\n\n"
    
    # Only show role if it's available and not empty
    if target_profile.get('role') and target_profile['role'].strip() and target_profile['role'] != 'Not specified':
        profile_message += f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
    
    profile_message += f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
    profile_message += f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
    
    profile_message += f"**Connected!** You can now message each other directly."
    
    # Add buttons for actions
    buttons = []
    if group_link:
        buttons.append([InlineKeyboardButton("🚀 View Group", url=group_link)])
    buttons.append([InlineKeyboardButton("◀️ Back to Connections", callback_data="view_connections")])
    keyboard = InlineKeyboardMarkup(buttons)
    
    if send_new_message:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=profile_message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            profile_message, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def create_instant_connection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, target_user_id: int):
    """Create instant connection and group between two users"""
    
    # Get profiles
    user_profile = await get_user_profile(user_id)
    target_profile = await get_user_profile(target_user_id)
    
    if not user_profile or not target_profile:
        await update.message.reply_text("❌ Error retrieving user profiles. Please try again.")
        return
    
    # Create connection in database
    connection_created = await create_connection_in_database(user_id, target_user_id, event_name="ETH Cannes")
    
    if not connection_created:
        await update.message.reply_text("❌ Failed to create connection. Please try again.")
        return
    
    # Create group name
    group_name = f"{user_profile['name']} ↔ {target_profile['name']}"
    
    # Try to create actual Telegram group automatically
    try:
        # Create group title
        group_title = f"{user_profile['name']} ↔ {target_profile['name']}"
        
        try:
            # Create an invite link approach - more reliable
            invite_link_message = f"🎉 **Instant Connection + Auto Group!**\n\n"
            invite_link_message += f"**Connected with:** {escape_markdown(target_profile['name'])}\n"
            invite_link_message += f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
            invite_link_message += f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
            invite_link_message += f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
            
            # Create a group by having the bot start a group conversation
            # This is a workaround since direct group creation has limitations
            
            # Send the invite to create the group
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏗️ Create Group Now", callback_data=f"create_group_{target_user_id}")]
            ])
            
            invite_link_message += f"**🏗️ Ready to create your networking group!**\n"
            invite_link_message += f"Click the button below to create a group chat.\n\n"
            invite_link_message += f"💾 **Connection saved to database.**"
            
            await update.message.reply_text(invite_link_message, reply_markup=keyboard)
            
        except Exception as group_error:
            logger.error(f"Group creation failed: {group_error}")
            
            # Fallback to connection without auto group
            success_message = f"🎉 **Instant Connection Created!**\n\n"
            success_message += f"**You're now connected with:**\n"
            success_message += f"👤 **{escape_markdown(target_profile['name'])}**\n"
            success_message += f"🏢 **Role:** {escape_markdown(target_profile['role'])}\n"
            success_message += f"🚀 **Project:** {escape_markdown(target_profile['project'])}\n"
            success_message += f"💬 **Bio:** {escape_markdown(target_profile['bio'])}\n\n"
            success_message += f"💡 **Next Steps:**\n"
            success_message += f"• You can now message each other directly\n"
            success_message += f"• Use /creategroup {target_user_id} to create a group\n"
            success_message += f"• View all connections: /myconnections\n\n"
            success_message += f"💾 **Connection saved to database.**"
            
            await update.message.reply_text(success_message)
        
        # Notify the target user
        try:
            target_message = f"🎉 **New Connection!**\n\n"
            target_message += f"**{escape_markdown(user_profile['name'])}** just connected with you!\n\n"
            target_message += f"🏢 **Their Role:** {escape_markdown(user_profile['role'])}\n"
            target_message += f"🚀 **Their Project:** {escape_markdown(user_profile['project'])}\n"
            target_message += f"💬 **Their Bio:** {escape_markdown(user_profile['bio'])}\n\n"
            target_message += f"💡 **Start networking!** Use /myconnections to see all your connections.\n\n"
            target_message += f"💾 **Connection saved to your WeMeetAI profile.**"
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=target_message
            )
        except Exception as e:
            logger.info(f"Could not notify target user {target_user_id}: {e}")
            # This is fine - they'll see the connection when they check the bot
        
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        # Still created the connection in database, just inform user
        await update.message.reply_text(
            f"🎉 **Connection Created!**\n\n"
            f"You're now connected with **{escape_markdown(target_profile['name'])}**!\n"
            f"Use /myconnections to see all your connections.\n\n"
            f"💾 **Connection saved to database.**"
        )

async def handle_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle instant connection request"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /connect [user_id]")
        return
    
    try:
        target_user_id = int(context.args[0])
        
        target_profile = await get_user_profile(target_user_id)
        if not target_profile:
            await update.message.reply_text("❌ User not found")
            return
        
        if target_user_id == user_id:
            await update.message.reply_text("❌ You cannot connect with yourself!")
            return
        
        # Check if already connected
        connection_exists = await check_connection_exists(user_id, target_user_id)
        if connection_exists:
            await update.message.reply_text(
                f"✅ **Already Connected!**\n\n"
                f"You're already connected with {escape_markdown(target_profile['name'])}.\n"
                f"Use /myconnections to see all your connections."
            )
            return
        
        # Create instant connection
        await create_instant_connection(update, context, user_id, target_user_id)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")

async def generate_qr_with_color(query, context, color_name):
    """Generate QR with selected color"""
    user_id = query.from_user.id
    user_name = get_full_name(query.from_user)
    
    # Create basic profile if user doesn't have one
    profile = await get_user_profile(user_id)
    if not profile:
        username = query.from_user.username or user_name.replace(' ', '').lower()
        basic_profile = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'WeMeetAI User',
            'profile_image_url': profile_image_url
        }
        success = await create_or_update_user_profile(user_id, basic_profile)
        if success:
            profile = await get_user_profile(user_id)
        else:
            await query.edit_message_text("❌ Failed to create your profile. Please try again.")
            return
    
    # Get QR data
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        qr_data = f"LinkUp://user/{user_id}"
    
    # Generate username for QR
    username = profile.get('username', profile['name'].replace(' ', '').lower())
    
    # Get color from the color map
    qr_color = QR_COLORS.get(color_name, QR_COLORS['blue'])  # Default to blue if color not found
    
    await query.edit_message_text(f"🎨 **Creating your {color_name.title()} QR card...** ⏳")
    
    try:
        # Create card style QR with specified color
        card_qr = create_card_style_qr(qr_data, username, qr_color=qr_color)
        
        if card_qr:
            bio = io.BytesIO()
            card_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"🎨 **Your {color_name.title()} ETHCC QR Card**\n\n"
            caption += f"👤 **Profile:** {profile['name']}\n"
            caption += f"🏢 **Role:** {profile['role']}\n"
            caption += f"🚀 **Project:** {profile['project']}\n\n"
            caption += f"💡 **Share this QR card at ETHCC events!**"
            
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            await query.edit_message_text(f"✅ **{color_name.title()} ETHCC QR Card sent!** Show it off at your next event! 🎉")
        else:
            await query.edit_message_text(
                "❌ **QR card creation failed**\n\n"
                "Use /myqr for a basic QR code instead."
            )
            
    except Exception as e:
        logger.error(f"QR card generation failed: {e}")
        await query.edit_message_text(
            "❌ **QR card creation failed**\n\n"
            f"Error: {str(e)}\n\n"
            "Use /myqr for a basic QR code instead."
        )

async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Show main menu"),
        BotCommand("update_profile", "Set up or update your profile"),
        BotCommand("myqr", "Generate a basic QR code to share"),
        BotCommand("myconnections", "View all your connections"),
        # BotCommand("creategroup", "Create a group chat with your connections"),
        # BotCommand("scan", "Scan a QR code from image"),
        # BotCommand("connect", "Connect with a user by ID"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Main function"""
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN environment variable not set")
    
    # ETHCC-themed ASCII art banner
    ethcc_banner = """
    ███████╗████████╗██╗  ██╗ ██████╗ ██████╗     ██████╗  ██████╗ ████████╗
    ██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
    █████╗     ██║   ███████║██║     ██║         ██████╔╝██║   ██║   ██║   
    ██╔══╝     ██║   ██╔══██║██║     ██║         ██╔══██╗██║   ██║   ██║   
    ███████╗   ██║   ██║  ██║╚██████╗╚██████╗    ██████╔╝╚██████╔╝   ██║   
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝    ╚═════╝  ╚═════╝    ╚═╝   
                                                                        
    📱 Networking made easy - Scan, Connect, Chat! 🚀
    """
    
    print(ethcc_banner)
    
    # Build application with hooks
    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(initialize_app)
        .post_shutdown(shutdown_app)
        .build()
    )
    
    # Set bot commands for the small Menu button
    asyncio.get_event_loop().run_until_complete(set_bot_commands(app))
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update_profile", setup_profile))
    app.add_handler(CommandHandler("myqr", generate_qr))
    app.add_handler(CommandHandler("scan", handle_scan))
    app.add_handler(CommandHandler("connect", handle_connect))
    app.add_handler(CommandHandler("myconnections", list_connections))
    # app.add_handler(CommandHandler("creategroup", create_group))  # Comment out handler registration
    # app.add_handler(CommandHandler("scan", handle_scan))  # Comment out handler registration
    # app.add_handler(CommandHandler("connect", handle_connect))  # Comment out handler registration
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Starting WeMeetAI Bot with ETHCC Theme...")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()