import os
import requests
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a real browser signature to avoid being blocked
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print("🚀 Testing Boise Yard: Toyota RAV4")
        page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle")
        
        # Give the site a few seconds to load the basic layout
        time.sleep(5)

        # We search inside all frames to find where the search tools live
        target = None
        for frame in page.frames:
            if frame.query_selector('select[name="location"]'):
                target = frame
                break
        
        if not target:
            print("❌ Error: Could not find the search menus.")
            browser.close()
            return

        try:
            # 1. SELECT LOCATION (BOISE)
            print("Selecting Location: BOISE...")
            target.select_option('select[name="location"]', label="BOISE")
            time.sleep(2) # Essential: wait for 'Make' to update

            # 2. SELECT MAKE (TOYOTA)
            print("Selecting Make: TOYOTA...")
            target.select_option('select[name="make"]', label="TOYOTA")
            time.sleep(2) # Essential: wait for 'Model' to update

            # 3. SELECT MODEL (RAV4)
            print("Selecting Model: RAV4...")
            target.select_option('select[name="model"]', label="RAV4")
            time.sleep(1)

            # 4. CLICK SEARCH
            print("Clicking Search...")
            target.click('input[type="submit"]')
            time.sleep(5) # Wait for the table to refresh

            # 5. SCRAPE RESULTS
            rows = target.locator("tr").all_inner_texts()
            found_matches = []
            
            for text in rows:
                if "YEAR" in text.upper() or len(text.split()) < 3:
                    continue
                found_matches.append(f"📍 BOISE: {text.strip()}")

            if found_matches:
                print(f"✅ Success! Found {len(found_matches)} vehicles:")
                for car in found_matches:
                    print(f"  - {car}")
                
                # Send one test notification to your phone
                report = "\n".join(found_matches)
                requests.post("https://ntfy.sh/Jalopy-Sniper", 
                              data=f"🎯 BOISE TEST SUCCESS:\n{report}".encode('utf-8'))
            else:
                print("🏁 Search finished, but the robot saw 0 cars. The table might be empty.")

        except Exception as e:
            print(f"⚠️ Test Snag: {e}")

        browser.close()

if __name__ == "__main__":
    main()
