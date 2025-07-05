#!/usr/bin/env python3
"""
LinkUp Telegram Bot - Running on ROFL
A networking assistant for event attendees
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram_api import telegram_api, initialize_telegram_api, close_telegram_api
import qrcode
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import random
import math

load_dotenv()

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
    'blockchain': {
        'bg_colors': [(147, 51, 234), (79, 70, 229)],  # Vibrant purple gradient
        'pattern': 'tech',
        'qr_colors': [(255, 255, 255), (240, 240, 240)]
    },
    'ethereum': {
        'bg_colors': [(99, 102, 241), (139, 69, 19)],  # ETH indigo/brown
        'pattern': 'crypto',
        'qr_colors': [(255, 255, 255), (240, 248, 255)]
    },
    'ocean': {
        'bg_colors': [(14, 165, 233), (6, 182, 212)],  # Vibrant ocean blue
        'pattern': 'waves',
        'qr_colors': [(255, 255, 255), (240, 255, 255)]
    },
    'sunset': {
        'bg_colors': [(251, 146, 60), (239, 68, 68)],  # Vibrant orange/red sunset
        'pattern': 'geometric',
        'qr_colors': [(255, 255, 255), (255, 248, 240)]
    },
    'forest': {
        'bg_colors': [(34, 197, 94), (21, 128, 61)],  # Vibrant green forest
        'pattern': 'nature',
        'qr_colors': [(255, 255, 255), (240, 255, 240)]
    },
    'minimal': {
        'bg_colors': [(71, 85, 105), (148, 163, 184)],  # Modern gray gradient
        'pattern': 'clean',
        'qr_colors': [(255, 255, 255), (248, 248, 248)]
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
        if theme_config.get('pattern') in ['tech', 'crypto']:
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
    
    # Add subtle border frame
    frame_margin = int(size * 0.01)
    draw.rectangle([frame_margin, frame_margin, size - frame_margin, size - frame_margin], 
                  outline=(255, 255, 255, 100), width=2)

def create_themed_qr(qr_data, username, event_name=None, theme='blockchain', size=1000):
    """Create a themed QR code with username and optional event name"""
    try:
        
        # Get theme configuration
        theme_config = QR_THEMES.get(theme, QR_THEMES['blockchain'])
        
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
        qr_size = int(size * 0.4)  # QR takes 40% of canvas (reduced for better spacing)
        qr_x = (size - qr_size) // 2
        
        # Dynamic positioning based on whether event name exists
        if event_name:
            qr_y = int(size * 0.4)  # Lower position when event name exists
        else:
            qr_y = int(size * 0.35)  # Higher position when no event name
        
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
            
            # Different font sizes for better hierarchy
            title_font = None
            username_font = None
            event_font = None
            
            for font_path in font_paths:
                try:
                    title_font = ImageFont.truetype(font_path, 72)  # Larger for title
                    username_font = ImageFont.truetype(font_path, 56)  # Medium for username
                    event_font = ImageFont.truetype(font_path, 48)  # Smaller for event
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
        
        # Add username at bottom with improved spacing
        username_text = f"@{username}" if not username.startswith('@') else username
        
        bbox = draw.textbbox((0, 0), username_text, font=username_font)
        username_width = bbox[2] - bbox[0]
        username_x = (size - username_width) // 2
        username_y = int(size * 0.85)  # Bottom positioning with percentage
        
        # Enhanced username text shadow
        for offset in range(4, 0, -1):
            shadow_alpha = int(150 * offset / 4)
            draw.text((username_x + offset, username_y + offset), username_text, 
                     fill=(0, 0, 0, shadow_alpha), font=username_font)
        
        # Main username text
        draw.text((username_x, username_y), username_text, fill=(255, 255, 255, 255), font=username_font)
        
        # Add enhanced decorative elements
        add_decorative_elements(draw, size, theme_config)
        
        # Convert back to RGB
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

# In-memory storage (in production, use encrypted database)
user_profiles = {}
connection_requests = {}
user_connections = {}
user_notes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message and handle deep link parameters"""
    user_name = get_full_name(update.effective_user)
    user_id = update.effective_user.id
    
    # Handle deep link parameters (from QR code scan)
    if context.args and context.args[0].startswith("user_"):
        try:
            target_user_id = int(context.args[0].replace("user_", ""))
            
            # Create basic profile if user doesn't have one
            if user_id not in user_profiles:
                username = update.effective_user.username or user_name.replace(' ', '').lower()
                user_profiles[user_id] = {
                    'name': user_name,
                    'username': username,
                    'role': 'Not specified',
                    'project': f"{user_name}'s Project",
                    'bio': 'LinkUp User',
                    'telegram_id': user_id,
                    'created_at': datetime.now().isoformat()
                }
            
            # Get target user info (create basic profile if needed)
            if target_user_id not in user_profiles:
                try:
                    target_user = await context.bot.get_chat(target_user_id)
                    target_name = get_full_name(target_user)
                    target_username = target_user.username or target_name.replace(' ', '').lower()
                    user_profiles[target_user_id] = {
                        'name': target_name,
                        'username': target_username,
                        'role': 'Not specified',
                        'project': f"{target_name}'s Project",
                        'bio': 'LinkUp User',
                        'telegram_id': target_user_id,
                        'created_at': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Could not get target user info: {e}")
                    await update.message.reply_text("❌ Could not connect with this user. Please try again.")
                    return
            
            if target_user_id == user_id:
                await update.message.reply_text("❌ You cannot connect with yourself!")
                return
            
            # Get profiles
            user_profile = user_profiles[user_id]
            target_profile = user_profiles[target_user_id]
            
            # Check if already connected
            if (user_id in user_connections and target_user_id in user_connections[user_id]):
                await update.message.reply_text(
                    f"✅ **Already Connected!**\n\n"
                    f"You're already connected with {target_profile['name']}.\n"
                    f"Use /myconnections to see all your connections."
                )
                return
            
            # Show immediate group creation option
            await show_group_creation_option(update, context, user_id, target_user_id)
            return
            
        except (ValueError, IndexError):
            # Invalid parameter, continue with normal welcome
            pass
    
    # Normal welcome message with options
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Basic QR Code", callback_data="generate_qr")],
        [InlineKeyboardButton("🎨 Themed QR Code", callback_data="themed_qr_menu")],
        [InlineKeyboardButton("✏️ Update Profile", callback_data="update_profile")]
    ])
    
    welcome_text = f"""
🎉 Welcome to LinkUp, {user_name}!

Your personal networking assistant for events.

**Quick Actions:**
    """
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Profile setup"""
    await update.message.reply_text(
        "Send your profile in format:\n"
        "Name | Role | Project | Bio\n\n"
        "Example: John Doe | VC | TechFund | Looking for AI startups"
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
            
            user_profiles[user_id] = {
                'name': name,
                'username': update.effective_user.username or name.replace(' ', '').lower(),
                'role': role,
                'project': project,
                'bio': bio,
                'telegram_id': user_id,
                'created_at': datetime.now().isoformat()
            }
            
            await update.message.reply_text(
                f"✅ **Profile Updated!**\n\n"
                f"👤 **Name:** {name}\n"
                f"🏢 **Role:** {role}\n"
                f"🚀 **Project:** {project}\n"
                f"💬 **Bio:** {bio}\n\n"
                f"Perfect! You can now generate QR codes and start networking.",
                parse_mode='Markdown'
            )
            context.user_data['awaiting_profile'] = False
        else:
            await update.message.reply_text(
                "❌ Invalid format. Please use:\n\n"
                "**Name | Role | Project | Bio**\n\n"
                "Example:\n"
                "`John Doe | VC | TechFund | Looking for AI startups`",
                parse_mode='Markdown'
            )
    else:
        # Handle other text messages
        await update.message.reply_text(
            "👋 Hi! Use /start to see available options, or try:\n\n"
            "📱 /myqr - Generate your QR code\n"
            "✏️ /profile - Update your profile\n"
            "🔍 /scan - Scan someone's QR code\n"
            "👥 /myconnections - View your connections"
        )

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code (works with or without full profile)"""
    user_id = update.effective_user.id
    user_name = get_full_name(update.effective_user)
    
    # Create basic profile if user doesn't have one
    if user_id not in user_profiles:
        username = update.effective_user.username or user_name.replace(' ', '').lower()
        user_profiles[user_id] = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'LinkUp User',
            'telegram_id': user_id,
            'created_at': datetime.now().isoformat()
        }
    
    profile = user_profiles[user_id]
    
    # Use Telegram deep link format that works with all QR scanners
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        # Fallback to user ID only
        qr_data = f"LinkUp://user/{user_id}"
    
    # Generate QR code image
    import qrcode
    import io
    from PIL import Image
    
    try:
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
                   f"{profile['name']} | {profile['role']} | {profile['project']}\n"
                   f"{profile['bio']}\n\n"
                   f"💡 **Want a themed QR?** Try `/themedqr event:ETHCC theme:ethereum`\n\n"
                   f"**Available themes:** blockchain, ethereum, ocean, sunset, forest, minimal",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        # Fallback to text
        await update.message.reply_text(
            f"📱 Your QR Code:\n\n"
            f"`{qr_data}`\n\n"
            f"👤 Your Profile:\n"
            f"{profile['name']} | {profile['role']} | {profile['project']}\n"
            f"{profile['bio']}", 
            parse_mode='Markdown'
        )

