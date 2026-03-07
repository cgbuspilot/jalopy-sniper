import os
import requests
import json
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
        
        print("Interacting with Jalopy Jungle server...")
        
        # We go to the page and wait for the 'XHR' (the data packet)
        try:
            page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
            
            # This is the 'Nuclear Option': We grab the raw HTML of the inventory container
            # specifically looking for the table body after it hydrates
            page.wait_for_selector("tbody", timeout=15000)
            rows = page.locator("tr").all_inner_texts()
            
            print(f"Intercepted {len(rows)} data rows.")
            
            found_matches = []
            for text in rows:
                row_upper = text.upper()
                if len(row_upper.split()) < 3: continue
                
                # Filter Logic
                if MAKE and MAKE not in row_upper: continue
                if MODEL and MODEL not in row_upper: continue
                if LOCATION != "ALL" and LOCATION not in row_upper: continue
                
                try:
                    car_year = int(row_upper.split()[0])
                    if not (YEAR_START <= car_year <= YEAR_END): continue
                    found_matches.append(text.strip())
                except:
                    continue

            if found_matches:
                summary = "\n".join(found_matches[:15])
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                              data=f"🎯 SNIPER HIT ({len(found_matches)}):\n{summary}".encode('utf-8'))
                print("Notification sent!")
            else:
                print(f"Scanned {len(rows)} cars. No matches found.")

        except Exception as e:
            print(f"Snagged: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
