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
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print(f"🚀 Boise Precision Hunt: {MAKE} {MODEL}")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(5)

        # FIND THE RIGHT WINDOW
        target = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                target = frame
                break
        
        if not target:
            print("❌ Critical Error: Could not find the search window.")
            browser.close()
            return

        try:
            # STEP 1: SELECT BOISE
            print("Selecting BOISE...")
            target.select_option('select[name="location"]', label="BOISE")
            time.sleep(4) # Let the 'Make' list load

            # STEP 2: SELECT MAKE (With Retry Logic)
            print(f"Trying to find {MAKE} in the list...")
            # We wait up to 15 seconds specifically for the TOYOTA option to exist
            target.wait_for_selector(f'select[name="make"] option:has-text("{MAKE}")', timeout=15000)
            target.select_option('select[name="make"]', label=MAKE)
            time.sleep(4) # Let the 'Model' list load

            # STEP 3: SELECT MODEL
            print(f"Trying to find {MODEL} in the list...")
            target.wait_for_selector(f'select[name="model"] option:has-text("{MODEL}")', timeout=15000)
            target.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            # STEP 4: CLICK SEARCH
            print("Submitting search...")
            target.click('input[type="submit"]')
            time.sleep(6) 

            # STEP 5: CAPTURE THE PRIZE
            rows = target.locator("tr").all_inner_texts()
            # Look for rows that contain both Toyota AND Rav4
            found = [r.strip() for r in rows if MAKE in r.upper() and MODEL in r.upper()]
            
            if found:
                print(f"✅ BINGO! Found {len(found)} cars.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 No cars found in the table. The yard might be out, or the scan failed.")
                
        except Exception as e:
            print(f"⚠️ Hunt interrupted: {e}")

        browser.close()

if __name__ == "__main__":
    main()
