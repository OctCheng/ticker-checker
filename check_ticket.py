import os
from playwright.sync_api import sync_playwright
import requests

ACTIVITY_ID = "af2bd66d8fe65d78963cbb5bdc85771c"
ACTIVITY_URL = f"https://ticketplus.com.tw/activity/{ACTIVITY_ID}"

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

def check_ticket_status():
    print("=" * 50)
    print("🌐 正在啟動背景瀏覽器抓取即時畫面...")
    
    with sync_playwright() as p:
        # 啟動無頭瀏覽器 (Headless Chrome)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # 前往活動頁面並等待網路閒置、元素載入
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="networkidle")
            
            # 額外等待 3 秒讓 JS 動態渲染完成
            page.wait_for_timeout(3000)
            
            # 取得畫面上完整渲染後的文字內容
            page_text = page.inner_text("body")
            print(f"成功擷取頁面文字，長度: {len(page_text)} 字元")
            
            # 檢查關鍵字
            if "銷售一空" in page_text:
                print("📌 偵測到畫面上有【銷售一空】")
            
            if "立即購買" in page_text or "暫無票券" in page_text:
                print("🎉 成功在畫面上偵測到購買/票券狀態！")
                send_telegram(f"🚨 <b>[Playwright 測試成功] 成功透過真實瀏覽器抓取頁面！</b>\n\n👉 <a href='{ACTIVITY_URL}'>點此前往搶票</a>")
                return "有票/狀態改變"
            else:
                print("😢 畫面中未偵測到開放購買字眼")
                return "全數售完"
                
        except Exception as e:
            print(f"❌ 瀏覽器載入頁面發生異常: {e}")
            return "異常"
        finally:
            browser.close()
            
    print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