async def generate_themed_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a themed, personalized QR code"""
    user_id = update.effective_user.id
    user_name = get_full_name(update.effective_user)
    
    # Create basic profile if user doesn't have one
    if user_id not in user_profiles:
        username = update.effective_user.username or user_name.replace(' ', '').lower()
        user_profiles[user_id] = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'LinkUp User',
            'telegram_id': user_id,
            'created_at': datetime.now().isoformat()
        }
    
    profile = user_profiles[user_id]
    
    # Parse command arguments
    event_name = None
    theme = 'blockchain'  # Default theme
    
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
            f"**Example:** `/themedqr event:ETHCC theme:ethereum`",
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
    
    # Send "generating" message
    generating_msg = await update.message.reply_text("🎨 **Creating your themed QR code...** ⏳")
    
    try:
        # Create themed QR
        themed_qr = create_themed_qr(qr_data, username, event_name, theme)
        
        if themed_qr:
            bio = io.BytesIO()
            themed_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"🎨 **Your Themed QR Code**\n\n"
            if event_name:
                caption += f"🎪 **Event:** {event_name.upper()}\n"
            caption += f"🎯 **Theme:** {theme.title()}\n"
            caption += f"👤 **Profile:** {profile['name']}\n"
            caption += f"🏢 **Role:** {profile['role']}\n"
            caption += f"🚀 **Project:** {profile['project']}\n\n"
            caption += f"💡 **Show this personalized QR code at events to stand out!**\n\n"
            caption += f"**Try other themes:**\n"
            caption += f"• `/themedqr theme:ethereum` - Crypto style\n"
            caption += f"• `/themedqr theme:ocean` - Ocean vibes\n"
            caption += f"• `/themedqr theme:sunset` - Warm colors"
            
            await update.message.reply_photo(
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Delete the generating message
            await generating_msg.delete()
        else:
            # Fallback if themed QR creation fails
            await generating_msg.edit_text(
                "❌ **Themed QR creation failed**\n\n"
                "Use `/myqr` for a basic QR code instead."
            )
            
    except Exception as e:
        logger.error(f"Themed QR code generation failed: {e}")
        await generating_msg.edit_text(
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
    
    # Extract user ID from QR code
    target_user_id = None
    
    if qr_input.startswith("LinkUp://user/"):
        try:
            target_user_id = int(qr_input.replace("LinkUp://user/", ""))
        except ValueError:
            await update.message.reply_text("❌ Invalid QR code format")
            return
    elif "?start=user_" in qr_input:
        # Handle Telegram deep link format
        try:
            start_param = qr_input.split("?start=user_")[1]
            target_user_id = int(start_param)
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Invalid QR code format")
            return
    else:
        # Try to parse as direct user ID
        try:
            target_user_id = int(qr_input)
        except ValueError:
            await update.message.reply_text("❌ Invalid QR code format")
            return
    
    # Check if target user exists
    if target_user_id not in user_profiles:
        await update.message.reply_text("❌ User not found or hasn't set up profile")
        return
    
    if target_user_id == user_id:
        await update.message.reply_text("❌ You cannot connect with yourself!")
        return
    
    # Instant connection - no approval needed!
    target_profile = user_profiles[target_user_id]
    
    # Check if already connected
    if (user_id in user_connections and target_user_id in user_connections[user_id]):
        await update.message.reply_text(
            f"✅ **Already Connected!**\n\n"
            f"You're already connected with {target_profile['name']}.\n"
            f"Use /myconnections to see all your connections."
        )
        return
    
    # Show group creation option instead of creating instant connection
    await show_group_creation_option(update, context, user_id, target_user_id)

async def show_group_creation_option(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, target_user_id: int):
    """Show immediate group creation option when users scan QR codes"""
    user_profile = user_profiles[user_id]
    target_profile = user_profiles[target_user_id]
    
    # Create instant connection first
    if user_id not in user_connections:
        user_connections[user_id] = []
    if target_user_id not in user_connections:
        user_connections[target_user_id] = []
    
    user_connections[user_id].append(target_user_id)
    user_connections[target_user_id].append(user_id)
    
    # Show group creation option
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏗️ Create Group Now", callback_data=f"instant_group_{target_user_id}")],
        [InlineKeyboardButton("📋 View Profile", callback_data=f"view_profile_{target_user_id}")]
    ])
    
    message = f"🎉 **Connected with {target_profile['name']}!**\n\n"
    message += f"👤 **{target_profile['name']}**\n"
    message += f"🏢 **Role:** {target_profile['role']}\n"
    message += f"🚀 **Project:** {target_profile['project']}\n"
    message += f"💬 **Bio:** {target_profile['bio']}\n\n"
    message += f"**Ready to start networking?**"
    
    await update.message.reply_text(message, reply_markup=keyboard)

async def generate_qr_from_callback(query, context):
    """Generate QR code from callback"""
    user_id = query.from_user.id
    user_name = get_full_name(query.from_user)
    
    # Create basic profile if user doesn't have one
    if user_id not in user_profiles:
        username = query.from_user.username or user_name.replace(' ', '').lower()
        user_profiles[user_id] = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'LinkUp User',
            'telegram_id': user_id,
            'created_at': datetime.now().isoformat()
        }
    
    profile = user_profiles[user_id]
    
    # Get QR data
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        qr_data = f"LinkUp://user/{user_id}"
    
    # Generate QR code image
    import qrcode
    import io
    
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        bio = io.BytesIO()
        qr_image.save(bio, format='PNG')
        bio.seek(0)
        
        # Send QR code image
        await context.bot.send_photo(
            chat_id=query.from_user.id,
            photo=bio,
            caption=f"📱 **Your QR Code**\n\n"
                   f"👤 **Your Profile:**\n"
                   f"{profile['name']} | {profile['role']} | {profile['project']}\n"
                   f"{profile['bio']}\n\n"
                   f"💡 **Share this QR code with other attendees to instantly create groups!**",
            parse_mode='Markdown'
        )
        
        await query.edit_message_text("✅ **QR Code sent!** Share it with other attendees to connect instantly.")
        
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        await query.edit_message_text(f"📱 Your QR Code: `{qr_data}`\n\nShare this with other attendees!", parse_mode='Markdown')

async def show_themed_qr_menu(query, context):
    """Show themed QR code menu"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔷 Blockchain", callback_data="themed_qr_blockchain"),
         InlineKeyboardButton("💎 Ethereum", callback_data="themed_qr_ethereum")],
        [InlineKeyboardButton("🌊 Ocean", callback_data="themed_qr_ocean"),
         InlineKeyboardButton("🌅 Sunset", callback_data="themed_qr_sunset")],
        [InlineKeyboardButton("🌲 Forest", callback_data="themed_qr_forest"),
         InlineKeyboardButton("⚪ Minimal", callback_data="themed_qr_minimal")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
    ])
    
    await query.edit_message_text(
        "🎨 **Choose Your QR Theme**\n\n"
        "Select a theme for your personalized QR code:\n\n"
        "🔷 **Blockchain** - Purple tech vibes\n"
        "💎 **Ethereum** - Crypto blue/purple\n"
        "🌊 **Ocean** - Turquoise waves\n"
        "🌅 **Sunset** - Warm orange/red\n"
        "🌲 **Forest** - Natural green\n"
        "⚪ **Minimal** - Clean gray\n\n"
        "💡 **Tip:** Use `/themedqr event:EVENTNAME theme:THEME` for event-specific QR codes!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def generate_themed_qr_callback(query, context, theme):
    """Generate themed QR from callback"""
    user_id = query.from_user.id
    user_name = get_full_name(query.from_user)
    
    # Create basic profile if user doesn't have one
    if user_id not in user_profiles:
        username = query.from_user.username or user_name.replace(' ', '').lower()
        user_profiles[user_id] = {
            'name': user_name,
            'username': username,
            'role': 'Not specified',
            'project': f"{user_name}'s Project",
            'bio': 'LinkUp User',
            'telegram_id': user_id,
            'created_at': datetime.now().isoformat()
        }
    
    profile = user_profiles[user_id]
    
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
    
    await query.edit_message_text("🎨 **Creating your themed QR code...** ⏳")
    
    try:
        # Create themed QR
        themed_qr = create_themed_qr(qr_data, username, None, theme)
        
        if themed_qr:
            bio = io.BytesIO()
            themed_qr.save(bio, format='PNG', quality=95)
            bio.seek(0)
            
            caption = f"🎨 **Your {theme.title()} QR Code**\n\n"
            caption += f"👤 **Profile:** {profile['name']}\n"
            caption += f"🏢 **Role:** {profile['role']}\n"
            caption += f"🚀 **Project:** {profile['project']}\n\n"
            caption += f"💡 **Share this personalized QR code at events!**\n\n"
            caption += f"**Want event-specific QR?**\n"
            caption += f"Use: `/themedqr event:ETHCC theme:{theme}`"
            
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=bio,
                caption=caption,
                parse_mode='Markdown'
            )
            
            await query.edit_message_text("✅ **Themed QR Code sent!** Show it off at your next event! 🎉")
        else:
            await query.edit_message_text(
                "❌ **Themed QR creation failed**\n\n"
                "Use /myqr for a basic QR code instead."
            )
            
    except Exception as e:
        logger.error(f"Themed QR code generation failed: {e}")
        await query.edit_message_text(
            "❌ **Themed QR creation failed**\n\n"
            f"Error: {str(e)}\n\n"
            "Use /myqr for a basic QR code instead."
        )

