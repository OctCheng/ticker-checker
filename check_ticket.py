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
    print("🌐 啟動遠大售票 (TicketPlus) 專用刷票引擎...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            page.goto(ACTIVITY_URL, timeout=30000)
            
            # 【遠大專屬邏輯 1】強制等待 10 秒，讓票況 API 跑完，確保 Loading 消失
            print("⏳ 等待 10 秒讓遠大售票載入真實票況...")
            page.wait_for_timeout(10000) 
            
            page_text = page.inner_text("body")
            
            # 如果伺服器卡頓還在 Loading，再給它 5 秒
            if "Loading..." in page_text:
                print("⏳ 網頁仍在 Loading，追加等待 5 秒...")
                page.wait_for_timeout(5000)
                page_text = page.inner_text("body")
            
            print(f"✅ 成功擷取頁面，長度: {len(page_text)} 字元")

            # 【遠大專屬邏輯 2】確認畫面有成功進入活動區塊
            if "售票狀態" not in page_text:
                print("⚠️ 找不到『售票狀態』，可能遭阻擋或網頁尚未載入完成。")
                return
            
            # 【遠大專屬邏輯 3】精準抓取實戰關鍵字 (避開頁尾常駐的假按鈕)
            # - 完售必定顯示：「銷售一空」
            # - 有票可買顯示：「選購」
            # - 鎖票/結帳中顯示：「暫無票券」
            is_sold_out = "銷售一空" in page_text
            has_ticket = "選購" in page_text
            has_buffer = "暫無票券" in page_text
            
            print(f"📊 當前狀態分析 -> 銷售一空: {is_sold_out} | 選購: {has_ticket} | 暫無票券: {has_buffer}")
            
            # 觸發通知：出現「選購」或「暫無票券」
            if has_ticket or has_buffer:
                print("🎉 發現目標！狀態改變，發送 Telegram 通知！")
                msg = (
                    f"🚨🚨🚨 <b>田馥甄演唱會 票況變動！</b>\n\n"
                    f"系統偵測到遠大售票出現 <b>「{'選購' if has_ticket else '暫無票券'}」</b> 狀態！\n"
                    f"這極可能是清票或釋票，快衝！\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票</a>"
                )
                send_telegram(msg)
            else:
                print("😢 目前場次仍為【銷售一空】，系統安靜待機中。")

        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
            print("=" * 50)

if __name__ == "__main__":
    check_ticket_status()
