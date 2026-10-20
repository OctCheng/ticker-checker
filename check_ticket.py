import time
import cloudscraper

ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def debug_api():
    print("=" * 50)
    timestamp = int(time.time() * 1000)
    url = f"https://api.ticketplus.com.tw/config/api/v1/get?activityId={ACTIVITY_ID}&_={timestamp}"
    
    try:
        resp = scraper.get(url, timeout=15)
        print(f"✅ 連線狀態碼: {resp.status_code}")
        
        if resp.status_code == 200:
            print("\n--- 📝 完整原始 JSON 內容 (前 1500 字) ---")
            raw_text = resp.text
            print(raw_text[:1500])
            print("\n------------------------------------------")
            
            data = resp.json()
            print(f"📌 最外層所有的 Key: {list(data.keys())}")
        else:
            print(f"❌ 連線失敗")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    print("=" * 50)

if __name__ == "__main__":
    debug_api()
