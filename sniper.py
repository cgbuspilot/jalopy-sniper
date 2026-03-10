import os
import requests
import time
from playwright.sync_api import sync_playwright

# Locked-in for our "First Win" test
LOC = os.getenv("INPUT_LOC", "BOISE")
MAKE = os.getenv("INPUT_MAKE", "TOYOTA")
MODEL = os.getenv("INPUT_MODEL", "YARIS")
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # We look like a real Windows user to avoid the bot-block
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🚀 Targeting: {LOC} {MAKE} {MODEL}...")
        
        try:
            # Go directly to the search tool
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
            time.sleep(5)

            # Wait for the search box to appear
            print("Checking for search form...")
            page.wait_for_selector('select[name="location"]', timeout=15000)
            
            # Select Yard
            page.select_option('select[name="location"]', label=LOC)
            time.sleep(2)
            
            # Select Make
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)
            
            # Select Model
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(1)
            
            # Click Search
            page.click('input[type="submit"]')
            time.sleep(5)
            
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"🎯 SUCCESS! Found {len(found)} results.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 Finished. No {MODEL}s found in {LOC}.")

        except Exception as e:
            print(f"❌ Still blocked or timed out: {e}")
            page.screenshot(path="fail_view.png")

        browser.close()

if __name__ == "__main__":
    main()
