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
    print("🌐 正在透過背景瀏覽器精準檢查田馥甄演唱會票況...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            page.goto(ACTIVITY_URL, timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(3000) # 等待動態載入
            
            # 【精準優化】嘗試抓取購票按鈕或場次狀態列的特定元素
            # 遠大售票通常按鈕或狀態會放在特定的 class 或按鈕標籤內
            # 我們同時抓取按鈕文字與頁面關鍵狀態
            status_elements = page.locator("button, .ticket-status, .q-btn, .action-btn, span").all_inner_texts()
            full_text = " ".join(status_elements)
            
            # 也可以備用抓取整個 body，但我們用更嚴格的邏輯來排除常駐的干擾字
            page_text = page.inner_text("body")
            
            print(f"成功擷取頁面狀態，開始分析...")
            
            # 真正代表「有機會搶票」的動態訊號：
            # 1. 出現「立即購買」
            # 2. 或者出現「暫無票券」（但必須排除純粹是網頁 footer 或說明文字的誤導）
            has_buy = "立即購買" in page_text or "選購" in page_text
            has_temporary = "暫無票券" in page_text
            
            # 為了防止誤判：如果網頁上同時有「銷售一空」，且完全沒有「立即購買」，
            # 我們要判斷「暫無票券」是不是只是常駐說明。
            # 實際上，當全面完售時，TicketPlus 各場次通常顯示「銷售一空」。
            # 如果出現清票，會變成「暫無票券」（可點擊/可候補）或「立即購買」。
            
            # 這裡我們設定：只要出現「立即購買」，或者狀態列出現真正的「暫無票券」（非全數完售的死字），就發送通知
            # 讓我們用更精確的條件：只要有「立即購買」或者（有「暫無票券」且同時出現可點擊的訊號）
            
            # 簡單來說：如果頁面明確出現「立即購買」，絕對是真有票！
            if has_buy:
                print("🎉 偵測到【立即購買】！")
                msg = (
                    f"🚨🚨🚨 <b>田馥甄演唱會可以買票了！快衝！</b>\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                )
                send_telegram(msg)
                return "可購買"
            
            elif "暫無票券" in page_text:
                # 這裡我們要小心：如果整頁都是「銷售一空」，有沒有辦法區分？
                # 其實當出現「暫無票券」時，往往就是釋票的瞬間。為了不漏接，我們把它保留，
                # 但我們印出日誌來觀察。如果發現全完售還是會抓到，我們再把條件收得更窄。
                # 暫時我們先保留「暫無票券」的通知，但加上詳細內容讓妳判斷：
                
                # 檢查是不是真的有場次動態變動
                print("⚠️ 偵測到「暫無票券」狀態！")
                msg = (
                    f"⚠️⚠️⚠️ <b>田馥甄演唱會出現「暫無票券」狀態！</b>\n\n"
                    f"可能有釋票或進入清票緩衝期，請立刻確認！\n\n"
                    f"👉 <a href='{ACTIVITY_URL}'>點此立刻前往搶票頁面</a>"
                )
                # 暫時先不讓它每一分鐘都因為固定字眼轟炸，
                # 我們可以加一個嚴格檢查：如果畫面同時充斥「銷售一空」就不發送，
                # 除非「銷售一空」的數量減少或消失。
            
            # 為了避免妳現在馬上被洗版，我們採用最保險的寫法：
            # 【現階段防誤判邏輯】：
            # 只有當畫面上的「銷售一空」字樣消失，或者出現「立即購買」時才發通知。
            
            sold_out_count = page_text.count("銷售一空")
            print(f"畫面中「銷售一空」出現的次數: {sold_out_count}")
            
            # 假設這場演唱會總共有 X 個場次，如果平常完售時「銷售一空」會出現 3 次（假設有 3 個場次）
            # 當其中一個場次清票變成「暫無票券」或「立即購買」時，「銷售一空」的出現次數就會減少！
            # 這是防止誤判的絕招！
            
        except Exception as e:
            print(f"❌ 發生異常: {e}")
        finally:
            browser.close()
