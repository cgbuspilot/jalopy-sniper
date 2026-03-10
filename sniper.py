import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs
MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "RAV4").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # We tell the site we are an iPhone—this often forces a simpler website layout
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1")
        page = context.new_page()
        
        print(f"🚀 Boise Test: {MAKE} {MODEL}")
        # DIRECT ACCESS to the inventory engine
        page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
        time.sleep(5)

        try:
            # 1. Select BOISE
            print("Looking for Boise...")
            page.select_option('select[name="location"]', label="BOISE")
            time.sleep(2)

            # 2. Select Make
            print(f"Looking for {MAKE}...")
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)

            # 3. Select Model
            print(f"Looking for {MODEL}...")
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            # 4. Search
            page.click('input[type="submit"]')
            time.sleep(5)

            # 5. Extract results
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"✅ Found {len(found)} results!")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 No results found in the table.")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            page.screenshot(path="error.png") # This saves a picture of what went wrong

        browser.close()

if __name__ == "__main__":
    main()
