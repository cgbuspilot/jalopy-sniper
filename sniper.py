import os
import requests
import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "YARIS").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # Launching with specific arguments to look less like a bot
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        # We tell the site we are a standard Windows Desktop user
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        stealth_sync(page) # Apply stealth patches
        
        print(f"🕵️ Stealth Hunt: BOISE {MAKE} {MODEL}")
        
        try:
            # Go to the direct inventory engine
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle", timeout=60000)
            
            # Wait a random amount of time to mimic a human 'thinking'
            time.sleep(random.uniform(3.0, 6.0))

            # Look for the location menu
            print("Scanning for search form...")
            page.wait_for_selector('select[name="location"]', timeout=30000)
            
            # Human-like selection with small pauses
            page.select_option('select[name="location"]', label="BOISE")
            time.sleep(random.uniform(1.5, 3.0))
            
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(random.uniform(1.5, 3.0))
            
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(random.uniform(1.0, 2.0))
            
            # Click the search button
            page.click('input[type="submit"]')
            print("Search sent! Waiting for results...")
            time.sleep(7) # Give it plenty of time to load the table
            
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"🎯 BINGO! Found {len(found)} matching vehicles.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 Search finished: No {MODEL}s currently in the yard.")

        except Exception as e:
            print(f"⚠️ Security wall still up: {e}")
            # If it fails, this will help us see WHY (screenshot)
            page.screenshot(path="final_attempt_error.png")

        browser.close()

if __name__ == "__main__":
    main()
