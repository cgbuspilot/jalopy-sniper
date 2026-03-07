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
        
        print("Opening Jalopy Jungle...")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # Give the site a long time to 'hydrate' the data
        time.sleep(10)

        found_matches = []
        total_rows_seen = 0

        # Loop through every frame to find the hidden table
        for frame in page.frames:
            try:
                # Try to find all table rows in this frame
                rows = frame.locator("tr").all_inner_texts()
                if len(rows) < 5: continue # Skip frames that are just headers or ads
                
                print(f"Found a data table with {len(rows)} rows!")
                total_rows_seen = len(rows)

                for text in rows:
                    row_upper = text.upper()
                    
                    # Filtering
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

        browser.close()

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Success! {len(found_matches)} matches found.")
        else:
            print(f"Scanned {total_rows_seen} rows. No matches for your search.")

if __name__ == "__main__":
    main()
