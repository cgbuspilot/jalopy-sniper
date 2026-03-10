import os
import requests
import time
from playwright.sync_api import sync_playwright

# Safer input handling
MAKE = os.getenv("INPUT_MAKE", "TOYOTA").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "RAV4").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # Launching with a real-looking browser signature
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"🚀 Starting Stealth Hunt for: {MAKE} {MODEL}")
        
        try:
            # Go to the main entry point
            page.goto("https://inventory.pickapartjalopyjungle.com/", wait_until="networkidle", timeout=60000)
            time.sleep(5) 

            # Check if we are stuck behind an iframe
            search_frame = None
            for frame in page.frames:
                if frame.query_selector('select[name="location"]'):
                    search_frame = frame
                    break
            
            if not search_frame:
                print(f"❌ Form not found. Page Title: {page.title()}")
                page.screenshot(path="bot_view.png")
                browser.close()
                return

            # Proceed with the clicks
            print("✅ Form found! Selecting BOISE...")
            search_frame.select_option('select[name="location"]', label="BOISE")
            time.sleep(4) # Extra time for the 'Make' list to load

            print(f"Selecting {MAKE}...")
            search_frame.wait_for_selector(f'select[name="make"] option:has-text("{MAKE}")', timeout=10000)
            search_frame.select_option('select[name="make"]', label=MAKE)
            time.sleep(4) # Extra time for the 'Model' list to load

            print(f"Selecting {MODEL}...")
            search_frame.wait_for_selector(f'select[name="model"] option:has-text("{MODEL}")', timeout=10000)
            search_frame.select_option('select[name="model"]', label=MODEL)
            time.sleep(2)

            search_frame.click('input[type="submit"]')
            print("Search submitted. Waiting for table...")
            time.sleep(6)

            rows = search_frame.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper() and MODEL in r.upper()]
            
            if found:
                print(f"✅ Success! Found {len(found)} results.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 BOISE HIT:\n{report}".encode('utf-8'))
            else:
                print("🏁 Search completed, but no cars found in the table.")

        except Exception as e:
            print(f"⚠️ Hunt Snag: {e}")
            page.screenshot(path="error_view.png")

        browser.close()

if __name__ == "__main__":
    main()
