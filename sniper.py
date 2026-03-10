import os
import requests
import time
from playwright.sync_api import sync_playwright

MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "RAV4").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a real screen size
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print(f"🚀 Boise Deep-Scan: {MAKE} {MODEL}")
        # We use the main portal to ensure cookies/sessions are set correctly
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(5)

        # 1. FIND THE SEARCH FRAME
        target = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                target = frame
                break
        
        if not target:
            print("❌ Error: Search frame not found. Website might be down or changed.")
            browser.close()
            return

        try:
            # 2. SELECT BOISE
            print("Step 1: Selecting BOISE...")
            target.wait_for_selector('select[name="location"]')
            target.select_option('select[name="location"]', label="BOISE")
            
            # 3. WAIT FOR MAKE TO POPULATE
            print("Step 2: Waiting for 'Make' menu to wake up...")
            time.sleep(4) 
            target.wait_for_selector('select[name="make"]')
            target.select_option('select[name="make"]', label=MAKE)

            # 4. WAIT FOR MODEL TO POPULATE
            print(f"Step 3: Waiting for '{MODEL}' to appear...")
            time.sleep(4)
            target.wait_for_selector('select[name="model"]')
            target.select_option('select[name="model"]', label=MODEL)

            # 5. CLICK SEARCH
            print("Step 4: Submitting search...")
            target.click('input[type="submit"]')
            time.sleep(6) # Give the result table plenty of time to render

            # 6. SCRAPE
            rows = target.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"✅ SUCCESS! Found {len(found)} results.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 No cars found in the result table.")
                
        except Exception as e:
            print(f"⚠️ Search failed: {e}")

        browser.close()

if __name__ == "__main__":
    main()