async def update_profile_from_callback(query, context):
    """Handle profile update from callback"""
    await query.edit_message_text(
        "✏️ **Update Your Profile**\n\n"
        "Send your profile in format:\n"
        "**Name | Role | Project | Bio**\n\n"
        "Example: John Doe | VC | TechFund | Looking for AI startups"
    )
    context.user_data['awaiting_profile'] = True

async def create_instant_group(query, context, target_user_id):
    """Create group immediately after QR scan"""
    user_id = query.from_user.id
    user_profile = user_profiles[user_id]
    target_profile = user_profiles[target_user_id]
    
    # Create group name: Project (UserA) <-> Project (UserB)
    group_title = f"{user_profile['project']} <-> {target_profile['project']}"
    group_description = f"LinkUp networking group: {user_profile['name']} & {target_profile['name']}"
    
    await query.edit_message_text("🏗️ **Creating your networking group...** ⏳")
    
    try:
        # Use Telegram API to create group
        if telegram_api.is_initialized:
            group_info = await telegram_api.create_group(
                group_title=group_title,
                user_ids=[target_user_id],
                description=group_description
            )
            
            if group_info:
                # Group created successfully - Send invite links via BOT
                success_message = f"🎉 **Group Created Successfully!**\n\n"
                success_message += f"**Group:** {group_info['group_title']}\n"
                success_message += f"**Members:** {group_info['member_count']}\n\n"
                success_message += f"🔗 **Join your group:**\n{group_info['invite_link']}\n\n"
                success_message += f"✅ {target_profile['name']} will receive their invite link from the bot!"
                
                await query.edit_message_text(success_message)
                
                # Send invite link to target user via BOT (not API user)
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"🎉 **You've been invited to a networking group!**\n\n"
                             f"**Group:** {group_info['group_title']}\n"
                             f"**Created by:** {user_profile['name']} ({user_profile['role']})\n\n"
                             f"🔗 **Join here:** {group_info['invite_link']}\n\n"
                             f"💡 **About {user_profile['name']}:**\n"
                             f"🏢 Role: {user_profile['role']}\n"
                             f"🚀 Project: {user_profile['project']}\n"
                             f"💬 Bio: {user_profile['bio']}\n\n"
                             f"Click the link to join and start networking! 🚀"
                    )
                    logger.info(f"Bot sent group invite to user {target_user_id}")
                except Exception as e:
                    logger.error(f"Failed to send bot invite to user {target_user_id}: {e}")
                
                return  # Successfully created group
        
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
        fallback_message += f"4. Start networking! 🚀"
        
        await query.edit_message_text(fallback_message)

