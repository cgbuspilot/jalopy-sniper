import os
import requests
import time
from playwright.sync_api import sync_playwright

# Inputs from Dashboard
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
        
        # WE ARE GOING DIRECTLY TO THE DATA SOURCE NOW
        print(f"Connecting directly to Inventory Server...")
        page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
        
        # Wait for the table to exist
        page.wait_for_selector("tr", timeout=15000)
        
        rows = page.query_selector_all("tr")
        print(f"Success! Found {len(rows)} total rows in the database.")
        
        found_matches = []

        for row in rows:
            text = row.inner_text().upper()
            parts = text.split()
            
            # Skip header or empty rows
            if len(parts) < 3 or "YEAR" in parts[0]: continue
            
            try:
                car_year = int(parts[0])
                
                # Apply your Point-and-Click Filters
                if not (YEAR_START <= car_year <= YEAR_END): continue
                if MAKE and MAKE not in text: continue
                if MODEL and MODEL not in text: continue
                if LOCATION != "ALL" and LOCATION not in text: continue
                
                # Clean up the text for the notification
                clean_text = " ".join(parts)
                found_matches.append(clean_text)
            except:
                continue

        browser.close()

        if found_matches:
            # Send the top 15 results
            summary = "\n".join(found_matches[:15])
            count = len(found_matches)
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({count} Hits):\n{summary}".encode('utf-8'))
            print(f"Notification sent with {count} vehicles!")
        else:
            print("The list was found, but no cars matched your specific filters.")

if __name__ == "__main__":
    main()
