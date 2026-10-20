import requests
import os
import time

# === 設定 (目前為測試活動 ID) ===
ACTIVITY_ID = "7f9c57d1f3e5c15d97c51408f26ca085"
ACTIVITY_URL = f"https://ticketplus.com.tw/activity/{ACTIVITY_ID}"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# 加上更逼真的瀏覽器 Headers 與防止快取機制
HEADERS = { 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
    "Accept": "application/json, text/plain, */*", 
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://ticketplus.com.tw",
    "Referer": ACTIVITY_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Connection": "keep-alive"
}

def send_telegram(message): 
    """發送 Telegram 通知到群組""" 
    token = TELEGRAM_BOT_TOKEN.strip()
    chat_id = TELEGRAM_CHAT_ID.strip()
    
    if not token or not chat_id:
        print("❌ 錯誤：未設定 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
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
            print("✅ Telegram 通知已成功發送！") 
        else: 
            print(f"❌ Telegram 發送失敗: {resp.status_code} {resp.text}") 
    except Exception as e: 
        print(f"❌ Telegram 發送錯誤: {e}")

def get_sessions_from_api(activity_id):
    """嘗試多個 API 端點取得場次資料，防止 404 中斷"""
    timestamp = int(time.time() * 1000)
    endpoints = [
        f"https://api.ticketplus.com.tw/config/api/v1/get?activityId={activity_id}&_={timestamp}",
        f"https://api.ticketplus.com.tw/config/api/v1/session?activityId={activity_id}&_={timestamp}"
    ]
    
    for url in endpoints:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                sessions = data.get("result", {}).get("session", [])
                if sessions:
                    print(f"成功從 API ({url.split('?')[0].split('/')[-1]}) 取得 {len(sessions)} 個場次")
                    return sessions
            else:
                print(f"⚠️ API 嘗試回傳非 200 狀態碼 ({resp.status_code}): {url.split('?')[0]}")
        except Exception as e:
            print(f"⚠️ API 請求異常: {e}")
            
    return []

def get_session_ticket_details(session_id):
    """深入查詢特定場次 (sessionId) 內各票價區域的明細狀態"""
    timestamp = int(time.time() * 1000)
    try:
        ticket_api = f"https://api.ticketplus.com.tw/config/api/v1/ticket?sessionId={session_id}&_={timestamp}"
        resp = requests.get(ticket_api, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tickets = data.get("result", {}).get("ticket", [])
            
            detail_msgs = []
            for t in tickets:
                ticket_name = t.get("name", "票區")
                price = t.get("price", "")
                t_status = str(t.get("status", "")).lower().strip()
                # 只要票區狀態不是完售，就記錄下來
                if t_status not in ["soldout", "ended"]:
                    detail_msgs.append(f"   ▫️ {ticket_name} (${price}): <b>{t_status}</b>")
            return detail_msgs
    except Exception as e:
        print(f"⚠️ 抓取票區明細失敗 (sessionId: {session_id}): {e}")
    return []

def check_ticket_status(): 
    """查詢 TicketPlus API 檢查場次與各票區售票狀態""" 
    sessions = get_sessions_from_api(ACTIVITY_ID)
    
    if not sessions:
        print("❌ 無法取得場次資料（所有 API 端點皆未回應有效資料或被防火牆阻擋）")
        return "無資料"

    changed_sessions = []

    for session in sessions:
        name = session.get("name", "演唱會場次")
        session_id = session.get("id", "")
        status = str(session.get("status", "")).lower().strip()
        
        print(f"📌 [場次 API] {name} | sessionId: {session_id} | status: '{status}'")
        
        # 只要狀態不是純粹完售 (soldout/ended)，代表有釋票或狀態改變
        if status not in ["soldout", "ended", ""]:
            session_msg = f"🎫 <b>{name}</b> (狀態: <code>{status}</code>)"
            
            if session_id:
                ticket_details = get_session_ticket_details(session_id)
                if ticket_details:
                    session_msg += "\n" + "\n".join(ticket_details)
            
            changed_sessions.append(session_msg)

    if changed_sessions:
        msg = (
            f"🚨🚨🚨 <b>[測試通知] 演唱會狀態改變 / 有票釋出！</b>\n\n"
            + "\n\n".join(changed_sessions)
            + f"\n\n👉 快去搶票：{ACTIVITY_URL}"
        )
        print("🎉 偵測到狀態改變，準備發送 Telegram 通知！")
        send_telegram(msg)
        return "狀態變更/有票"
    else:
        print("😢 目前所有場次 API 狀態均為 soldout")
        return "全數售完"

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 開始檢查票券狀態...")
    status = check_ticket_status()
    print(f"\n最終檢查結果: {status}")
    print("=" * 50)