async def view_user_profile(query, context, target_user_id):
    """View user profile details"""
    target_profile = user_profiles[target_user_id]
    
    profile_message = f"👤 **Profile: {target_profile['name']}**\n\n"
    profile_message += f"🏢 **Role:** {target_profile['role']}\n"
    profile_message += f"🚀 **Project:** {target_profile['project']}\n"
    profile_message += f"💬 **Bio:** {target_profile['bio']}\n\n"
    profile_message += f"**Connected!** You can now message each other directly."
    
    await query.edit_message_text(profile_message)

async def create_instant_connection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, target_user_id: int):
    """Create instant connection and group between two users"""
    
    # Get profiles
    user_profile = user_profiles[user_id]
    target_profile = user_profiles[target_user_id]
    
    # Add to connections
    if user_id not in user_connections:
        user_connections[user_id] = []
    if target_user_id not in user_connections:
        user_connections[target_user_id] = []
    
    user_connections[user_id].append(target_user_id)
    user_connections[target_user_id].append(user_id)
    
    # Create group name
    group_name = f"{user_profile['name']} ↔ {target_profile['name']}"
    
    # Try to create actual Telegram group automatically
    try:
        # Create actual Telegram group with both users
        group_title = f"{user_profile['name']} ↔ {target_profile['name']}"
        
        # First create a group chat (Telegram requires special handling)
        # We'll use the bot's ability to create group chats
        group_chat = None
        
        try:
            # Method 1: Try to create a supergroup
            # Note: This requires both users to have started the bot
            
            # Create an invite link approach - more reliable
            invite_link_message = f"🎉 **Instant Connection + Auto Group!**\n\n"
            invite_link_message += f"**Connected with:** {target_profile['name']}\n"
            invite_link_message += f"🏢 **Role:** {target_profile['role']}\n"
            invite_link_message += f"🚀 **Project:** {target_profile['project']}\n"
            invite_link_message += f"💬 **Bio:** {target_profile['bio']}\n\n"
            
            # Create a group by having the bot start a group conversation
            # This is a workaround since direct group creation has limitations
            
            # Send the invite to create the group
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏗️ Create Group Now", callback_data=f"create_group_{target_user_id}")]
            ])
            
            invite_link_message += f"**🏗️ Ready to create your networking group!**\n"
            invite_link_message += f"Click the button below to create a group chat."
            
            await update.message.reply_text(invite_link_message, reply_markup=keyboard)
            
        except Exception as group_error:
            logger.error(f"Group creation failed: {group_error}")
            
            # Fallback to connection without auto group
            success_message = f"🎉 **Instant Connection Created!**\n\n"
            success_message += f"**You're now connected with:**\n"
            success_message += f"👤 **{target_profile['name']}**\n"
            success_message += f"🏢 **Role:** {target_profile['role']}\n"
            success_message += f"🚀 **Project:** {target_profile['project']}\n"
            success_message += f"💬 **Bio:** {target_profile['bio']}\n\n"
            success_message += f"💡 **Next Steps:**\n"
            success_message += f"• You can now message each other directly\n"
            success_message += f"• Use /creategroup {target_user_id} to create a group\n"
            success_message += f"• View all connections: /myconnections"
            
            await update.message.reply_text(success_message)
        
        # Notify the target user
        try:
            target_message = f"🎉 **New Connection!**\n\n"
            target_message += f"**{user_profile['name']}** just connected with you!\n\n"
            target_message += f"🏢 **Their Role:** {user_profile['role']}\n"
            target_message += f"🚀 **Their Project:** {user_profile['project']}\n"
            target_message += f"💬 **Their Bio:** {user_profile['bio']}\n\n"
            target_message += f"💡 **Start networking!** Use /myconnections to see all your connections."
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=target_message
            )
        except Exception as e:
            logger.info(f"Could not notify target user {target_user_id}: {e}")
            # This is fine - they'll see the connection when they check the bot
        
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        # Still create the connection, just without group
        await update.message.reply_text(
            f"🎉 **Connection Created!**\n\n"
            f"You're now connected with **{target_profile['name']}**!\n"
            f"Use /myconnections to see all your connections."
        )

