from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import asyncio

TOKEN = "7668843152:AAG58tszCSeS_kiP0mGP6vWLLFcNPTLwgdk"
adminler = {8143084360}

kanallar = [
    ("𝐎𝐨𝐭 𝐪𝐞𝐶", "https://t.me/mega_keys"),
    ("𝐋𝐞𝐨 𝐒𝐨𝐫𝐞𝐫𝐨𝐭 🦁🔐", "https://t.me/Lion_Servers"),
    ("𝔺𝔢𝕋𝔨 𝔿𝔺𝔽 𝔬𝕋𝕀𝕀", "https://t.me/VPNDayka")
]

vpn_kody = "🟢 Täze VPN: DARKTUNNEL-123456"
banlananlar = []
ilkigirenler = set()
ulanyjylar = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    is_ilki = user_id not in ilkigirenler
    ilkigirenler.add(user_id)
    ulanyjylar.add(user_id)

    if user_id in banlananlar and not is_ilki:
        await update.message.reply_text("🚫 Siz banlandyňyz.")
        return

    kanal_buttons = [InlineKeyboardButton(name, url=url) for name, url in kanallar]
    keyboard = InlineKeyboardMarkup([
        kanal_buttons,
        [InlineKeyboardButton("✅ Kody alyň", callback_data="kody_al")]
    ])

    await update.message.reply_text(
        "👋 Salam! Aşakdaky kanallara goşulyň we VPN kody alyň:",
        reply_markup=keyboard
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "kody_al":
        if user_id in banlananlar:
            await query.message.reply_text("\ud83d\udeab Siz banlandy\u0148yz.")
            return

        not_joined = []
        for name, url in kanallar:
            kanal_username = url.split("/")[-1]
            try:
                member = await context.bot.get_chat_member(chat_id=f"@{kanal_username}", user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(name)
            except Exception as e:
                print(f"Kanala barlagda ýalňyşlyk: {e}")
                not_joined.append(name)

        if not_joined:
            await query.message.reply_text("\ud83d\udccb Iltimas, aşakdaky kanallara agza boluň:\n" + "\n".join(f"• {ad}" for ad in not_joined))
            return

        await query.message.reply_text(vpn_kody)

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in adminler:
        return
    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("\u274c Ban ulanyjy", callback_data="banla")],
        [InlineKeyboardButton("\u267b\ufe0f Ban aç", callback_data="ban_ac")],
        [InlineKeyboardButton("\ud83d\udd01 VPN kod üýtget", callback_data="vpn_uytget")],
        [InlineKeyboardButton("\ud83d\udce2 Bildiriş ugrat", callback_data="bildiris")],
        [InlineKeyboardButton("\u2795 Kanal Goş", callback_data="kanal_gos")],
        [InlineKeyboardButton("\u2796 Kanal Aýyr", callback_data="kanal_ayyr")],
        [InlineKeyboardButton("\ud83d\udc64➕ Admin Goş", callback_data="admin_gos")],
        [InlineKeyboardButton("\ud83d\udc64➖ Admin Aýyr", callback_data="admin_ayyr")]
    ])
    await update.message.reply_text("\ud83d\udee0 Admin panel:", reply_markup=admin_keyboard)

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in adminler:
        return

    context_data = context.user_data

    if query.data == "banla":
        await query.message.reply_text("Banlamak üçin ulanyjynyň ID-sini ýaz:")
        context_data["banla"] = True

    elif query.data == "ban_ac":
        await query.message.reply_text("Ban açmak üçin ID-ni ýaz:")
        context_data["ban_ac"] = True

    elif query.data == "vpn_uytget":
        await query.message.reply_text("Täze VPN koduny giriz:")
        context_data["vpn_uytget"] = True

    elif query.data == "bildiris":
        await query.message.reply_text("Ugratmaly bildirişi ýaz:")
        context_data["bildiris"] = True

    elif query.data == "kanal_gos":
        await query.message.reply_text("Täze kanal ady we URL giriziň:\nMysal: Kanal Ady | https://t.me/kanal")
        context_data["kanal_gos"] = True

    elif query.data == "kanal_ayyr":
        if not kanallar:
            await query.message.reply_text("\ud83d\udccd Häzirki wagtda kanal ýok.")
            return
        kanal_list = "\n".join(f"{i+1}. {ad} ({url})" for i, (ad, url) in enumerate(kanallar))
        await query.message.reply_text(f"Aýyrmak isleýän kanalyňyzyň belgisi:\n{kanal_list}")
        context_data["kanal_ayyr"] = True

    elif query.data == "admin_gos":
        await query.message.reply_text("Täze adminiň Telegram ID-sini giriziň:")
        context_data["admin_gos"] = True

    elif query.data == "admin_ayyr":
        if len(adminler) <= 1:
            await query.message.reply_text("⚠️ Diňe bir admin bar, aýrylyp bilinmez.")
            return
        admin_list = "\n".join(f"{i+1}. {aid}" for i, aid in enumerate(adminler))
        await query.message.reply_text(
            "Aýyrmak isleýän adminiň ID-sini giriziň:\n" + admin_list
        )
        context_data["admin_ayyr"] = True

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    context_data = context.user_data

    if context_data.get("banla"):
        try:
            banlananlar.append(int(text))
            await update.message.reply_text("✅ Ulanyjy banlandy!")
        except:
            await update.message.reply_text("❌ Nädogry ID!")
        del context_data["banla"]

    elif context_data.get("ban_ac"):
        try:
            banlananlar.remove(int(text))
            await update.message.reply_text("✅ Ban açyldy!")
        except:
            await update.message.reply_text("❌ ID tapylmady!")
        del context_data["ban_ac"]

    elif context_data.get("vpn_uytget"):
        global vpn_kody
        vpn_kody = text
        await update.message.reply_text("✅ Täze VPN kody girizildi!")
        del context_data["vpn_uytget"]

    elif context_data.get("bildiris"):
        for uid in ulanyjylar:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 Bildiriş:\n{text}")
            except Exception as e:
                print(f"❌ Ugratmak bolmady: {uid} → {e}")
        await update.message.reply_text("📢 Bildiriş ugradyldy!")
        del context_data["bildiris"]

    elif context_data.get("kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError("URL nädogry")
            kanallar.append((ad, url))
            await update.message.reply_text("✅ Kanal goşuldy!")
        except:
            await update.message.reply_text("❌ Format nädogry. Mysal: Kanal Ady | https://t.me/kanal")
        del context_data["kanal_gos"]

    elif context_data.get("kanal_ayyr"):
        try:
            indeks = int(text) - 1
            pozuldy = kanallar.pop(indeks)
            await update.message.reply_text(f"❎ Kanal aýryldy: {pozuldy[0]}")
        except:
            await update.message.reply_text("❌ Nädogry belgä girildi.")
        del context_data["kanal_ayyr"]

    elif context_data.get("admin_gos"):
        try:
            täze_id = int(text)
            if täze_id in adminler:
                await update.message.reply_text("ℹ️ Bu ulanyjy eýýäm admin.")
            else:
                adminler.add(täze_id)
                await update.message.reply_text(f"✅ Täze admin goşuldy! ID: {täze_id}")
        except:
            await update.message.reply_text("❌ Nädogry ID formaty!")
        del context_data["admin_gos"]

    elif context_data.get("admin_ayyr"):
        try:
            ayrylýan_id = int(text)
            if ayrylýan_id not in adminler:
                await update.message.reply_text("❌ Bu ID admin däl!")
            elif len(adminler) == 1:
                await update.message.reply_text("⚠️ Diňe bir admin bar, aýryp bolmaýar.")
            elif ayrylýan_id == user_id:
                await update.message.reply_text("⚠️ Siz özüňizi adminlikden aýryp bilmersiňiz!")
            else:
                adminler.remove(ayrylýan_id)
                await update.message.reply_text(f"✅ Admin aýryldy: {ayrylýan_id}")
        except:
            await update.message.reply_text("❌ ID formaty nädogry!")
        del context_data["admin_ayyr"]

# === Boty işledýän ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback_handler, pattern="^kody_al$"))
app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^(banla|ban_ac|vpn_uytget|bildiris|kanal_gos|kanal_ayyr|admin_gos|admin_ayyr)$"))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(MessageHandler(filters.TEXT, mesaj_handler))

print("✅ Bot başlady!")
app.run_polling()
    
