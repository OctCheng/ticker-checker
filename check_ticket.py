import os
from playwright.sync_api import sync_playwright
import requests

# === 田馥甄演唱會正式 ID ===
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
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(3000) # 等待動態載入
            
            page_text = page.inner_text("body")
            print(f"成功擷取頁面文字，長度: {len(page_text)} 字元")
            
            # 檢查關鍵字
            has_buy = "立即購買" in page_text or "選購" in page_text
            has_temp = "暫無票券" in page_text
            
            print(f"狀態檢查 -> 立即購買/選購: {has_buy}, 暫無票券: {has_temp}")
            
            # 如果出現立即購買，或是出現暫無票券（且不是整頁純粹的靜態完售字眼）
            if has_buy:
                print("🎉 偵測到有票可以買！")
                msg = (
                    f"🚨🚨🚨 <b>田馥甄演唱會出現購票按鈕！快搶！</b>\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                )
                send_telegram(msg)
            elif has_temp and "銷售一空" not in page_text:
                print("⚠️ 偵測到可能有釋票（暫無票券狀態）！")
                msg = (
                    f"⚠️⚠️⚠️ <b>田馥甄演唱會出現「暫無票券」狀態！</b>\n\n"
                    f"可能有清票或緩衝釋票，請立刻確認！\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                )
                send_telegram(msg)
            else:
                print("😢 目前所有場次均顯示【銷售一空】，不發送通知")
                
        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
            print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
