import os
import requests
import time
from playwright.sync_api import sync_playwright

# Locked-in Search Terms
LOC = os.getenv("INPUT_LOC", "BOISE")
MAKE = os.getenv("INPUT_MAKE", "TOYOTA")
MODEL = os.getenv("INPUT_MODEL", "YARIS")
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"🚀 Hunting for: {LOC} {MAKE} {MODEL}")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(5)

        # Find the search frame
        target = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                target = frame
                break
        
        if not target:
            print("❌ Failure: Search form not found. Website is blocking the bot.")
            browser.close()
            return

        try:
            # Step 1: Select Location
            print(f"Selecting {LOC}...")
            target.select_option('select[name="location"]', label=LOC)
            time.sleep(3)

            # Step 2: Select Make
            print(f"Selecting {MAKE}...")
            target.select_option('select[name="make"]', label=MAKE)
            time.sleep(3)

            # Step 3: Select Model
            print(f"Selecting {MODEL}...")
            target.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            # Step 4: Click Search
            target.click('input[type="submit"]')
            time.sleep(5)

            # Step 5: Check Results
            rows = target.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"✅ Found {len(found)} results!")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 No {MODEL}s found in {LOC} today.")

        except Exception as e:
            print(f"⚠️ Error: {e}")

        browser.close()

if __name__ == "__main__":
    main()
