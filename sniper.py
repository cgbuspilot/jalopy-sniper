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
        # 1. Launch a more stable browser instance
        browser = p.chromium.launch(headless=True)
        # 2. Use a specific window size to look like a real desktop
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"Connecting to Jalopy Jungle...")
            # Go to the main site first to establish a session
            page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            # Now go to the list
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            # Look for table rows
            rows = page.locator("tr").all_inner_texts()
            print(f"Robot successfully reached the database. Rows found: {len(rows)}")
            
            found_matches = []

            for text in rows:
                row_upper = text.upper()
                parts = row_upper.split()
                if len(parts) < 3: continue
                
                try:
                    # Check if the first part is a 4-digit year
                    car_year = int(parts[0])
                    if not (1900 <= car_year <= 2030): continue
                    
                    # Apply User Filters
                    if not (YEAR_START <= car_year <= YEAR_END): continue
                    if MAKE and MAKE not in row_upper: continue
                    if MODEL and MODEL not in row_upper: continue
                    if LOCATION != "ALL" and LOCATION not in row_upper: continue
                    
                    found_matches.append(text.strip())
                except:
                    continue

            if found_matches:
                summary = "\n".join(found_matches[:15])
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                              data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
                print("Notification sent!")
            else:
                print("Scan complete. No matches found for these filters.")

        except Exception as e:
            print(f"Robot encountered a snag: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
