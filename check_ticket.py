import cloudscraper
import os

ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"
ACTIVITY_URL = f"https://ticketplus.com.tw/activity/{ACTIVITY_ID}"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def send_telegram(message): 
    token = TELEGRAM_BOT_TOKEN.strip()
    chat_id = TELEGRAM_CHAT_ID.strip()
    if not token or not chat_id: 
        print("❌ 未設定 Telegram Token 或 Chat ID")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage" 
    try: 
        resp = scraper.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10) 
        if resp.status_code == 200:
            print("✅ Telegram 通知發送成功！")
        else:
            print(f"❌ Telegram 發送失敗: {resp.status_code} {resp.text}")
    except Exception as e: 
        print(f"❌ Telegram 錯誤: {e}")

def check_ticket_status():
    print("=" * 50)
    print("🔍 正在透過 Cloudscraper 抓取活動網頁...")
    
    try:
        resp = scraper.get(ACTIVITY_URL, timeout=15)
        print(f"網頁連線狀態碼: {resp.status_code}")
        
        if resp.status_code == 200:
            html_content = resp.text
            
            # 直接在網頁文字中搜尋關鍵字
            if "銷售一空" in html_content:
                print("📌 目前網頁偵測結果：部分或全部場次顯示【銷售一空】")
            
            if "立即購買" in html_content or "暫無票券" in html_content:
                print("🎉 偵測到網頁出現【立即購買】或【暫無票券】！")
                send_telegram(f"🚨 <b>[測試通知] 遠大售票狀態改變！</b>\n\n👉 <a href='{ACTIVITY_URL}'>點此前往搶票頁面</a>")
                return "有票/狀態改變"
            else:
                print("😢 目前未偵測到開放購買字眼")
                return "全數售完"
        else:
            print(f"❌ 網頁抓取失敗，狀態碼: {resp.status_code}")
            return "抓取失敗"
            
    except Exception as e:
        print(f"❌ 發生異常: {e}")
        return "異常"
    print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
