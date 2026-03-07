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
        # We use a real-looking browser to avoid 'Bot Detected' screens
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Listening for Jalopy Jungle data packets...")
        
        # This list will hold the raw data we 'sniff' from the network
        raw_inventory = []

        # We tell the robot to 'listen' for the response from their database
        def handle_response(response):
            if "inventorylist.php" in response.url:
                print("Bingo! Data packet intercepted.")
                raw_inventory.append(response.text())

        page.on("response", handle_response)
        
        # Go to the main site which triggers the database call
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        time.sleep(10) # Give the database plenty of time to send the list

        found_matches = []
        if not raw_inventory:
            print("The website blocked the data packet. Trying fallback...")
            # Fallback: Just grab every bit of text on the page as a last resort
            content = page.content().upper()
            rows = page.locator("tr").all_inner_texts()
        else:
            # We take the intercepted data and turn it into rows
            rows = raw_inventory[0].split("</tr>")

        print(f"Analyzing {len(rows)} potential vehicles...")

        for text in rows:
            row_upper = text.upper()
            # Clean up HTML tags if they exist in the raw packet
            row_clean = row_upper.replace("<td>", " ").replace("</td>", " ")
            parts = row_clean.split()
            
            if len(parts) < 3: continue
            
            try:
                car_year = int(parts[0])
                if not (YEAR_START <= car_year <= YEAR_END): continue
                if MAKE and MAKE not in row_clean: continue
                if MODEL and MODEL not in row_clean: continue
                if LOCATION != "ALL" and LOCATION not in row_clean: continue
                
                found_matches.append(row_clean.strip())
            except:
                continue

        browser.close()

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Notification sent! Found {len(found_matches)} cars.")
        else:
            print(f"Scan finished. Scanned {len(rows)} rows, but nothing matched your search.")

if __name__ == "__main__":
    main()
