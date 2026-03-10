import requests
import time
from playwright.sync_api import sync_playwright

# Hard-coded for our test
LOC = "BOISE"
MAKE = "TOYOTA"
MODEL = "YARIS"
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # Launch with a fake 'User Agent' so the site thinks we are on Windows
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🚀 Stealth Hunt Starting: {LOC} {MAKE} {MODEL}")
        
        # Go to the direct inventory page instead of the landing page
        page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="domcontentloaded")
        time.sleep(5)

        try:
            # 1. Select Location
            print("Looking for Location menu...")
            page.wait_for_selector('select[name="location"]', timeout=15000)
            page.select_option('select[name="location"]', label=LOC)
            time.sleep(3)

            # 2. Select Make
            print(f"Selecting {MAKE}...")
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(3)

            # 3. Select Model
            print(f"Selecting {MODEL}...")
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            # 4. Search
            page.click('input[type="submit"]')
            time.sleep(5)

            # 5. Scrape
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"✅ SUCCESS! Found {len(found)} cars.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 Search finished. No {MODEL}s found.")

        except Exception as e:
            print(f"❌ Site Blocked the Bot: {e}")
            page.screenshot(path="blocked.png")

        browser.close()

if __name__ == "__main__":
    main()
