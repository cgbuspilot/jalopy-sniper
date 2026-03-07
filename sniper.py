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
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        print(f"Opening Jalopy Jungle...")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # 1. Wait extra time for the JavaScript to finish building the table
        time.sleep(5) 
        
        # 2. Find all table rows that actually contain car data
        # Most of their cars are inside 'td' tags
        rows = page.query_selector_all("tr")
        print(f"Robot successfully scanned {len(rows)} rows.")
        
        found_matches = []

        for row in rows:
            text = row.inner_text().upper()
            # Split by newlines or tabs to get individual pieces
            parts = text.split()
            
            if len(parts) < 3: continue
            
            try:
                # In their list, Year is usually the first thing
                car_year = int(parts[0])
                
                # Check Year Range
                if not (YEAR_START <= car_year <= YEAR_END): continue
                # Check Make
                if MAKE and MAKE not in text: continue
                # Check Model
                if MODEL and MODEL not in text: continue
                # Check Location
                if LOCATION != "ALL" and LOCATION not in text: continue
                
                found_matches.append(text.replace('\t', ' ').strip())
            except:
                continue

        browser.close()

        if found_matches:
            # Send the first 10 matches so the text isn't too long
            summary = "\n".join(found_matches[:10])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER HIT:\n{summary}".encode('utf-8'))
            print(f"Sent {len(found_matches)} matches to your phone!")
        else:
            print("No matches found in the scanned rows.")

if __name__ == "__main__":
    main()
