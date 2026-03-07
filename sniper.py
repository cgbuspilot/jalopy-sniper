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
        page = browser.new_page()
        
        print(f"Starting Multi-Yard Search for: {MAKE} {MODEL}")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(4)
        
        found_matches = []
        
        # We find the inner frame where the dropdowns live
        inventory_frame = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                inventory_frame = frame
                break
        
        if not inventory_frame:
            print("Could not find the inventory search form.")
            return

        # Get all location names from the dropdown (excluding the first 'Select' option)
        locations = inventory_frame.eval_on_selector_all(
            'select[name="location"] option', 
            'nodes => nodes.map(n => n.label).filter(l => l && !l.includes("Select"))'
        )
        
        print(f"Found {len(locations)} locations to check: {locations}")

        for loc in locations:
            print(f"--- Checking {loc} ---")
            try:
                # Select Location
                inventory_frame.select_option('select[name="location"]', label=loc)
                time.sleep(1)
                
                # Select Make
                if MAKE:
                    inventory_frame.select_option('select[name="make"]', label=MAKE)
                    time.sleep(1)
                
                # Select Model
                if MODEL:
                    inventory_frame.select_option('select[name="model"]', label=MODEL)
                    time.sleep(1)
                
                # Click Search
                inventory_frame.click('input[type="submit"]')
                time.sleep(3) # Wait for results to load for this yard

                # Grab results
                rows = inventory_frame.locator("tr").all_inner_texts()
                
                for text in rows:
                    if "YEAR" in text.upper() or len(text.split()) < 3: continue
                    
                    try:
                        car_year = int(text.split()[0])
                        if YEAR_START <= car_year <= YEAR_END:
                            match_entry = f"📍 {loc}: {text.strip()}"
                            found_matches.append(match_entry)
                            print(f"Hit found: {match_entry}")
                    except:
                        continue
            except Exception as e:
                print(f"Skipping {loc} due to error: {e}")
                continue

        browser.close()

        if found_matches:
            # Group results by location for the notification
            report = "\n".join(found_matches[:20])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER HITS ({len(found_matches)}):\n{report}".encode('utf-8'))
            print("Notification sent with all matches!")
        else:
            print("No matches found across any location.")

if __name__ == "__main__":
    main()
