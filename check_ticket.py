import os
import time
import cloudscraper

# === 設定 (測試活動 ID) ===
ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"
ACTIVITY_URL = f"https://ticketplus.com.tw/activity/{ACTIVITY_ID}"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# 建立 Cloudscraper 實例來繞過防火牆
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def send_telegram(message): 
    token = TELEGRAM_BOT_TOKEN.strip()
    chat_id = TELEGRAM_CHAT_ID.strip()
    if not token or not chat_id:
        print("❌ 未設定 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage" 
    try: 
        resp = scraper.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10) 
        if resp.status_code == 200: 
            print("✅ Telegram 通知已發送成功！") 
        else: 
            print(f"❌ Telegram 失敗: {resp.status_code} {resp.text}") 
    except Exception as e: 
        print(f"❌ Telegram 錯誤: {e}")

def get_sessions_from_api(activity_id):
    """使用 Cloudscraper 突破防火牆抓取場次"""
    timestamp = int(time.time() * 1000)
    endpoints = [
        f"https://api.ticketplus.com.tw/config/api/v1/get?activityId={activity_id}&_={timestamp}",
        f"https://api.ticketplus.com.tw/config/api/v1/session?activityId={activity_id}&_={timestamp}"
    ]
    for url in endpoints:
        try:
            resp = scraper.get(url, timeout=15)
            if resp.status_code == 200:
                sessions = resp.json().get("result", {}).get("session", [])
                if sessions:
                    print(f"🔥 成功突破防火牆 ({url.split('?')[0].split('/')[-1]})！取得 {len(sessions)} 個場次")
                    return sessions
            else:
                print(f"⚠️ 防火牆阻擋或 404 ({resp.status_code}): {url.split('?')[0]}")
        except Exception as e:
            print(f"⚠️ 請求異常: {e}")
    return []

def get_session_ticket_details(session_id):
    timestamp = int(time.time() * 1000)
    try:
        url = f"https://api.ticketplus.com.tw/config/api/v1/ticket?sessionId={session_id}&_={timestamp}"
        resp = scraper.get(url, timeout=10)
        if resp.status_code == 200:
            tickets = resp.json().get("result", {}).get("ticket", [])
            details = []
            for t in tickets:
                name, price = t.get("name", "票區"), t.get("price", "")
                t_status = str(t.get("status", "")).lower().strip()
                if t_status not in ["soldout", "ended"]:
                    details.append(f"   ▫️ {name} (${price}): <b>{t_status}</b>")
            return details
    except Exception:
        pass
    return []

def check_ticket_status(): 
    sessions = get_sessions_from_api(ACTIVITY_ID)
    if not sessions:
        print("❌ 依然被防火牆阻擋或查無資料")
        return "無資料"

    changed_sessions = []
    for session in sessions:
        name = session.get("name", "演唱會場次")
        s_id = session.get("id", "")
        status = str(session.get("status", "")).lower().strip()
        print(f"📌 [API] {name} | status: '{status}'")
        
        if status not in ["soldout", "ended", ""]:
            msg = f"🎫 <b>{name}</b> (狀態: <code>{status}</code>)"
            if s_id:
                details = get_session_ticket_details(s_id)
                if details: msg += "\n" + "\n".join(details)
            changed_sessions.append(msg)

    if changed_sessions:
        final_msg = f"🚨🚨🚨 <b>[測試] 演唱會狀態改變/有票釋出！</b>\n\n" + "\n\n".join(changed_sessions) + f"\n\n👉 {ACTIVITY_URL}"
        send_telegram(final_msg)
        return "狀態變更/有票"
    print("😢 目前 API 狀態均為 soldout")
    return "全數售完"

if __name__ == "__main__":
    print("=" * 50)
    check_ticket_status()
    print("=" * 50)
