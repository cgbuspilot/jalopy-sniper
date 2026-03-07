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
        time.sleep(5)

        found_matches = []
        vehicle_count = 0

        # We need to find the right frame that contains the inventory
        for frame in page.frames:
            try:
                # Check if this frame has the location dropdown
                dropdown = frame.query_selector('select[name="location"]')
                if dropdown:
                    print("Found the inventory frame! Forcing 'ALL' locations...")
                    frame.select_option('select[name="location"]', label="ALL")
                    time.sleep(5) # Wait for table to populate
                    
                    rows = frame.locator("tr").all_inner_texts()
                    vehicle_count = len(rows)
                    
                    for text in rows:
                        row_upper = text.upper()
                        parts = row_upper.split()
                        if len(parts) < 3: continue
                        
                        try:
                            car_year = int(parts[0])
                            if not (YEAR_START <= car_year <= YEAR_END): continue
                            if MAKE and MAKE not in row_upper: continue
                            if MODEL and MODEL not in row_upper: continue
                            if LOCATION != "ALL" and LOCATION not in row_upper: continue
                            
                            found_matches.append(text.strip())
                        except:
                            continue
                    break # We found the right frame, no need to check others
            except Exception as e:
                continue

        browser.close()

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Success! Sent {len(found_matches)} matches.")
        else:
            print(f"Scanned {vehicle_count} rows. No matches found.")

if __name__ == "__main__":
    main()
