from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "7668843152:AAG58tszCSeS_kiP0mGP6vWLLFcNPTLwgdk"
adminler = {8143084360}

kanallar = []
vpn_kody = "🟢 Täze VPN: DARKTUNNEL-123456"
banlananlar = []
ulanyjylar = set()

def agzalygy_barla(user_id, context):
    not_joined = []
    for name, url in kanallar:
        kanal_username = url.split("/")[-1]
        try:
            member = context.bot.get_chat_member(chat_id=f"@{kanal_username}", user_id=user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(name)
        except:
            not_joined.append(name)
    return not_joined

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ulanyjylar.add(user_id)

    if user_id in banlananlar:
        await update.message.reply_text("🚫 Siz banlandyňyz.")
        return

    kanal_buttons = []
    row = []

    for i, (name, url) in enumerate(kanallar, 1):
        row.append(InlineKeyboardButton(name, url=url))
        if i % 3 == 0:
            kanal_buttons.append(row)
            row = []

    if row:
        kanal_buttons.append(row)

    kanal_buttons.append([InlineKeyboardButton("✅ Kody alyň", callback_data="kody_al")])
    keyboard = InlineKeyboardMarkup(kanal_buttons)

    await update.message.reply_text("👋 Kanallara goşulyň we VPN kody alyň:", reply_markup=keyboard)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "kody_al":
        if user_id in banlananlar:
            await query.message.reply_text("🚫 Siz banlandyňyz.")
            return

        not_joined = []
        for name, url in kanallar:
            kanal_username = url.split("/")[-1]
            try:
                member = await context.bot.get_chat_member(chat_id=f"@{kanal_username}", user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(name)
            except:
                not_joined.append(name)

        if not_joined:
            await query.message.reply_text("📛 Iltimas, şu kanallara goşulyň:\n" + "\n".join(f"• {n}" for n in not_joined))
            return

        await query.message.reply_text(vpn_kody)

    elif query.data == "panel":
        if user_id not in adminler:
            await query.message.reply_text("❌ Bu diňe admin üçin.")
            return
        await show_panel(update, context)

    elif query.data == "banla":
        context.user_data["banla"] = True
        await query.message.reply_text("Ulanyjy ID giriziň (banlamak üçin):")

    elif query.data == "ban_ac":
        context.user_data["ban_ac"] = True
        await query.message.reply_text("ID giriziň (ban açmak üçin):")

    elif query.data == "vpn_uytget":
        context.user_data["vpn_uytget"] = True
        await query.message.reply_text("Täze VPN koduny giriziň:")

    elif query.data == "bildiris":
        context.user_data["bildiris"] = True
        await query.message.reply_text("Bildirişi giriziň:")

    elif query.data == "kanal_gos":
        context.user_data["kanal_gos"] = True
        await query.message.reply_text("Kanal ady we URL giriziň. Mysal: Kanal Ady | https://t.me/kanal")

    elif query.data == "kanal_ayyr":
        if not kanallar:
            await query.message.reply_text("📭 Kanal ýok.")
        else:
            kanal_list = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän kanalyňyzyň belgisi:\n{kanal_list}")
            context.user_data["kanal_ayyr"] = True

    elif query.data == "admin_gos":
        context.user_data["admin_gos"] = True
        await query.message.reply_text("Täze admin ID giriziň:")

    elif query.data == "admin_ayyr":
        if len(adminler) <= 1:
            await query.message.reply_text("⚠️ Diňe bir admin bar.")
            return
        admin_list = "\n".join(str(aid) for aid in adminler)
        await query.message.reply_text(f"Aýyrmak isleýän adminiň ID-si:\n{admin_list}")
        context.user_data["admin_ayyr"] = True

async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Ban ulanyjy", callback_data="banla")],
        [InlineKeyboardButton("♻️ Ban aç", callback_data="ban_ac")],
        [InlineKeyboardButton("🔁 VPN kod üýtget", callback_data="vpn_uytget")],
        [InlineKeyboardButton("📢 Bildiriş ugrat", callback_data="bildiris")],
        [InlineKeyboardButton("➕ Kanal Goş", callback_data="kanal_gos")],
        [InlineKeyboardButton("➖ Kanal Aýyr", callback_data="kanal_ayyr")],
        [InlineKeyboardButton("👤➕ Admin Goş", callback_data="admin_gos")],
        [InlineKeyboardButton("👤➖ Admin Aýyr", callback_data="admin_ayyr")]
    ])
    await update.message.reply_text("🛠 Admin panel:", reply_markup=admin_keyboard)

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in adminler:
        return
    await show_panel(update, context)

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get("banla"):
        try:
            banlananlar.append(int(text))
            await update.message.reply_text("✅ Banlandy.")
        except:
            await update.message.reply_text("❌ Nädogry ID")
        del context.user_data["banla"]

    elif context.user_data.get("ban_ac"):
        try:
            banlananlar.remove(int(text))
            await update.message.reply_text("✅ Ban açyldy.")
        except:
            await update.message.reply_text("❌ ID tapylmady")
        del context.user_data["ban_ac"]

    elif context.user_data.get("vpn_uytget"):
        global vpn_kody
        vpn_kody = text
        await update.message.reply_text("✅ Kody üýtgedildi.")
        del context.user_data["vpn_uytget"]

    elif context.user_data.get("bildiris"):
        for uid in ulanyjylar:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 Bildiriş:\n{text}")
            except:
                pass
        await update.message.reply_text("✅ Bildiriş ugradyldy!")
        del context.user_data["bildiris"]

    elif context.user_data.get("kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            kanallar.append((ad, url))
            await update.message.reply_text("✅ Kanal goşuldy")
        except:
            await update.message.reply_text("❌ Format ýalňyş. Mysal: Ady | https://t.me/kanal")
        del context.user_data["kanal_gos"]

    elif context.user_data.get("kanal_ayyr"):
        try:
            indeks = int(text) - 1
            pozuldy = kanallar.pop(indeks)
            await update.message.reply_text(f"❎ Kanal aýryldy: {pozuldy[0]}")
        except:
            await update.message.reply_text("❌ Nädogry belgi")
        del context.user_data["kanal_ayyr"]

    elif context.user_data.get("admin_gos"):
        try:
            täze = int(text)
            if täze in adminler:
                await update.message.reply_text("🔁 Eýýäm admin")
            else:
                adminler.add(täze)
                await update.message.reply_text("✅ Täze admin goşuldy")
        except:
            await update.message.reply_text("❌ ID nädogry")
        del context.user_data["admin_gos"]

    elif context.user_data.get("admin_ayyr"):
        try:
            aid = int(text)
            if aid not in adminler:
                await update.message.reply_text("❌ Admin tapylmady")
            elif len(adminler) == 1:
                await update.message.reply_text("⚠️ Diňe bir admin bar")
            else:
                adminler.remove(aid)
                await update.message.reply_text("✅ Admin aýryldy")
        except:
            await update.message.reply_text("❌ ID nädogry")
        del context.user_data["admin_ayyr"]

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT, mesaj_handler))

print("✅ Bot başlady!")
app.run_polling()
