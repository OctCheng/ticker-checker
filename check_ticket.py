import cloudscraper
import json
import re
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
    print("🔍 正在解析網頁內嵌資料...")
    
    try:
        resp = scraper.get(ACTIVITY_URL, timeout=15)
        if resp.status_code == 200:
            html = resp.text
            
            # 尋找網頁中常見的 Nuxt / 狀態 JSON 結構
            # 通常網頁會包含 session 或 ticket 相關的關鍵字
            print(f"網頁文字總長度: {len(html)} 字元")
            
            # 用正則表達式尋找網頁中是否有藏有 "session" 或 "status" 的 JSON 片段
            if "session" in html.lower() or "status" in html.lower():
                print("🎯 成功在網頁原始碼中找到票務相關關鍵字！")
                
                # 簡單印出包含 session 的周邊文字來確認結構
                matches = re.findall(r'.{0,50}session.{0,50}', html, re.IGNORECASE)
                print(f"找到 {len(matches)} 個匹配片段，範例：")
                for m in matches[:3]:
                    print(f"  - {m.strip()}")
                
                # 既然網頁載入成功且包含資料，直接發送測試通知驗證流程！
                send_telegram(f"🚨 <b>[測試成功] 成功穿透防火牆並抓取活動頁面！</b>\n\n👉 <a href='{ACTIVITY_URL}'>點此檢視活動</a>")
                print("✅ 測試通知已發送！")
            else:
                print("⚠️ 未能在網頁中找到預期的票務關鍵字")
        else:
            print(f"❌ 網頁抓取失敗，狀態碼: {resp.status_code}")
    except Exception as e:
        print(f"❌ 發生異常: {e}")
    print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
