import logging
import random
from datetime import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

WORDS = [
    ("Привет","Salom","Privet"),("Пока","Xayr","Paka"),("Да","Ha","Da"),
    ("Нет","Yo'q","Net"),("Спасибо","Rahmat","Spasibo"),("Хорошо","Yaxshi","Khorosho"),
    ("Плохо","Yomon","Plokho"),("Вода","Suv","Voda"),("Хлеб","Non","Khleb"),
    ("Дом","Uy","Dom"),("Мама","Ona","Mama"),("Папа","Ota","Papa"),
    ("Друг","Do'st","Drug"),("Кошка","Mushuk","Koshka"),("Собака","It","Sobaka"),
    ("Один","Bir","Odin"),("Два","Ikki","Dva"),("Три","Uch","Tri"),
    ("Большой","Katta","Bolshoy"),("Красивый","Chiroyli","Krasiviy"),
]

PHRASES = [
    ("Как вас зовут?","Ismingiz nima?","Kak vas zovut?"),
    ("Меня зовут ...","Mening ismim ...","Menya zovut ..."),
    ("Как дела?","Ahvolingiz qanday?","Kak dela?"),
    ("Всё хорошо","Hammasi yaxshi","Vsyo khorosho"),
    ("Я не понимаю","Men tushunmadim","Ya ne ponimayu"),
    ("Сколько стоит?","Qancha turadi?","Skolko stoit?"),
    ("Доброе утро","Xayrli tong","Dobroye utro"),
    ("Добрый вечер","Xayrli kech","Dobryy vecher"),
    ("Спокойной ночи","Xayrli tun","Spokoynoy nochi"),
    ("Я из Узбекистана","Men O'zbekistondan","Ya iz Uzbekistana"),
]

user_scores = {}

def get_score(uid):
    return user_scores.get(uid, {"score":0,"streak":0,"total":0})

def update_score(uid, correct):
    s = get_score(uid)
    if correct: s["score"]+=10; s["streak"]+=1
    else: s["streak"]=0
    s["total"]+=1
    user_scores[uid]=s
    return s

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📚 So'z o'rgan", callback_data="word")],
        [InlineKeyboardButton("💬 Iboralar", callback_data="phrases")],
        [InlineKeyboardButton("🧠 Test", callback_data="quiz")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
    ]
    await update.message.reply_text(
        f"Salom {update.effective_user.first_name}! 🇷🇺\n\n"
        "Har kuni 8:00 va 20:00 da dars eslatmasi keladi!\n\nBo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    jq = context.job_queue
    cid = update.effective_chat.id
    for j in jq.get_jobs_by_name(str(cid)): j.schedule_removal()
    jq.run_daily(morning_cb, time=time(3,0), chat_id=cid, name=str(cid), data=cid)
    jq.run_daily(evening_cb, time=time(15,0), chat_id=cid, name=str(cid)+"e", data=cid)

async def morning_cb(context: ContextTypes.DEFAULT_TYPE):
    w = random.choice(WORDS)
    await context.bot.send_message(context.job.data,
        f"☀️ Xayrli tong! Bugungi so'z:\n\n🇷🇺 *{w[0]}*\n🇺🇿 {w[1]}\n🔤 [{w[2]}]\n\n5 marta yozing! ✍️",
        parse_mode="Markdown")

async def evening_cb(context: ContextTypes.DEFAULT_TYPE):
    p = random.choice(PHRASES)
    await context.bot.send_message(context.job.data,
        f"🌙 Kechqurun darsi:\n\n💬 *{p[0]}*\n🇺🇿 {p[1]}\n🔤 [{p[2]}]\n\nBu iborani ishlatib ko'ring! 😊",
        parse_mode="Markdown")

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    d = q.data

    if d == "menu":
        kb = [[InlineKeyboardButton("📚 So'z o'rgan",callback_data="word")],
              [InlineKeyboardButton("💬 Iboralar",callback_data="phrases")],
              [InlineKeyboardButton("🧠 Test",callback_data="quiz")],
              [InlineKeyboardButton("📊 Statistika",callback_data="stats")]]
        await q.edit_message_text("Bo'limni tanlang:", reply_markup=InlineKeyboardMarkup(kb))

    elif d == "word":
        w = random.choice(WORDS); context.user_data["w"]=w
        kb = [[InlineKeyboardButton("👁 Tarjimani ko'r",callback_data="show")],
              [InlineKeyboardButton("🧠 Test",callback_data="quiz"),InlineKeyboardButton("🏠 Menu",callback_data="menu")]]
        await q.edit_message_text(f"📚 So'z:\n\n🇷🇺 *{w[0]}*\n🔤 [{w[2]}]\n\nTarjimasini bilesizmi?",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif d == "show":
        w = context.user_data.get("w", random.choice(WORDS))
        kb = [[InlineKeyboardButton("➡️ Keyingi",callback_data="word")],
              [InlineKeyboardButton("🏠 Menu",callback_data="menu")]]
        await q.edit_message_text(f"📚 So'z:\n\n🇷🇺 *{w[0]}*\n🇺🇿 ✅ {w[1]}\n🔤 [{w[2]}]",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif d == "phrases":
        sel = random.sample(PHRASES, 3)
        txt = "💬 *Iboralar:*\n\n"
        for p in sel: txt += f"🇷🇺 {p[0]}\n🇺🇿 {p[1]}\n🔤 [{p[2]}]\n\n"
        kb = [[InlineKeyboardButton("🔄 Boshqalari",callback_data="phrases"),
               InlineKeyboardButton("🏠 Menu",callback_data="menu")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif d == "quiz":
        correct = random.choice(WORDS)
        wrong = random.sample([w for w in WORDS if w[0]!=correct[0]], 3)
        opts = wrong+[correct]; random.shuffle(opts)
        context.user_data["qw"] = correct
        kb = [[InlineKeyboardButton(o[1], callback_data=f"a_{o[0]}_{correct[0]}")] for o in opts]
        await q.edit_message_text(f"🧠 *Test:*\n\n🇷🇺 *{correct[0]}* — qaysi tarjima?",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif d.startswith("a_"):
        parts = d.split("_",2); chosen=parts[1]; correct=parts[2]
        ok = chosen==correct
        s = update_score(update.effective_user.id, ok)
        if ok: msg=f"✅ *To'g'ri!* +10 ball 🎉\n🔥 Ketma-ket: {s['streak']}"
        else:
            ctr = next((w[1] for w in WORDS if w[0]==correct),"?")
            msg=f"❌ *Xato!*\nTo'g'ri: {ctr}"
        kb = [[InlineKeyboardButton("🔄 Yana",callback_data="quiz"),
               InlineKeyboardButton("🏠 Menu",callback_data="menu")]]
        await q.edit_message_text(msg+f"\n\n⭐ Ball: {s['score']} | Savollar: {s['total']}",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif d == "stats":
        s = get_score(update.effective_user.id)
        acc = round(s["score"]/10/s["total"]*100) if s["total"]>0 else 0
        kb = [[InlineKeyboardButton("🏠 Menu",callback_data="menu")]]
        await q.edit_message_text(
            f"📊 *Statistika:*\n\n⭐ Ball: {s['score']}\n🔥 Ketma-ket: {s['streak']}\n"
            f"📝 Savollar: {s['total']}\n✅ To'g'rilik: {acc}%\n\nZo'r ketayapsiz! 💪",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def main():
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    print("Bot ishga tushdi! ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
