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
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(6000) # 給足夠時間讓畫面渲染完畢
            
            page_text = page.inner_text("body")
            print(f"成功擷取頁面文字，長度: {len(page_text)} 字元")
            
            # 檢查是否有活動標題，確保不是空白頁面
            if "田馥甄" in page_text or "Hebe" in page_text:
                # 判斷是否全數完售
                has_sold_out = "銷售一空" in page_text
                print(f"狀態檢查 -> 是否包含『銷售一空』: {has_sold_out}")
                
                # 只有當「銷售一空」完全消失，且網頁上出現「立即購買」或「選購」時才通知
                if not has_sold_out and ("立即購買" in page_text or "選購" in page_text):
                    print("🎉 發現『銷售一空』消失，且出現購票按鈕！")
                    msg = (
                        f"🚨🚨🚨 <b>田馥甄演唱會出現購票按鈕！快搶！</b>\n\n"
                        f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                    )
                    send_telegram(msg)
                else:
                    print("😢 目前所有場次均確定【銷售一空】或尚未開賣，不發送通知")
            else:
                print("⚠️ 警告：頁面尚未完整載入活動資訊")
                
        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
            print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
