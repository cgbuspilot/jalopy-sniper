import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs
MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "RAV4").strip().upper()
YEAR_START = int(os.getenv("INPUT_YEAR_START") or 1900)
YEAR_END = int(os.getenv("INPUT_YEAR_END") or 2026)
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print(f"🚀 Targeted Boise Search: {MAKE} {MODEL}...")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # Look for the inventory frame specifically
        inventory_frame = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                inventory_frame = frame
                break
        
        if not inventory_frame:
            print("❌ Error: Could not find search form frame.")
            browser.close()
            return

        try:
            # 1. Select BOISE
            print("Selecting Location: BOISE...")
            inventory_frame.select_option('select[name="location"]', label="BOISE")
            time.sleep(3) # Wait for 'Make' dropdown to refresh its contents

            # 2. Select TOYOTA
            print(f"Selecting Make: {MAKE}...")
            inventory_frame.select_option('select[name="make"]', label=MAKE)
            time.sleep(3) # Wait for 'Model' dropdown to refresh its contents

            # 3. Select RAV4
            print(f"Selecting Model: {MODEL}...")
            inventory_frame.select_option('select[name="model"]', label=MODEL)
            time.sleep(1)

            # 4. Click Search
            inventory_frame.click('input[type="submit"]')
            print("Search submitted. Waiting for table...")
            time.sleep(5)

            # 5. Scrape Results
            rows = inventory_frame.locator("tr").all_inner_texts()
            found_matches = []
            
            for text in rows:
                parts = text.split()
                if "YEAR" in text.upper() or len(parts) < 3:
                    continue
                
                try:
                    car_year = int(parts[0])
                    if YEAR_START <= car_year <= YEAR_END:
                        found_matches.append(f"📍 BOISE: {text.strip()}")
                except:
                    continue

            if found_matches:
                print(f"✅ SUCCESS: Found {len(found_matches)} vehicles in Boise.")
                report = "\n".join(found_matches)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                              data=f"🎯 BOISE TEST HIT ({len(found_matches)}):\n{report}".encode('utf-8'))
            else:
                print("🏁 Finished search, but no cars were found in the table results.")

        except Exception as e:
            print(f"⚠️ snags found: {e}")

        browser.close()

if __name__ == "__main__":
    main()
