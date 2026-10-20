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
        # 使用非 headless 模式或加上更多防偵測參數，避免被擋
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000) # 多給幾秒鐘讓動態資料跑出來
            
            page_text = page.inner_text("body")
            print(f"成功擷取頁面文字，長度: {len(page_text)} 字元")
            print("--- 抓到的頁面內容預覽開始 ---")
            print(page_text[:500]) # 印出前 500 字看看裡面到底有什麼
            print("--- 抓到的頁面內容預覽結束 ---")
            
            # 必須同時確保頁面包含活動關鍵字（證明不是被 Cloudflare 擋下的空白或防護頁面）
            if "田馥甄" in page_text or "Hebe" in page_text:
                has_buy = "立即購買" in page_text or "選購" in page_text
                
                if has_buy and "銷售一空" not in page_text:
                    print("🎉 真的偵測到有票可以買！")
                    msg = (
                        f"🚨🚨🚨 <b>田馥甄演唱會出現購票按鈕！快搶！</b>\n\n"
                        f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                    )
                    send_telegram(msg)
                else:
                    print("😢 頁面正常，但目前所有場次均顯示【銷售一空】")
            else:
                print("⚠️ 警告：頁面可能被 Cloudflare 攔截或尚未完全載入活動頁面！")
                
        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
            print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
