import time
import cloudscraper

ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def debug_api():
    print("=" * 50)
    print("🔍 開始偵測 API 真實資料結構...")
    timestamp = int(time.time() * 1000)
    url = f"https://api.ticketplus.com.tw/config/api/v1/get?activityId={ACTIVITY_ID}&_={timestamp}"
    
    try:
        resp = scraper.get(url, timeout=15)
        print(f"API 狀態碼: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", {})
            print(f"✅ 連線成功！成功突破防火牆拿到資料。")
            print(f"📦 Result 內包含的主欄位有：{list(result.keys())}")
            
            for key, item in result.items():
                if isinstance(item, list):
                    print(f"  👉 [陣列] '{key}' 包含 {len(item)} 筆資料")
                    if len(item) > 0 and isinstance(item[0], dict):
                        print(f"       第一筆的內部屬性有: {list(item[0].keys())}")
                elif isinstance(item, dict):
                    print(f"  👉 [物件] '{key}' 包含 {len(item.keys())} 個屬性")
                    if 'session' in item:
                        print(f"       ⚠️ 發現 'session' 藏在 '{key}' 裡面！")
                else:
                    print(f"  👉 [數值/字串] '{key}' = {str(item)[:20]}...")
        else:
            print(f"❌ 連線失敗，狀態碼: {resp.status_code}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    print("=" * 50)

if __name__ == "__main__":
    debug_api()