async def handle_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle instant connection request"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /connect [user_id]")
        return
    
    try:
        target_user_id = int(context.args[0])
        
        if target_user_id not in user_profiles:
            await update.message.reply_text("❌ User not found")
            return
        
        if target_user_id == user_id:
            await update.message.reply_text("❌ You cannot connect with yourself!")
            return
        
        # Check if already connected
        if (user_id in user_connections and target_user_id in user_connections[user_id]):
            target_profile = user_profiles[target_user_id]
            await update.message.reply_text(
                f"✅ **Already Connected!**\n\n"
                f"You're already connected with {target_profile['name']}.\n"
                f"Use /myconnections to see all your connections."
            )
            return
        
        # Create instant connection
        await create_instant_connection(update, context, user_id, target_user_id)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks including auto group creation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_qr":
        # Handle QR generation from start menu
        await generate_qr_from_callback(query, context)
        return
    
    elif query.data == "update_profile":
        # Handle profile update from start menu
        await update_profile_from_callback(query, context)
        return
    
    elif query.data == "themed_qr_menu":
        # Handle themed QR menu
        await show_themed_qr_menu(query, context)
        return
    
    elif query.data.startswith("themed_qr_"):
        # Handle themed QR generation
        theme = query.data.replace("themed_qr_", "")
        await generate_themed_qr_callback(query, context, theme)
        return
    
    elif query.data.startswith("instant_group_"):
        # Handle instant group creation from QR scan
        target_user_id = int(query.data.replace("instant_group_", ""))
        await create_instant_group(query, context, target_user_id)
        return
    
    elif query.data.startswith("view_profile_"):
        # Handle profile viewing
        target_user_id = int(query.data.replace("view_profile_", ""))
        await view_user_profile(query, context, target_user_id)
        return
    
    elif query.data == "back_to_start":
        # Handle back to start menu
        user_name = get_full_name(query.from_user)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Basic QR Code", callback_data="generate_qr")],
            [InlineKeyboardButton("🎨 Themed QR Code", callback_data="themed_qr_menu")],
            [InlineKeyboardButton("✏️ Update Profile", callback_data="update_profile")]
        ])
        
        welcome_text = f"""
🎉 Welcome to LinkUp, {user_name}!

Your personal networking assistant for events.

**Quick Actions:**
        """
        await query.edit_message_text(welcome_text, reply_markup=keyboard)
        return
    
    elif query.data.startswith("create_group_"):
        # Handle auto group creation using actual Telegram API
        target_user_id = int(query.data.replace("create_group_", ""))
        user_id = query.from_user.id
        
        user_profile = user_profiles[user_id]
        target_profile = user_profiles[target_user_id]
        
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
                    user_ids=[target_user_id],
                    description=group_description
                )
                
                if group_info:
                    # Group created successfully - Send invite links via BOT
                    success_message = f"🎉 **Group Created Successfully!**\n\n"
                    success_message += f"**Group:** {group_info['group_title']}\n"
                    success_message += f"**Members:** {group_info['member_count']}\n"
                    success_message += f"**Invite Link:** {group_info['invite_link']}\n\n"
                    success_message += f"**Instructions:**\n"
                    success_message += f"1. Click the link above to join\n"
                    success_message += f"2. {target_profile['name']} will receive their invite link\n"
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
                                     f"**Group:** {group_info['group_title']}\n"
                                     f"**Created by:** {user_profile['name']} ({user_profile['role']})\n\n"
                                     f"🔗 **Your Invite Link:** {group_info['invite_link']}\n\n"
                                     f"Click the link to join and start networking! 🚀"
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
        
        user_profile = user_profiles[user_id]
        target_profile = user_profiles[target_user_id]
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
        
        user_profile = user_profiles[user_id]
        target_profile = user_profiles[target_user_id]
        
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
    else:
        # For any other callbacks, show instant connections message
        await query.edit_message_text(
            "🚀 **LinkUp now uses instant connections!**\n\n"
            "Just scan QR codes or use /connect for immediate connections.\n"
            "No more waiting for approvals! 🎉"
        )

