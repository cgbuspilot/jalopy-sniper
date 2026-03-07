import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs from your Dashboard
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
        
        # Give the inner frame time to load
        time.sleep(8) 
        
        # This is the secret sauce: looking inside the frame
        found_matches = []
        all_text = ""
        
        # Get all frames and look for the one with the car list
        for frame in page.frames:
            try:
                # Get every row inside every frame found
                rows = frame.query_selector_all("tr")
                if len(rows) > 5: # If we found more than just a header
                    print(f"Found the car list! Scanning {len(rows)} vehicles...")
                    for row in rows:
                        text = row.inner_text().upper()
                        parts = text.split()
                        if len(parts) < 3: continue
                        
                        try:
                            car_year = int(parts[0])
                            # Filters
                            if not (YEAR_START <= car_year <= YEAR_END): continue
                            if MAKE and MAKE not in text: continue
                            if MODEL and MODEL not in text: continue
                            if LOCATION != "ALL" and LOCATION not in text: continue
                            
                            found_matches.append(text.replace('\t', ' ').strip())
                        except:
                            continue
            except:
                continue

        browser.close()

        if found_matches:
            # Send the top 10 matches
            summary = "\n".join(found_matches[:10])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER HIT:\n{summary}".encode('utf-8'))
            print(f"Sent {len(found_matches)} matches to your phone!")
        else:
            print("No matches found in the car list.")

if __name__ == "__main__":
    main()
