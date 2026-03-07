import os
import requests
from playwright.sync_api import sync_playwright

# Get inputs from the "Point and Click" dashboard
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
        
        # Wait for the actual data table to load
        page.wait_for_selector("table", timeout=20000)
        
        # Grab every row in the table
        rows = page.query_selector_all("tr")
        print(f"Found {len(rows)} total vehicles in yard.")
        
        found_matches = []

        for row in rows:
            text = row.inner_text().upper()
            columns = text.split('\t') # The site uses tabs to separate Year, Make, Model
            
            if len(columns) < 3: continue
            
            try:
                # Column 0 is usually the Year
                car_year = int(columns[0].strip())
                car_make = columns[1].strip()
                car_model = columns[2].strip()
                car_location = text # Search the whole line for location
                
                # 1. Check Year Range
                if not (YEAR_START <= car_year <= YEAR_END): continue
                
                # 2. Check Make (If provided)
                if MAKE and MAKE not in car_make: continue
                
                # 3. Check Model (If provided)
                if MODEL and MODEL not in car_model: continue
                
                # 4. Check Location
                if LOCATION != "ALL" and LOCATION not in car_location: continue
                
                found_matches.append(f"{car_year} {car_make} {car_model} ({text.split()[-2]})")
            
            except Exception:
                continue

        browser.close()

        if found_matches:
            # Send results in chunks if there are too many
            report = "\n".join(found_matches[:20]) 
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 MATCHES FOUND:\n{report}".encode('utf-8'))
            print(f"Success! Sent {len(found_matches)} matches to phone.")
        else:
            print("No matches found for those specific settings.")

if __name__ == "__main__":
    main()
