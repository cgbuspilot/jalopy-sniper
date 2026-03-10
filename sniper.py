import requests
import time
from playwright.sync_api import sync_playwright

# Locked-in for our "First Win" test
LOC = "BOISE"
MAKE = "TOYOTA"
MODEL = "YARIS"
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # Using a very common Chrome profile to look like a regular person
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🚀 Targeting Boise Toyota Yaris...")
        
        # We're going to the search results page DIRECTLY
        # This bypasses the need to click dropdowns
        target_url = "https://inventory.pickapartjalopyjungle.com/inventorylist.php"
        
        try:
            page.goto(target_url, wait_until="networkidle")
            time.sleep(5)

            # Check if we can see the location dropdown now
            if page.query_selector('select[name="location"]'):
                print("✅ Found the search engine!")
                
                page.select_option('select[name="location"]', label=LOC)
                time.sleep(2)
                page.select_option('select[name="make"]', label=MAKE)
                time.sleep(2)
                page.select_option('select[name="model"]', label=MODEL)
                time.sleep(1)
                
                page.click('input[type="submit"]')
                time.sleep(5)
                
                rows = page.locator("tr").all_inner_texts()
                found = [r.strip() for r in rows if MAKE in r.upper()]
                
                if found:
                    print(f"🎯 SUCCESS! Found {len(found)} results.")
                    report = "\n".join(found)
                    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
                else:
                    print(f"🏁 Finished. No {MODEL}s found in {LOC}.")
            else:
                print("❌ Still blocked. The site is not showing the search form to the bot.")
                page.screenshot(path="blocked_view.png")

        except Exception as e:
            print(f"⚠️ Error: {e}")

        browser.close()

if __name__ == "__main__":
    main()
