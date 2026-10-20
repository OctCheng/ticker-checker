import cloudscraper
import time

ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def test_api():
    print("=" * 50)
    print("🔍 測試遠大售票隱藏的正確參數...")
    
    timestamp = int(time.time() * 1000)
    
    # 根據報錯訊息，我們測試三個最有可能的正確 API 組合
    urls_to_test = {
        "測試 1 (eventId)": f"https://api.ticketplus.com.tw/config/api/v1/get?eventId={ACTIVITY_ID}&_={timestamp}",
        "測試 2 (productId)": f"https://api.ticketplus.com.tw/config/api/v1/get?productId={ACTIVITY_ID}&_={timestamp}",
        "測試 3 (主活動 API)": f"https://api.ticketplus.com.tw/activity/api/v1/activity/{ACTIVITY_ID}?_={timestamp}"
    }
    
    for name, url in urls_to_test.items():
        print(f"\n▶️ {name} ...")
        try:
            resp = scraper.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # 如果回傳的資料裡面沒有 errCode，代表我們成功拿到真實資料了！
                if "errCode" not in data:
                    print("✅ 賓果！這個 API 是正確的！")
                    print(f"回傳的 Keys: {list(data.keys())}")
                    if "result" in data:
                        print(f"Result 裡面的 Keys: {list(data['result'].keys())}")
                else:
                    print(f"❌ 錯誤: {data.get('errMsg')}")
            else:
                print(f"❌ 失敗，狀態碼: {resp.status_code}")
        except Exception as e:
            print(f"❌ 發生異常: {e}")
            
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_api()
