import os
import requests
import time
import html
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The ABS Indicator API Endpoint
ABS_API_URL = "https://api.abs.gov.au/indicators/v1/indicators"

# Keywords for your specific property/construction interest
WATCHLIST = [
    "Building Activity", 
    "Building Approvals", 
    "Construction Work Done", 
    "Lending Indicators",
    "Consumer Price Index",
    "Residential Property Price"
]

def log(msg):
    print(f"📊 [ABS LOG] {msg}", flush=True)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("Missing Telegram Credentials")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=30)
    return r.status_code == 200

def check_abs_indicators():
    log("Fetching ABS Indicators...")
    try:
        # ABS API returns a list of all available indicators
        response = requests.get(ABS_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        found_updates = []
        
        # The API usually returns a list under 'data' or similar key
        # Adjust based on actual JSON structure of the v1/indicators endpoint
        indicators = data.get('data', [])
        
        for item in indicators:
            name = item.get('indicator_name', '')
            last_update = item.get('last_updated', 'Unknown')
            
            # Filter for your specific watchlist
            if any(word.lower() in name.lower() for word in WATCHLIST):
                # Clean up the name for display
                safe_name = html.escape(name)
                # ABS links usually follow a pattern based on indicator ID
                link = f"https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/{item.get('id', '')}"
                
                found_updates.append(
                    f"• <b>{safe_name}</b>\n"
                    f"📅 Updated: {last_update}\n"
                    f"🔗 <a href='{link}'>View Full Release</a>"
                )

        return found_updates
    except Exception as e:
        log(f"API Error: {e}")
        return []

def main():
    updates = check_abs_indicators()
    
    if updates:
        header = f"📈 <b>ABS Property & Construction Update</b>\n"
        header += f"<i>Checked at: {datetime.now().strftime('%d %b %Y %H:%M')}</i>\n\n"
        
        full_message = header + "\n\n".join(updates)
        
        # Check if the message is too long for Telegram
        if len(full_message) > 4000:
            full_message = full_message[:3900] + "\n\n... (Truncated)"
            
        send_telegram(full_message)
        log("✅ Update sent to Telegram")
    else:
        log("No matching indicators found today.")

if __name__ == "__main__":
    main()
