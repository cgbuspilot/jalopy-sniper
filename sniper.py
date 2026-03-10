import requests
import time
from patchright.sync_api import sync_playwright

# Locked-in for the Boise Toyota Yaris hunt
LOC = "BOISE"
MAKE = "TOYOTA"
MODEL = "YARIS"
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    with sync_playwright() as p:
        # 'patchright' launches a browser that hides the 'navigator.webdriver' flag
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🕵️ Ghost Hunt: {LOC} {MAKE} {MODEL}")
        
        try:
            # We use the direct inventory list URL
            page.goto("https://inventory.pickapartjalopyjungle.com/inventorylist.php", wait_until="networkidle")
            time.sleep(5)

            # We try to find the frame or the direct selector
            print("Searching for the inventory engine...")
            page.wait_for_selector('select[name="location"]', timeout=30000)
            
            page.select_option('select[name="location"]', label=LOC)
            time.sleep(2)
            page.select_option('select[name="make"]', label=MAKE)
            time.sleep(2)
            page.select_option('select[name="model"]', label=MODEL)
            time.sleep(1)
            
            page.click('input[type="submit"]')
            print("Search submitted!")
            time.sleep(6)
            
            rows = page.locator("tr").all_inner_texts()
            found = [r.strip() for r in rows if MAKE in r.upper()]
            
            if found:
                print(f"🎯 BINGO! {len(found)} results found.")
                report = "\n".join(found)
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"🎯 {LOC} HIT:\n{report}".encode('utf-8'))
            else:
                print(f"🏁 Search complete. No {MODEL}s found.")

        except Exception as e:
            print(f"⚠️ Still Blocked: {e}")
            page.screenshot(path="ghost_fail.png")

        browser.close()

if __name__ == "__main__":
    main()
