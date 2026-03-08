import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs
MAKE = os.getenv("INPUT_MAKE", "").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "").strip().upper()
YEAR_START = int(os.getenv("INPUT_YEAR_START", 1900))
YEAR_END = int(os.getenv("INPUT_YEAR_END", 2026))
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a high-res window so menus don't collapse into 'mobile mode'
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🚀 Starting Multi-Yard Search for: {MAKE} {MODEL}")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle", timeout=60000)
        
        # Wait for the frame to actually exist
        page.wait_for_selector("iframe", timeout=20000)
        time.sleep(5) 
        
        found_matches = []
        
        # Look for the frame containing 'location'
        target_frame = None
        for frame in page.frames:
            if "inventory" in frame.url or frame.query_selector('select[name="location"]'):
                target_frame = frame
                break
        
        if not target_frame:
            print("❌ Error: Search form is still hidden. Trying a deep-page scan...")
            target_frame = page # Fallback to main page

        try:
            # Get all locations
            locations = target_frame.eval_on_selector_all(
                'select[name="location"] option', 
                'nodes => nodes.map(n => n.label).filter(l => l && !l.includes("Select"))'
            )
            print(f"✅ Found {len(locations)} yards: {locations}")

            for loc in locations:
                print(f"🔍 Checking {loc}...")
                target_frame.select_option('select[name="location"]', label=loc)
                time.sleep(2)
                
                if MAKE:
                    target_frame.select_option('select[name="make"]', label=MAKE)
                    time.sleep(1)
                if MODEL:
                    # Some sites require a second to load the model list after picking the make
                    target_frame.select_option('select[name="model"]', label=MODEL)
                    time.sleep(1)
                
                target_frame.click('input[type="submit"]')
                time.sleep(4) 

                rows = target_frame.locator("tr").all_inner_texts()
                for text in rows:
                    if "YEAR" in text.upper() or len(text.split()) < 3: continue
                    try:
                        car_year = int(text.split()[0])
                        if YEAR_START <= car_year <= YEAR_END:
                            match_entry = f"📍 {loc}: {text.strip()}"
                            found_matches.append(match_entry)
                            print(f"✨ MATCH: {match_entry}")
                    except:
                        continue
        except Exception as e:
            print(f"⚠️ Encountered a snag: {e}")

        browser.close()

        if found_matches:
            report = "\n".join(found_matches[:20])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER HITS ({len(found_matches)}):\n{report}".encode('utf-8'))
            print("📢 Notification sent!")
        else:
            print("🏁 Scan complete. No matches found today.")

if __name__ == "__main__":
    main()
