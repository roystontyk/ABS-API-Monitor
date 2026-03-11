import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone # Added timedelta and timezone

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Keywords for your property/construction interest
WATCHLIST = [
    "Building Activity", 
    "Building Approvals", 
    "Construction Work Done", 
    "Lending Indicators",
    "Consumer Price Index",
    "Dwellings",
    "Average Weekly Earnings",
    "Gross Domestic Product",
    "Business Indicators",
    "Labour Force",
    "Household Spending",
    "Producer Price Index",
    "Wage Price Index",
    "Property Price"
]

def log(msg):
    print(f"📊 [ABS LOG] {msg}", flush=True)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("Missing Telegram Secrets")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.status_code == 200
    except Exception as e:
        log(f"Telegram Error: {e}")
        return False

def check_abs_calendar():
    log("Scraping ABS Release Calendar...")
    url = "https://www.abs.gov.au/release-calendar/latest-releases"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        
        updates = []
        for link_tag in soup.find_all('a', href=True):
            text = link_tag.get_text().strip()
            
            if any(word.lower() in text.lower() for word in WATCHLIST):
                href = link_tag['href']
                full_url = f"https://www.abs.gov.au{href}" if href.startswith('/') else href
                
                entry = f"• <b>{html.escape(text)}</b>\n🔗 {full_url}"
                if entry not in updates:
                    updates.append(entry)
        
        return updates
    except Exception as e:
        log(f"Scraping Error: {e}")
        return []

def main():
    log("🚀 ABS Monitor Started")
    results = check_abs_calendar()
    
    if results:
        # --- AMENDED: Force Melbourne Time (UTC+11) ---
        melbourne_tz = timezone(timedelta(hours=11))
        today_melb = datetime.now(melbourne_tz)
        
        header = f"📈 <b>ABS Property & Construction Update</b>\n"
        header += f"<i>Checked: {today_melb.strftime('%d %b %Y')}</i>\n\n"
        # ----------------------------------------------
        
        message = header + "\n\n".join(results[:15])
        send_telegram(message)
        log(f"✅ Sent {len(results)} updates to Telegram.")
    else:
        log("🧐 No relevant updates found on the calendar today.")

if __name__ == "__main__":
    main()
