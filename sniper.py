import os
import requests
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "YARIS").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        stealth_sync(page) 
        
        print(f"🚀 Stealth Hunt: BOISE {MAKE} {MODEL}")
        try:
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
            time.sleep(5)
            page.wait_for_selector('select[name="location"]', timeout=20000)
            page.select_option('select[name="location"]', label="BOISE")
            time.sleep(2)
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)
            page.select_option('select[name="model"]', label=MODEL)
            page.click('input[type="submit"]')
            time.sleep(5)
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            if found:
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n" + "\n".join(found))
                print("✅ Found results and sent notification!")
            else:
                print(f"🏁 No {MODEL}s found.")
        except Exception as e:
            print(f"❌ Error: {e}")
        browser.close()

if __name__ == "__main__":
    main()
