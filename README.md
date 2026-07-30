[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E41CVWBU)

# AliExpress Affiliate Bot

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E41CVWBU)

An English Telegram bot that helps users get AliExpress affiliate links and product information quickly from shared product URLs.

## Features
- Extracts AliExpress product links from messages
- Generates affiliate links for different promo types
- Fetches product details such as price, rating, and store information
- Sends product images and offers directly in Telegram

## Requirements
- Python 3.9+
- Telegram Bot Token
- AliExpress API credentials
- Optional: template image file for custom media output

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/bitt-ar/aliexpress-affiliate-bot.git
   cd AliExpress-Affiliate-Bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your environment variables:
   ```env
   TRACKING_ID=your_tracking_id
   KEY=your_api_key
   SECRET=your_api_secret
   TELEGRAM_TOKEN=your_telegram_bot_token
   COUNTRY_CODE=US
   CURRENCY=USD
   LOADING_STICKER=optional_sticker_id
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Usage
- Start the bot in Telegram with the `/start` command
- Send an AliExpress product link directly
- Forward a message containing an AliExpress link

## Notes
- Make sure the link is valid and belongs to AliExpress
- The bot will reply with product information and available affiliate offers

## Support
If you want to support this project, you can donate here:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E41CVWBU)