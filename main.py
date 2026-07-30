from aliexpress_api import AliexpressApi, models
from API import generate_affiliate_links, get_product_details_by_id, find_and_extract_id_from_aliexpress_links
import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import re

# Load environment variables
load_dotenv()

# Extract environment variables
TRACKING_ID = os.environ.get('TRACKING_ID')
KEY = os.environ.get('KEY')
SECRET = os.environ.get('SECRET')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
COUNTRY_CODE = os.environ.get('COUNTRY_CODE')
CURRENCY = os.environ.get('CURRENCY')
LOADING_STICKER = os.environ.get('LOADING_STICKER')

def clean_title(title):
        return re.sub(r'[^\w\s]', '', title).strip()
def overlay_template(image_url: str, template_path: str = "template.png") -> BytesIO:
    response = requests.get(image_url)
    response.raise_for_status()  
    base_image = Image.open(BytesIO(response.content)).convert("RGBA")
    template = Image.open(template_path).convert("RGBA")
    template = template.resize(base_image.size)
    combined = Image.alpha_composite(base_image, template)
    output_buffer = BytesIO()
    combined.save(output_buffer, format="PNG")
    output_buffer.seek(0)  
    return output_buffer

# Create AliexpressApi object
aliexpress = AliexpressApi(KEY, SECRET, models.Language.EN, CURRENCY, TRACKING_ID)

# Welcome message
WELCOME_MESSAGE = """🛍️ Welcome to AliExpress Bot!

🔗 You can use this bot to get:
- Affiliate links for AliExpress products
- Detailed product information
- Exclusive prices and discounts

📩 How to use:
1. Send product link directly from AliExpress
2. Or forward a message containing AliExpress link

⚡ I will analyze the link and send all available product information!

❗ Note: Please make sure the link is correct and belongs to AliExpress."""

# Bot start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send message when /start command is triggered."""
    await update.message.reply_text(WELCOME_MESSAGE)

async def send_loading_sticker(update: Update):
    if not LOADING_STICKER:
        return None
    try:
        return await update.message.reply_sticker(LOADING_STICKER)
    except Exception:
        return None

async def delete_loading_sticker(sticker_message):
    if not sticker_message:
        return
    try:
        await sticker_message.delete()
    except Exception:
        pass

