import os
import random
import requests

from flask import Flask, request
from openai import OpenAI


# =========================
# تنظیمات
# =========================

TOKEN = os.environ.get("RUBIKA_TOKEN")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

API = f"https://botapi.rubika.ir/v3/{TOKEN}"

BOT_NAME = "ربیکا"

app = Flask(__name__)


# =========================
# هوش مصنوعی
# =========================

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# =========================
# ارسال پیام
# =========================

def send_message(chat_id, text):

    try:

        response = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=30
        )

        print("SEND:", response.text)

        return response.json()

    except Exception as e:

        print("SEND ERROR:", e)

        return None


# =========================
# هوش مصنوعی
# =========================

def ask_ai(text):

    system_prompt = """
تو «ربیکا» هستی؛ یک ربات گروهی فارسی‌زبان.

شخصیت تو:
- شوخ
- بازیگوش
- صمیمی
- مهربان
- کمی شیطون

قوانین:
- همیشه فارسی جواب بده.
- جواب‌ها معمولاً کوتاه و طبیعی باشند.
- از ایموجی مناسب استفاده کن.
- اگر کاربر شوخی کرد، شوخی کن.
- اگر سؤال جدی پرسید، جدی جواب بده.
- اگر بازی خواست، بازی پیشنهاد بده.
- اگر جوک خواست، جوک بگو.
- اگر معما خواست، معما بگو.
- اگر فال خواست، فقط برای سرگرمی فال بگو.
- ادعا نکن که واقعاً آینده را می‌بینی.
- خودت را انسان واقعی معرفی نکن.
- تو ربات فروشگاه نیستی.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content


# =========================
# پاسخ‌های ربیکا
# =========================

def make_reply(text):

    text = text.strip()

    # فال
    if "فال" in text:

        fortunes = [
            "🔮 یه اتفاق خوب در راهته؛ فقط عجله نکن 😌",
            "🔮 امروز یه خبر جالب می‌شنوی 👀",
            "🔮 یه نفر بهت فکر می‌کنه... حالا کیه؟ خودت کشفش کن 😂",
            "🔮 شانس باهاته؛ فقط پولتو الکی خرج نکن 😎",
            "🔮 یه شروع تازه در راهته ✨",
            "🔮 چیزی که منتظرشی ممکنه زودتر برسه 🌹"
        ]

        return random.choice(fortunes)


    # جوک
    if "جوک" in text:

        jokes = [
            "😂 زندگی کوتاهه، ولی پیام‌های گروه تمومی ندارن!",
            "😂 یه روز تصمیم گرفتم آدم عاقل‌تری باشم... منصرف شدم!",
            "😂 به خودم گفتم آروم باش... گفتم اول خودت آروم شو!",
            "😂 من نیومدم گروه رو شلوغ کنم، خود گروه منو شلوغ کرد 😂"
        ]

        return random.choice(jokes)


    # بازی
    if "بازی" in text:

        games = [
            "🎮 جرئت یا حقیقت؟ 😈",
            "🎮 یه عدد بین ۱ تا ۱۰ انتخاب کن!",
            "🎮 شیر یا خط؟ 🪙",
            "🎮 معما می‌خوای یا جرئت؟ 👀",
            "🎮 اسم و فامیل بازی کنیم؟ 😎"
        ]

        return random.choice(games)


    # معما
    if "معما" in text:

        return (
            "🧩 یه معما برات دارم:\n\n"
            "اون چیه که هرچی بیشتر ازش برداری، "
            "بزرگ‌تر میشه؟ 🤔"
        )


    # سلام
    if "سلام" in text:

        return random.choice([
            "سلاممم 😎🌹",
            "جانم؟ بالاخره یکی صدام کرد 😂",
            "سلام رفیق 👋 چه خبر؟",
            "سلام 😌 امروز چه نقشه‌ای داری؟"
        ])


    # هوش مصنوعی
    try:

        return ask_ai(text)

    except Exception as e:

        print("AI ERROR:", e)

        return random.choice([
            "😂 یه لحظه مغزم هنگ کرد!",
            "صبر کن، مغز مصنوعیم قاط کرد 😐😂",
            "اوپس! دوباره بگو ببینم چی گفتی 👀"
        ])


# =========================
# ثبت Webhook
# =========================

def set_webhook():

    if not TOKEN:

        print("ERROR: RUBIKA_TOKEN پیدا نشد")

        return


    if not RENDER_URL:

        print("ERROR: RENDER_EXTERNAL_URL پیدا نشد")

        return


    webhook_url = RENDER_URL.rstrip("/") + "/receiveUpdate"

    print("WEBHOOK URL:", webhook_url)


    data = {
        "url": webhook_url,
        "type": "ReceiveUpdate"
    }


    try:

        response = requests.post(
            f"{API}/updateBotEndpoints",
            json=data,
            timeout=30
        )

        print("WEBHOOK RESPONSE:", response.text)

    except Exception as e:

        print("WEBHOOK ERROR:", e)


# =========================
# Health Check
# =========================

@app.route("/healthz")
def health():

    return "OK"


# =========================
# دریافت پیام روبیکا
# =========================

@app.route("/receiveUpdate", methods=["POST"])
def receive_update():

    update = request.get_json(silent=True) or {}

    print("================================")
    print("UPDATE:", update)


    data = update.get(
        "data",
        update
    )


    update_data = data.get(
        "update",
        data
    )


    update_type = update_data.get(
        "type"
    )


    print("TYPE:", update_type)


    # فقط پیام جدید
    if update_type != "NewMessage":

        return "OK"


    message = update_data.get(
        "new_message",
        {}
    )


    chat_id = update_data.get(
        "chat_id"
    )


    text = message.get(
        "text",
        ""
    )


    print("CHAT:", chat_id)
    print("TEXT:", text)


    if not chat_id or not text:

        return "OK"


    # =========================
    # فقط وقتی ربیکا صدا زده شود
    # =========================

    if BOT_NAME not in text:

        print("ربیکا صدا زده نشده.")

        return "OK"


    # حذف اسم ربیکا
    user_text = text.replace(
        BOT_NAME,
        "",
        1
    ).strip()


    # فقط اسم ربیکا گفته شده
    if not user_text:

        answer = random.choice([
            "جانم؟ 😎",
            "بله؟ صدام کردی؟ 😂",
            "اینجام 👀",
            "چی شده رفیق؟ 😌",
            "ها؟ منو کار داشتی؟ 😂"
        ])

    else:

        answer = make_reply(user_text)


    # ارسال جواب
    send_message(
        chat_id,
        answer
    )


    print("ANSWER:", answer)
    print("================================")


    return "OK"


# =========================
# ثبت Webhook هنگام شروع
# =========================

print("================================")
print("🤖 ربیکا در حال شروع است...")
print("================================")

set_webhook()
