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
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1")
        page = context.new_page()
        
        print(f"🚀 Boise Test: {MAKE} {MODEL} (Filtering years: {YEAR_START}-{YEAR_END})")
        page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
        time.sleep(5)

        try:
            # 1. Select BOISE
            print("Selecting Boise...")
            page.select_option('select[name="location"]', label="BOISE")
            time.sleep(2)

            # 2. Select Make
            print(f"Selecting {MAKE}...")
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)

            # 3. Select Model
            print(f"Selecting {MODEL}...")
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            # 4. Search (The site doesn't ask for years here!)
            page.click('input[type="submit"]')
            time.sleep(5)

            # 5. Extract and Filter results by year locally
            rows = page.locator("tr").all_inner_texts()
            found_matches = []
            
            for text in rows:
                parts = text.split()
                if "YEAR" in text.upper() or len(parts) < 3: continue
                
                try:
                    car_year = int(parts[0])
                    # We check the year here in our own code!
                    if YEAR_START <= car_year <= YEAR_END:
                        found_matches.append(f"📍 BOISE: {text.strip()}")
                except:
                    continue

            if found_matches:
                print(f"✅ Found {len(found_matches)} results within your year range!")
                report = "\n".join(found_matches)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 No cars found matching that year range.")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")

        browser.close()

if __name__ == "__main__":
    main()
