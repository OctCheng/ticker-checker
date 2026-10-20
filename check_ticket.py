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
    print("🌐 正在透過背景瀏覽器檢查田馥甄演唱會票況...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            # 前往網頁，等待網路閒置
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="networkidle")
            
            # 額外等待 6 秒，確保遠大售票的動態 JavaScript 把真實票況渲染完畢
            page.wait_for_timeout(6000)
            
            page_text = page.inner_text("body")
            print(f"成功擷取頁面文字，長度: {len(page_text)} 字元")
            
            # 檢查是否還在讀取中
            if "Loading..." in page_text:
                print("⏳ 頁面仍在 Loading，再多等 3 秒...")
                page.wait_for_timeout(3000)
                page_text = page.inner_text("body")

            # 判斷當前狀態：
            # 如果全面完售，遠大售票通常會顯示「銷售一空」
            # 如果有釋票或能買，會出現真正的可點擊購票按鈕或「暫無票券」
            has_sold_out = "銷售一空" in page_text
            
            # 為了精準避開導覽列的「立即購買」，我們檢查頁面上是否有「銷售一空」以外的狀態
            # 當真正有票時，「銷售一空」的字樣會減少或消失，並出現可以買的按鈕
            print(f"狀態判定 -> 是否包含『銷售一空』: {has_sold_out}")
            
            if not has_sold_out and ("立即購買" in page_text or "選購" in page_text or "暫無票券" in page_text):
                print("🎉 發現異常！『銷售一空』消失或出現購票/暫無票券狀態！")
                msg = (
                    f"🚨🚨🚨 <b>田馥甄演唱會票況有重大變化！</b>\n\n"
                    f"系統偵測到頁面不再全是完售狀態，可能有機會搶票！\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                )
                send_telegram(msg)
            else:
                print("😢 目前所有場次均確定【銷售一空】，不發送通知")
                
        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
            print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
