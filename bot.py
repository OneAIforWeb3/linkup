#!/usr/bin/env python3
"""
EventCRM Telegram Bot - Running on ROFL
A networking assistant for event attendees
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram_api import telegram_api, initialize_telegram_api, close_telegram_api

load_dotenv()

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
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    
    # Handle deep link parameters (from QR code scan)
    if context.args and context.args[0].startswith("user_"):
        try:
            target_user_id = int(context.args[0].replace("user_", ""))
            
            # Check if user has a profile - but allow connection anyway
            if user_id not in user_profiles:
                # Create a basic profile for the user
                user_profiles[user_id] = {
                    'name': user_name,
                    'role': 'Not specified',
                    'project': 'Not specified',
                    'bio': 'Profile not set up yet',
                    'telegram_id': user_id,
                    'created_at': datetime.now().isoformat()
                }
            
            # Check if target user exists
            if target_user_id not in user_profiles:
                await update.message.reply_text("❌ The user you're trying to connect with hasn't set up their profile yet.")
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
            
            # Create instant connection
            await create_instant_connection(update, context, user_id, target_user_id)
            return
            
        except (ValueError, IndexError):
            # Invalid parameter, continue with normal welcome
            pass
    
    # Normal welcome message
    welcome_text = f"""
🎉 Welcome to EventCRM, {user_name}!

Your personal networking assistant for events.

Commands:
/profile - Set up your profile
/myqr - Get your QR code
/scan [qr_data] - Scan someone's QR code
/connect [user_id] - Connect with someone
/myconnections - View your connections
/creategroup [user_ids] - Create group with connections
/note [user_id] [note] - Add private note
    """
    await update.message.reply_text(welcome_text)

async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Profile setup"""
    await update.message.reply_text(
        "Send your profile in format:\n"
        "Name | Role | Project | Bio\n\n"
        "Example: John Doe | VC | TechFund | Looking for AI startups"
    )
    context.user_data['awaiting_profile'] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile input"""
    if context.user_data.get('awaiting_profile'):
        parts = update.message.text.split(' | ')
        if len(parts) == 4:
            name, role, project, bio = parts
            user_id = update.effective_user.id
            
            user_profiles[user_id] = {
                'name': name.strip(),
                'role': role.strip(),
                'project': project.strip(),
                'bio': bio.strip(),
                'telegram_id': user_id,
                'created_at': datetime.now().isoformat()
            }
            
            await update.message.reply_text(
                f"✅ Profile saved!\n\n"
                f"Name: {name}\n"
                f"Role: {role}\n"
                f"Project: {project}\n"
                f"Bio: {bio}\n\n"
                f"Get your QR code: /myqr"
            )
            context.user_data['awaiting_profile'] = False
        else:
            await update.message.reply_text("❌ Please use format: Name | Role | Project | Bio")

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.message.reply_text("❌ Set up your profile first: /profile")
        return
    
    profile = user_profiles[user_id]
    # Use Telegram deep link format that works with all QR scanners
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        qr_data = f"https://t.me/{bot_username}?start=user_{user_id}"
    except Exception as e:
        logger.error(f"Could not get bot username: {e}")
        # Fallback to user ID only
        qr_data = f"eventcrm://user/{user_id}"
    
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
                   f"**QR Data:** `{qr_data}`\n\n"
                   f"💡 **Share this QR code with other attendees to connect!**",
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

async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle QR code scan"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "📱 **QR Code Scanner**\n\n"
            "Usage: `/scan [QR_CODE_DATA]`\n\n"
            "Examples:\n"
            "• `/scan https://t.me/your_bot?start=user_5094393032`\n"
            "• `/scan eventcrm://user/5094393032`\n"
            "• `/scan 5094393032` (just the user ID)\n\n"
            "💡 **In a real app, this would use your camera to scan QR codes automatically!**"
        )
        return
    
    qr_input = ' '.join(context.args)
    
    # Extract user ID from QR code
    target_user_id = None
    
    if qr_input.startswith("eventcrm://user/"):
        try:
            target_user_id = int(qr_input.replace("eventcrm://user/", ""))
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
    
    # Create instant connection
    await create_instant_connection(update, context, user_id, target_user_id)

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
    
    if query.data.startswith("create_group_"):
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
                    # Success message with invite link
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
            "🚀 **EventCRM now uses instant connections!**\n\n"
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
    
    group_name = f"EventCRM: {' & '.join(group_members[:3])}"
    if len(group_members) > 3:
        group_name += f" + {len(group_members) - 3} others"
    
    # Create group description
    group_description = f"EventCRM networking group created by {user_profile['name']}\n\n"
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
    app.add_handler(CommandHandler("scan", handle_scan))
    app.add_handler(CommandHandler("connect", handle_connect))
    app.add_handler(CommandHandler("myconnections", list_connections))
    app.add_handler(CommandHandler("creategroup", create_group))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Starting EventCRM Bot...")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()