import requests
import os

# === 設定 ===
ACTIVITY_URL = "https://ticketplus.com.tw/activity/af2bd66d8fe65d78963cbb5bdc85771c"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = { 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8", 
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8", 
}

def send_telegram(message): 
    """發送 Telegram 通知到群組""" 
    chat_id = TELEGRAM_CHAT_ID.strip() 
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage" 
    payload = { 
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "HTML", 
    } 
    try: 
        resp = requests.post(url, json=payload, timeout=10) 
        if resp.status_code == 200: 
            print("✅ Telegram 通知已發送") 
        else: 
            print(f"❌ Telegram 發送失敗: {resp.status_code} {resp.text}") 
    except Exception as e: 
        print(f"❌ Telegram 發送錯誤: {e}")

def check_page(): 
    """檢查 TicketPlus 活動頁面的售票狀態""" 
    try: 
        resp = requests.get(ACTIVITY_URL, headers=HEADERS, timeout=15) 
        resp.raise_for_status() 
        html = resp.text
        print(f"頁面抓取成功，長度: {len(html)}")

        if "銷售一空" in html:
            print("😢 目前狀態：銷售一空（沒有變化）")
            return "銷售一空"

        elif "暫無票券" in html:
            print("🎫 狀態變成「暫無票券」了！可能有退票！")
            send_telegram(
                "🎫🔔🔔🔔 田馥甄演唱會狀態改變！\n\n"
                "狀態：暫無票券（可能有退票釋出！）\n\n"
                f"👉 快去看：{ACTIVITY_URL}"
            )
            return "暫無票券"
            
        elif "立即購買" in html or "選擇場次" in html:
            print("🎉 好像有票可以買！！！")
            send_telegram(
                "🎉🎉🎉 田馥甄演唱會可能有票了！！！\n\n"
                "頁面出現可購買的跡象！\n\n"
                f"👉 立刻搶：{ACTIVITY_URL}"
            )
            return "可能有票"

        else:
            print("🤔 頁面狀態不明，可能網頁結構改變了")
            return "未知"

    except Exception as e:
        print(f"❌ 抓取頁面失敗: {e}")
        return "錯誤"

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 開始檢查田馥甄演唱會票券狀態...")
    status = check_page()
    print(f"\n最終狀態: {status}")
    print("=" * 50)
    # 測試用：確認通知有通就刪掉或註解底下這行
    send_telegram("✅ 測試通知：如果你在群組看到這則訊息，代表 GitHub Actions 執行成功！")
