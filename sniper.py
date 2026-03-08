import os
import requests
import time
from playwright.sync_api import sync_playwright

# Safer input handling
MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "RAV4").strip().upper()
# If year is blank, use wide defaults
YEAR_START = int(os.getenv("INPUT_YEAR_START") or 1900)
YEAR_END = int(os.getenv("INPUT_YEAR_END") or 2026)
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"🚀 Boise Test: {MAKE} {MODEL} ({YEAR_START}-{YEAR_END})")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(5)

        target = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                target = frame
                break
        
        if not target:
            print("❌ Error: Search form not found.")
            browser.close()
            return

        try:
            print("Selecting BOISE...")
            target.select_option('select[name="location"]', label="BOISE")
            time.sleep(2)

            print(f"Selecting {MAKE}...")
            target.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)

            print(f"Selecting {MODEL}...")
            target.select_option('select[name="model"]', label=MODEL)
            time.sleep(1)

            target.click('input[type="submit"]')
            time.sleep(5)

            rows = target.locator("tr").all_inner_texts()
            found_matches = []
            
            for text in rows:
                parts = text.split()
                if "YEAR" in text.upper() or len(parts) < 3: continue
                
                try:
                    car_year = int(parts[0])
                    if YEAR_START <= car_year <= YEAR_END:
                        found_matches.append(f"📍 BOISE: {text.strip()}")
                except:
                    continue

            if found_matches:
                print(f"✅ Found {len(found_matches)} vehicles.")
                report = "\n".join(found_matches)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 SNIPER HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 No matches seen in the results table.")

        except Exception as e:
            print(f"⚠️ Error during selection: {e}")

        browser.close()

if __name__ == "__main__":
    main()