# Link handling function
async def handle_aliexpress_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle AliExpress links sent by user."""
    # Send "Loading" sticker
    sticker_message = await send_loading_sticker(update)
    
    # Extract text from message (whether regular or forwarded)
    message_text = ""
    if update.message.text:
        message_text = update.message.text
    elif update.message.caption:
        message_text = update.message.caption
    
    if not message_text:
        await delete_loading_sticker(sticker_message)
        await update.message.reply_text("❌ No text found in message. Please send an AliExpress link. 🔍")
        return
    
    try:
        # Extract product ID from link
        product_ids = find_and_extract_id_from_aliexpress_links(message_text)
        
        if not product_ids:
            await delete_loading_sticker(sticker_message)
            await update.message.reply_text("❌ No valid AliExpress link found. Please check the link and try again. 🔍")
            return
        
        product_id = product_ids[0]
        
        # Product ID confirmation message was removed per user request
        async def get_product_info_api(aliexpress, id, country=COUNTRY_CODE):
            try:
                products = await asyncio.to_thread(aliexpress.get_products_details, [id], country=country)
                return products  
            except Exception as e:
                return None

        results = await asyncio.gather(
            generate_affiliate_links(aliexpress, product_id),
            get_product_info_api(aliexpress, product_id, country=COUNTRY_CODE),     
        )
        
        affiliate_links = results[0]
        if results[1] is None:
            product_info = await get_product_details_by_id(product_id)
        else:
            product_info = results[1]
        affiliate_message = f"\n🎯 Exclusive Offers Links:\n\n"
        affiliate_message += f" 🏆 ExtraCoin Discounts:\n *{affiliate_links['ExtraCoin'][8:]}*\n\n"
        affiliate_message += f" 💰 Coin Discounts:\n *{affiliate_links['Coin'][8:]}*\n\n"
        affiliate_message += f" ⚡ Super Deals:\n *{affiliate_links['SuperDeals'][8:]}*\n\n"
        affiliate_message += f" ⏳ Limited Offers:\n *{affiliate_links['LimitedOffers'][8:]}*\n\n"
        affiliate_message += f" 💎 Big Save:\n *{affiliate_links['BigSave'][8:]}*\n\n"
        affiliate_message += f" 📦 Bundle Deals:\n *{affiliate_links['BundleDeals'][8:]}*\n\n"
        # Create keyboard correctly using InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
                [ # Row 1
                InlineKeyboardButton("Button 1", url='https://www.google.com'),
                InlineKeyboardButton("Button 2", url='https://www.google.com')
            ],
            [ # Row 2
                InlineKeyboardButton("Button 3 URL", url='https://www.google.com')
            ]
        ])

        
        # Delete loading sticker
        

        if not product_info:
            await delete_loading_sticker(sticker_message)
            await update.message.reply_text(
                text=affiliate_message,  # Use 'text' instead of 'caption'
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
            return
            
        # Prepare product info and affiliate links in one message
        elif product_info:
            # Check received data type
            if isinstance(product_info, tuple) and len(product_info) == 2:
                await delete_loading_sticker(sticker_message)

                
                # Second data type (product title and image URL)
                product_title, product_image = product_info
                
                # Prepare info message with affiliate links
                info_message = f"{clean_title(product_title)}\n\n"
                info_message += " Switch to Canada country to get full commission discount\n\n "
                
                # Add affiliate links to info message
                info_message += affiliate_message
                
                

                if os.path.exists("template.png"):
                    image =overlay_template(product_image)
                else:
                    image = product_image
                await update.message.reply_photo(
                    photo=image,
                    caption=info_message,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            elif hasattr(product_info, '__iter__') and len(product_info) > 0:
                
                # First data type (object containing detailed info)
                product = product_info[0] 
                # Prepare info message
                info_message = f"{clean_title(product.product_title)}\n\n"
                info_message += " Switch to Canada country to get full commission discount\n\n "
                # Add affiliate links
                info_message += affiliate_message
                info_message += f"📦 Product Information:\n\n"
                # Add price, rating and store info
                if hasattr(product, 'target_sale_price') and hasattr(product, 'target_original_price'):
                    info_message += f"💰 Price: {product.target_sale_price} {product.target_sale_price_currency}\n"
                    info_message += f"💲 Original Price: {product.target_original_price} {product.target_original_price_currency}\n"
                    
                    if hasattr(product, 'discount'):
                        info_message += f"🏷️ Discount: {product.discount}\n"
                
                if hasattr(product, 'evaluate_rate'):
                    info_message += f"⭐ Rating: {product.evaluate_rate}\n"
                    
                if hasattr(product, 'shop_name'):
                    info_message += f"🏪 Store: {product.shop_name}\n"
                
                
                if os.path.exists("template.png"):
                    image =overlay_template(product.product_main_image_url)
                else:
                    image = product.product_main_image_url


                
                await delete_loading_sticker(sticker_message)
                # Send main image with info
                if hasattr(product, 'product_main_image_url'):
                    await update.message.reply_photo(
                        photo=image,
                        caption=info_message,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_text(info_message, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ No product information found. Please check the link and try again.")
    
    except Exception as e:
        # Delete loading sticker in case of error
        await delete_loading_sticker(sticker_message)
        await update.message.reply_text(f"❌ Error processing link: {str(e)}\n\nPlease check the link and try again. 🔄")

# Main function
def main():
    """Run the bot."""
    # Create application and use token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add text message handler (for links)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_aliexpress_link))
    
    # Add forwarded message handler
    application.add_handler(MessageHandler(filters.FORWARDED, handle_aliexpress_link))
    
    # Add photo handler (may contain links in captions)
    application.add_handler(MessageHandler(filters.PHOTO, handle_aliexpress_link))

    # Run bot until Ctrl-C is pressed
    # Using run_polling without await to avoid event loop issues
    print("✅ Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    # Run bot directly without using asyncio
    # To avoid "This event loop is already running" issue
    main()
