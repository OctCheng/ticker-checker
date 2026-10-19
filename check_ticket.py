import requests
import os

# === 設定 ===
ACTIVITY_ID = "af2bd66d8fe65d78963cbb5bdc85771c"
ACTIVITY_URL = f"https://ticketplus.com.tw/activity/{ACTIVITY_ID}"
API_URL = f"https://api.ticketplus.com.tw/config/api/v1/session?activityId={ACTIVITY_ID}"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = { 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
    "Accept": "application/json, text/plain, */*", 
    "Origin": "https://ticketplus.com.tw",
    "Referer": ACTIVITY_URL
}

def send_telegram(message): 
    """發送 Telegram 通知到群組""" 
    token = TELEGRAM_BOT_TOKEN.strip()
    chat_id = TELEGRAM_CHAT_ID.strip()
    
    if not token or not chat_id:
        print("❌ 錯誤：未讀取到 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage" 
    payload = { 
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "HTML", 
    } 
    try: 
        resp = requests.post(url, json=payload, timeout=10) 
        if resp.status_code == 200: 
            print("✅ Telegram 通知已發送成功！") 
        else: 
            print(f"❌ Telegram 發送失敗: {resp.status_code} {resp.text}") 
    except Exception as e: 
        print(f"❌ Telegram 發送錯誤: {e}")

def check_ticket_status(): 
    """查詢 TicketPlus API 檢查場次售票狀態""" 
    try: 
        resp = requests.get(API_URL, headers=HEADERS, timeout=15) 
        resp.raise_for_status() 
        data = resp.json()
        
        sessions = data.get("result", {}).get("session", [])
        if not sessions:
            get_url = f"https://api.ticketplus.com.tw/config/api/v1/get?activityId={ACTIVITY_ID}"
            resp = requests.get(get_url, headers=HEADERS, timeout=15)
            data = resp.json()
            sessions = data.get("result", {}).get("session", [])

        print(f"頁面資料抓取成功，共找到 {len(sessions)} 個場次")

        available_count = 0
        status_summary = []

        for session in sessions:
            name = session.get("name", "演唱會場次")
            status = session.get("status", "")
            print(f"場次：{name} | 狀態：{status}")
            
            if status not in ["soldout", "sold_out", "ended"]:
                available_count += 1
                status_summary.append(f"🎫 {name}：<b>狀態改變（{status}）</b>")
            else:
                status_summary.append(f"❌ {name}：完售")

        if available_count > 0:
            msg = f"🎉🎉🎉 <b>田馥甄演唱會狀態改變/可能有票！</b>\n\n" + "\n".join(status_summary) + f"\n\n👉 搶票網址：{ACTIVITY_URL}"
            print("🎉 發現潛在票券，準備發送 Telegram 通知！")
            send_telegram(msg)
            return "可能有票"
        else:
            print("😢 目前所有場次均為售完狀態")
            return "全數售完"

    except Exception as e: 
        print(f"❌ 查詢 API 失敗: {e}") 
        return "錯誤"

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 開始檢查田馥甄演唱會票券狀態...")
    status = check_ticket_status()
    print(f"\n最終檢查結果: {status}")
    print("=" * 50)
    
    # 測試發送通知，確定成功收到訊息後可刪除或註解下一行
    send_telegram("✅ 測試通知：GitHub 機器人執行完成，Telegram 連線成功！")
