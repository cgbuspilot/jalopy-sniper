import os
import requests

# Inputs from Dashboard
MAKE = os.getenv("INPUT_MAKE", "").strip().upper()
MODEL = os.getenv("INPUT_MODEL", "").strip().upper()
YEAR_START = int(os.getenv("INPUT_YEAR_START", 1900))
YEAR_END = int(os.getenv("INPUT_YEAR_END", 2026))
LOCATION = os.getenv("INPUT_LOCATION", "ALL").strip().upper()
NTFY_TOPIC = "Jalopy-Sniper"

def main():
    print("Requesting Raw Inventory Feed...")
    
    # We are using their internal search API directly now
    # This bypasses the website layout entirely
    url = "https://inventory.pickapartjalopyjungle.com/inventorylist.php"
    
    try:
        # We pretend to be a very basic mobile browser
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'}
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Server refused connection: {response.status_code}")
            return

        # Instead of Playwright, we are just reading the raw text
        # This is much more reliable
        lines = response.text.split('</tr>')
        print(f"Successfully pulled {len(lines)} raw records.")
        
        found_matches = []
        for line in lines:
            # Clean up HTML tags to get plain text
            clean_text = line.replace('<td>', ' ').replace('</td>', ' ').upper()
            parts = clean_text.split()
            
            if len(parts) < 3: continue
            
            try:
                car_year = int(parts[0])
                # Filter logic
                if not (YEAR_START <= car_year <= YEAR_END): continue
                if MAKE and MAKE not in clean_text: continue
                if MODEL and MODEL not in clean_text: continue
                if LOCATION != "ALL" and LOCATION not in clean_text: continue
                
                found_matches.append(" ".join(parts))
            except:
                continue

        if found_matches:
            summary = "\n".join(found_matches[:15])
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"🎯 JALOPY SNIPER ({len(found_matches)} Hits):\n{summary}".encode('utf-8'))
            print(f"Success! {len(found_matches)} matches sent to phone.")
        else:
            print(f"Scanned {len(lines)} cars, but zero matches for your filters.")

    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    main()