async def list_connections(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List user connections"""
    user_id = update.effective_user.id
    
    if user_id not in user_connections or not user_connections[user_id]:
        await update.message.reply_text("📭 No connections yet")
        return
    
    connections = user_connections[user_id]
    connection_list = "🤝 Your Connections:\n\n"
    
    for i, connection_id in enumerate(connections, 1):
        if connection_id in user_profiles:
            profile = user_profiles[connection_id]
            connection_list += f"{i}. {profile['name']} - {profile['role']} - {profile['project']}\n"
    
    await update.message.reply_text(connection_list)

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a group with connections using Telegram API"""
    user_id = update.effective_user.id
    
    if user_id not in user_connections or not user_connections[user_id]:
        await update.message.reply_text(
            "📭 **No connections found!**\n\n"
            "You need to connect with someone first before creating a group.\n"
            "Use /myqr to share your QR code and connect with others!"
        )
        return
    
    if not context.args:
        # Show available connections
        connections = user_connections[user_id]
        connection_list = "👥 **Create Group with Connections**\n\n"
        connection_list += "Available connections:\n"
        
        for i, connection_id in enumerate(connections, 1):
            if connection_id in user_profiles:
                profile = user_profiles[connection_id]
                connection_list += f"{i}. {profile['name']} (ID: {connection_id})\n"
        
        connection_list += f"\n💡 **Usage:** `/creategroup [user_id1] [user_id2] ...`\n"
        connection_list += f"**Example:** `/creategroup {connections[0] if connections else 'USER_ID'}`"
        
        await update.message.reply_text(connection_list)
        return
    
    # Parse user IDs
    try:
        target_user_ids = [int(arg) for arg in context.args]
    except ValueError:
        await update.message.reply_text("❌ Invalid user IDs. Please use numbers only.")
        return
    
    # Verify all users are connections
    user_connections_list = user_connections.get(user_id, [])
    for target_id in target_user_ids:
        if target_id not in user_connections_list:
            await update.message.reply_text(f"❌ User {target_id} is not in your connections.")
            return
        if target_id not in user_profiles:
            await update.message.reply_text(f"❌ User {target_id} profile not found.")
            return
    
    # Create group name and description
    user_profile = user_profiles[user_id]
    all_users = [user_id] + target_user_ids
    group_members = []
    
    for uid in all_users:
        if uid in user_profiles:
            profile = user_profiles[uid]
            group_members.append(f"{profile['name']} ({profile['project']})")
    
    group_name = f"LinkUp: {' & '.join(group_members[:3])}"
    if len(group_members) > 3:
        group_name += f" + {len(group_members) - 3} others"
    
    # Create group description
    group_description = f"LinkUp networking group created by {user_profile['name']}\n\n"
    group_description += "Members:\n"
    for uid in all_users:
        if uid in user_profiles:
            profile = user_profiles[uid]
            group_description += f"• {profile['name']} - {profile['role']} at {profile['project']}\n"
    
    # Send processing message
    processing_message = await update.message.reply_text(
        "⏳ **Creating your group...**\n\n"
        f"Group: {group_name}\n"
        f"Members: {len(all_users)}\n\n"
        "This may take a few seconds..."
    )
    
    try:
        # Attempt to create group using Telegram API
        if telegram_api.is_initialized:
            logger.info(f"Attempting to create group '{group_name}' with users: {target_user_ids}")
            
            group_info = await telegram_api.create_group(
                group_title=group_name,
                user_ids=target_user_ids,
                description=group_description
            )
            
            if group_info:
                # Group created successfully!
                success_message = f"🎉 **Group Created Successfully!**\n\n"
                success_message += f"**Group:** {group_info['group_title']}\n"
                success_message += f"**Members:** {group_info['member_count']}\n"
                success_message += f"**Invite Link:** {group_info['invite_link']}\n\n"
                success_message += f"✅ All members have been notified and can join using the link above!"
                
                await processing_message.edit_text(success_message)
                
                # Send invite links to all target users
                for target_id in target_user_ids:
                    try:
                        await telegram_api.send_group_invite(
                            user_id=target_id,
                            group_info=group_info,
                            sender_name=user_profile['name']
                        )
                        logger.info(f"Sent group invite to user {target_id}")
                    except Exception as e:
                        logger.error(f"Failed to send invite to user {target_id}: {e}")
                        # Fallback: send via bot
                        try:
                            await context.bot.send_message(
                                chat_id=target_id,
                                text=f"🎉 **Group Invitation**\n\n"
                                     f"{user_profile['name']} created a group: **{group_info['group_title']}**\n\n"
                                     f"🔗 **Join here:** {group_info['invite_link']}\n\n"
                                     f"Click the link to join and start networking! 🚀"
                            )
                        except Exception as bot_e:
                            logger.error(f"Failed to send bot message to user {target_id}: {bot_e}")
                
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
    instructions += f"**Suggested Group Name:** {group_name}\n\n"
    instructions += f"**To create the group manually:**\n"
    instructions += f"1. Create a new group in Telegram\n"
    instructions += f"2. Add these members:\n"
    
    for uid in all_users:
        if uid in user_profiles:
            profile = user_profiles[uid]
            username = profile.get('username', f'UserID: {uid}')
            instructions += f"   • {profile['name']} (@{username})\n"
    
    instructions += f"\n3. Set group name: {group_name}\n"
    instructions += f"4. Start networking! 🚀\n\n"
    instructions += f"💡 **Tip:** Copy this message and share it with all members!"
    
    await update.message.reply_text(instructions)
    
    # Notify all target users
    for target_id in target_user_ids:
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"👥 **Group Invitation**\n\n"
                     f"{user_profile['name']} wants to create a group:\n"
                     f"**{group_name}**\n\n"
                     f"You'll receive group creation instructions from them!"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {target_id}: {e}")

async def initialize_app(application):
    """Initialize the application and Telegram API client"""
    # Initialize Telegram API client
    logger.info("Initializing Telegram API client...")
    api_success = await initialize_telegram_api()
    if api_success:
        logger.info("✅ Telegram API client initialized - Group creation available!")
    else:
        logger.warning("⚠️ Telegram API client failed to initialize - Using fallback mode")
    
    return api_success

async def shutdown_app(application):
    """Cleanup function"""
    logger.info("Shutting down Telegram API client...")
    await close_telegram_api()

def main():
    """Main function"""
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN environment variable not set")
    
    # Build application with hooks
    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(initialize_app)
        .post_shutdown(shutdown_app)
        .build()
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", setup_profile))
    app.add_handler(CommandHandler("myqr", generate_qr))
    app.add_handler(CommandHandler("themedqr", generate_themed_qr))
    app.add_handler(CommandHandler("scan", handle_scan))
    app.add_handler(CommandHandler("connect", handle_connect))
    app.add_handler(CommandHandler("myconnections", list_connections))
    app.add_handler(CommandHandler("creategroup", create_group))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Starting LinkUp Bot...")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()