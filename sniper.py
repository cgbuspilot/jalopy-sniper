import requests
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Locked-in for our test
LOC = "BOISE"
MAKE = "TOYOTA"
MODEL = "YARIS"
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # Launching with a real-looking browser signature
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Apply the cloaking device
        stealth_sync(page) 
        
        print(f"🕵️ Ghost Hunt Starting: {LOC} {MAKE} {MODEL}")
        
        try:
            # Go directly to the search tool
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            # Wait for the location menu (this is where we were failing)
            print("Looking for search menu...")
            page.wait_for_selector('select[name="location"]', timeout=30000)
            
            # Select Yard
            page.select_option('select[name="location"]', label=LOC)
            time.sleep(3)
            
            # Select Make
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(3)
            
            # Select Model
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)
            
            # Click Search
            page.click('input[type="submit"]')
            print("Search submitted!")
            time.sleep(5)
            
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"🎯 BINGO! Found {len(found)} results.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 Finished. No {MODEL}s found in {LOC} today.")

        except Exception as e:
            print(f"❌ Still blocked: {e}")
            page.screenshot(path="blocked_view.png")

        browser.close()

if __name__ == "__main__":
    main()
