import os, requests, html, sys
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Dataflows for your property/construction interests
# These IDs are standard across the ABS system
TARGET_DATAFLOWS = {
    "BUILDING_APPROV": "Building Approvals",
    "RES_PROP_PRICE": "Residential Property Price Indexes",
    "CONSTRUCTION": "Construction Work Done",
    "CPI": "Consumer Price Index",
    "LENDING": "Lending Indicators",
    "RETAIL": "Retail Trade"
}

def log(msg):
    print(f"📊 [ABS LOG] {msg}", flush=True)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("Missing Telegram Secrets")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.status_code == 200
    except Exception as e:
        log(f"Telegram Error: {e}")
        return False

def check_abs():
    log("Checking ABS Data API...")
    # New reliable endpoint for data discovery
    api_url = "https://data.api.abs.gov.au/rest/dataflow/ABS/all?detail=allstubs"
    headers = {"Accept": "application/json"}
    
    updates = []
    try:
        r = requests.get(api_url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Dig into the SDMX-JSON structure to find our dataflows
        dataflows = data.get('data', {}).get('dataflows', [])
        
        for df in dataflows:
            df_id = df.get('id')
            if df_id in TARGET_DATAFLOWS:
                name = TARGET_DATAFLOWS[df_id]
                version = df.get('version', '1.0.0')
                # Construct a clean link to the ABS website for that topic
                link = f"https://www.abs.gov.au/statistics/search?search_text={df_id}"
                
                updates.append(
                    f"• <b>{name}</b> ({df_id})\n"
                    f"🏷️ Version: {version}\n"
                    f"🔗 <a href='{link}'>View Release</a>"
                )
        
        return updates
    except Exception as e:
        log(f"ABS API Error: {e}")
        return []

def main():
    log("🚀 Script Started")
    results = check_abs()
    
    if results:
        header = f"📈 <b>ABS Property & Construction Update</b>\n"
        header += f"<i>Checked: {datetime.now().strftime('%d %b %Y %H:%M')}</i>\n\n"
        send_telegram(header + "\n\n".join(results))
        log(f"✅ Sent {len(results)} updates.")
    else:
        log("🧐 No matching dataflows found.")

if __name__ == "__main__":
    main()
