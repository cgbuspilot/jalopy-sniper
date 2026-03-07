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
        
        print(f"Opening Jalopy Jungle Main Page...")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # Give it a moment to breathe
        time.sleep(3)

        # THE SECRET SAUCE: We have to find the inner frame where the cars live
        # and look at the 'raw' text inside of it.
        found_matches = []
        vehicle_count = 0

        for frame in page.frames:
            # We want the frame that actually has vehicle data
            content = frame.content().upper()
            if "YEAR" in content and "MAKE" in content:
                rows = frame.locator("tr").all_inner_texts()
                vehicle_count = len(rows)
                
                for text in rows:
                    row_upper = text.upper()
                    # We look for the MAKE and MODEL anywhere in the line 
                    # This prevents the 'Make vs Model' confusion
                    if MAKE and MAKE not in row_upper: continue
                    if MODEL and MODEL not in row_upper: continue
                    if LOCATION != "ALL" and LOCATION not in row_upper: continue
                    
                    # Try to pull the year out of the start of the line
                    try:
                        parts = row_upper.split()
                        car_year = int(parts[0])
                        if not (YEAR_START <= car_year <= YEAR_END): continue
                        found_matches.append(text.strip())
                    except:
                        continue
        
        print(f"Robot scanned {vehicle_count} total vehicles.")
        browser.close()

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Sent {len(found_matches)} matches!")
        elif vehicle_count == 0:
            print("ERROR: Robot didn't see any vehicles. The website layout might have changed.")
        else:
            print(f"Scanned {vehicle_count} cars, but none matched your filters.")

if __name__ == "__main__":
    main()
