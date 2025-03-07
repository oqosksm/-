import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ جلب القيم من المتغيرات البيئية
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("hmsa_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ تخزين الهمسات لكل مستخدم
hmses = {}

@app.on_message(filters.command("start"))
def start_message(client, message):
    if len(message.command) > 1 and message.command[1].startswith("hms"):
        try:
            hms_data = message.command[1].replace("hms", "")
            from_id, to_id, chat_id = map(int, hms_data.split("to")[0], hms_data.split("to")[-1].split("in")[0], hms_data.split("in")[-1])

            hmses[message.from_user.id] = {"from": from_id, "to": to_id, "chat": chat_id}

            message.reply_text(
                "✏️ **اكتب الهمسة الآن وسيتم إرسالها بشكل سري**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="hms_cancel")]])
            )
        except Exception as e:
            message.reply_text("❌ حدث خطأ في معالجة الهمسة!")
            print(f"خطأ: {e}")
    else:
        user_name = message.from_user.first_name
        text = f"""
👋 مرحبًا {user_name}، أهلاً بك في بوت **همسة**! 💬

🔹 هذا البوت يتيح لك إرسال واستقبال الهمسات السرية بين أعضاء المجموعات. 🔐
🔹 يمكنك الرد على أي رسالة بكلمة "همسة" لإرسال رسالة خاصة لا يراها إلا المستقبل.

👨‍💻 المطور: [@Sm_ar_t](https://t.me/Sm_ar_t)
"""
        message.reply_text(text, disable_web_page_preview=True)

@app.on_message(filters.reply & filters.regex("همسه") & filters.group)
def reply_with_link(client, message):
    try:
        user_id = message.reply_to_message.from_user.id
        my_id = message.from_user.id
        chat_id = message.chat.id

        bot_username = client.get_me().username
        start_link = f"https://t.me/{bot_username}?start=hms{my_id}to{user_id}in{chat_id}"

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("- اضغط لإرسال الهمسة! 💌", url=start_link)]
        ])
        message.reply_text("🔒 اضغط لإرسال همسة سرية!", reply_markup=reply_markup)
    except Exception as e:
        message.reply_text("❌ حدث خطأ أثناء إنشاء رابط الهمسة!")
        print(f"خطأ: {e}")

@app.on_message(filters.private & filters.text & ~filters.command("start"))
def send_hms(client, message):
    user_id = message.from_user.id

    if user_id not in hmses:
        message.reply_text("❌ لا يوجد طلب همسة نشط. قم بإرسال همسة جديدة من المجموعة.")
        return

    hms_data = hmses[user_id]
    to_id = hms_data["to"]
    from_id = hms_data["from"]
    chat_id = hms_data["chat"]

    hmses[to_id] = {"hms": message.text, "chat": chat_id}

    message.reply_text("✅ تم إرسال الهمسة بنجاح!")

    to_url = f"tg://openmessage?user_id={to_id}"
    from_url = f"tg://openmessage?user_id={from_id}"

    app.send_message(
        chat_id=chat_id,
        text=f"📩 لديك همسة من [{app.get_chat(from_id).first_name}]({from_url})!\n🔐 أنت فقط من يمكنه رؤيتها.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("- اضغط لرؤية الهمسة 👀", callback_data="hms_answer")]
        ])
    )

    del hmses[user_id]

@app.on_callback_query(filters.regex("hms_answer"))
def display_hms(client, callback):
    user_id = callback.from_user.id

    if user_id in hmses:
        callback.answer(hmses[user_id]["hms"], show_alert=True)
        del hmses[user_id]
    else:
        callback.answer("❌ لا توجد همسة لك!", show_alert=True)

@app.on_callback_query(filters.regex("hms_cancel"))
def cancel_hms(client, callback):
    user_id = callback.from_user.id

    if user_id in hmses:
        del hmses[user_id]
        callback.message.edit_text("❌ تم إلغاء إرسال الهمسة.")
    else:
        callback.answer("❌ لا يوجد طلب همسة نشط.")

if __name__ == "__main__":
    app.run()