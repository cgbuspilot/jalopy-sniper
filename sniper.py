import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs
MAKE = os.getenv("INPUT_MAKE", "").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "").strip().upper()
YEAR_START = int(os.getenv("INPUT_YEAR_START", 1900))
YEAR_END = int(os.getenv("INPUT_YEAR_END", 2026))
LOCATION = os.getenv("INPUT_LOCATION", "ALL").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Opening Jalopy Jungle...")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # 1. Give the site 5 seconds to load the basic layout
        time.sleep(5)

        # 2. SCROLL DOWN to trigger the database to load
        print("Scrolling to load vehicles...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5) # Wait for cars to appear after scroll

        found_matches = []
        vehicle_count = 0

        # 3. Look at the main page AND all frames (windows) for car data
        all_frames = page.frames
        for frame in all_frames:
            try:
                # Find all table rows
                rows = frame.locator("tr").all_inner_texts()
                if len(rows) <= 1: continue # Skip if it's just a header
                
                vehicle_count += len(rows)
                for text in rows:
                    row_upper = text.upper()
                    
                    # Basic filters
                    if MAKE and MAKE not in row_upper: continue
                    if MODEL and MODEL not in row_upper: continue
                    if LOCATION != "ALL" and LOCATION not in row_upper: continue
                    
                    try:
                        parts = row_upper.split()
                        car_year = int(parts[0])
                        if not (YEAR_START <= car_year <= YEAR_END): continue
                        found_matches.append(text.strip())
                    except:
                        continue
            except:
                continue
        
        print(f"Robot successfully scanned {vehicle_count} total vehicles.")
        browser.close()

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Success! Notification sent with {len(found_matches)} cars.")
        else:
            print(f"Scanned {vehicle_count} cars, but none matched your search.")

if __name__ == "__main__":
    main()
