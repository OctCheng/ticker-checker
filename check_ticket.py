import cloudscraper
from bs4 import BeautifulSoup
import json
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
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage" 
    try: 
        scraper.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10) 
    except Exception: 
        pass

def check_ticket_status():
    print("=" * 50)
    print("🔍 正在抓取活動網頁並解析票況...")
    
    try:
        resp = scraper.get(ACTIVITY_URL, timeout=15)
        print(f"網頁連線狀態碼: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 檢查網頁標題確認是否成功進入
            title = soup.find('title')
            print(f"📌 網頁標題: {title.text if title else '無標題'}")
            
            # 嘗試尋找網頁中的內嵌 JSON 資料 (通常 Nuxt 網站會放在 __NUXT__ 或 script 標籤中)
            scripts = soup.find_all('script')
            found_data = False
            
            for s in scripts:
                if s.string and ('session' in s.string or 'status' in s.string):
                    # 這裡可以印出部分內容協助確認
                    if 'activity' in s.string:
                        print("🎯 找到包含活動資料的 Script 標籤！")
                        found_data = True
                        break
            
            if found_data:
                print("✅ 成功透過網頁原始碼掌握活動結構！")
            else:
                print("⚠️ 網頁內容已載入，但未在 script 中直接命中關鍵字，改用文字檢索...")
                
            # 直接搜尋網頁上常見的狀態文字
            page_text = soup.text
            if "銷售一空" in page_text:
                print("😢 網頁顯示目前有場次為：銷售一空")
            if "立即購買" in page_text or "暫無票券" in page_text:
                print("🎉 網頁中偵測到「立即購買」或「暫無票券」字眼！")
                send_telegram(f"🚨 <b>[測試通知] 發現網頁狀態改變！</b>\n\n👉 <a href='{ACTIVITY_URL}'>點此前往查看</a>")
        else:
            print(f"❌ 網頁抓取失敗，狀態碼: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ 發生異常: {e}")
    print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
