import os
import requests
import sys
from playwright.sync_api import sync_playwright

# GitHub inputs come in as "Environment Variables"
MAKE = os.getenv("INPUT_MAKE", "").upper()
MODEL = os.getenv("INPUT_MODEL", "").upper()
YEAR_START = int(os.getenv("INPUT_YEAR_START", 1900))
YEAR_END = int(os.getenv("INPUT_YEAR_END", 2026))
LOCATION = os.getenv("INPUT_LOCATION", "ALL").upper()
NTFY_TOPIC = "Jalopy-Sniper"

def get_inventory():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://inventory.pickapartjalopyjungle.com/")
        page.wait_for_selector("tr", timeout=15000)
        
        rows = page.query_selector_all("tr")
        data = []
        for row in rows:
            text = row.inner_text().upper().replace('\t', ' ')
            # Example text: "2005 TOYOTA TUNDRA BOISE 03/05/2026"
            data.append(text)
        
        browser.close()
        return data

def main():
    print(f"Searching for: {YEAR_START}-{YEAR_END} {MAKE} {MODEL} at {LOCATION}")
    listings = get_inventory()
    found = []

    for item in listings:
        parts = item.split()
        if len(parts) < 3: continue
        
        try:
            car_year = int(parts[0])
            # Check Year Range
            if not (YEAR_START <= car_year <= YEAR_END): continue
            # Check Make
            if MAKE not in item: continue
            # Check Model
            if MODEL not in item: continue
            # Check Location
            if LOCATION != "ALL" and LOCATION not in item: continue
            
            found.append(item)
        except ValueError:
            continue

    if found:
        msg = f"🎯 SNIPER HIT!\n" + "\n".join(found)
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))
        print("Alert sent!")
    else:
        print("Nothing found today.")

if __name__ == "__main__":
    main()
