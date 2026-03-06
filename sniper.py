import os
import requests
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# Add or remove cars here. Keep them in quotes and all CAPS.
TARGET_CARS = ["2005 TOYOTA TUNDRA", "1998 HONDA CIVIC", "2001 JEEP CHEROKEE"]
NTFY_TOPIC = "Jalopy-Sniper" 
# ---------------------

def get_inventory():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://inventory.pickapartjalopyjungle.com/")
        # This waits for the car list to actually load
        page.wait_for_selector("tr", timeout=10000)
        rows = page.query_selector_all("tr")
        inventory = [row.inner_text().upper() for row in rows]
        browser.close()
        return inventory

def main():
    print("Scouting the yard...")
    listings = get_inventory()
    found_matches = []

    for car in listings:
        if any(target in car for target in TARGET_CARS):
            found_matches.append(car)

    if found_matches:
        message = "🎯 JALOPY SNIPER MATCH:\n" + "\n".join(found_matches)
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'))
        print("Alert sent!")
    else:
        print("No matches today.")

if __name__ == "__main__":
    main()
