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
        # Create a 'Human' browser context
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        stealth_sync(page) # This is the magic "Don't Block Me" button
        
        print(f"🚀 Stealth Hunt: BOISE {MAKE} {MODEL}")
        
        try:
            # Go directly to the search engine sub-page
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
            time.sleep(5)

            # Wait for the yard selector to appear
            page.wait_for_selector('select[name="location"]', timeout=20000)
            
            page.select_option('select[name="location"]', label="BOISE")
            time.sleep(2)
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(1)
            
            page.click('input[type="submit"]')
            print("Search submitted, waiting for results...")
            time.sleep(5)
            
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"🎯 SUCCESS! Found {len(found)} results.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 No {MODEL}s found in Boise today.")

        except Exception as e:
            print(f"❌ Site is still resisting: {e}")
            page.screenshot(path="blocked.png") # We'll see what it's showing us

        browser.close()

if __name__ == "__main__":
    main()
