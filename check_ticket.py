import os
import requests
import json

API_URL = "https://apis.ticketplus.com.tw/config/api/v1/getS3?path=event/af2bd66d8fe65d78963cbb5bdc85771c/event.json"
ACTIVITY_URL = "https://ticketplus.com.tw/activity/af2bd66d8fe65d78963cbb5bdc85771c"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(message): 
    token = TELEGRAM_BOT_TOKEN.strip()
    chat_id = TELEGRAM_CHAT_ID.strip()
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage" 
    try: 
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10) 
    except Exception: 
        pass

def check_ticket_api():
    print("=" * 50)
    print("🚀 啟動 API 直連探勘模式 (不依賴瀏覽器)...")
    
    # 偽裝成正常的瀏覽器發送 API 請求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://ticketplus.com.tw",
        "Referer": f"https://ticketplus.com.tw/activity/af2bd66d8fe65d78963cbb5bdc85771c"
    }
    
    try:
        # 直接用 requests 敲 API，速度極快，不用等載入！
        response = requests.get(API_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("✅ 成功突破防線！取得 API JSON 資料！")
            
            # 將資料轉為字典格式
            data = response.json()
            
            # 把 JSON 轉回字串印出來看結構 (印出前 1500 字元)
            data_str = json.dumps(data, ensure_ascii=False)
            print(f"資料總長度: {len(data_str)} 字元")
            print("--- JSON 內容預覽開始 ---")
            print(data_str[:1500])
            print("--- JSON 內容預覽結束 ---")
            
            print("⚠️ 探勘完成：請查看上方 JSON 預覽內容。")
            print("接下來我們只要看裡面代表『完售』的英文關鍵字是什麼，就能寫出無敵的判斷式！")
            
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 發生異常: {e}")
    finally:
        print("=" * 50)

if __name__ == "__main__":
    check_ticket_api()
