import asyncio
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 👤 ADMIN CONFIGURATION
ADMIN_ID = 8143084360
ALLOWED_USERS = set()  # Admin goşar

# 🗂️ Session & Scheduling Data
user_sessions = {}
waiting_for = {}
scheduled_posts = []
previous_messages = {}

# 🔧 Utility: Main Menu Keyboard
def main_menu_keyboard(user_id=None):
    buttons = [
        [InlineKeyboardButton("📤 Reklama Goýmаk", callback_data='reklama')],
        [InlineKeyboardButton("📊 Statistika", callback_data='statistika')],
        [InlineKeyboardButton("📂 Postlarym", callback_data='postlarym')]
    ]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data='admin_panel')])
    return InlineKeyboardMarkup(buttons)

# 🚀 START Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "👋 Hoş geldiňiz! Aşakdaky menýulardan birini saýlaň:",
        reply_markup=main_menu_keyboard(user_id)
    )

# 🤖 BUTTON Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == 'admin_panel' and user_id == ADMIN_ID:
        await query.edit_message_text(
            "⚙️ Admin Panel:\nUlanyjy dolandyryşlaryny saýlaň:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Ulanyjy goş", callback_data='add_user')],
                [InlineKeyboardButton("➖ Ulanyjy aýyr", callback_data='remove_user')],
                [InlineKeyboardButton("📋 Sanawy gör", callback_data='list_users')],
                [InlineKeyboardButton("📢 Bildiriş Ugrat", callback_data='send_announcement')],
                [InlineKeyboardButton("⬅ Yza", callback_data='back')]
            ])
        )

    elif data == 'add_user' and user_id == ADMIN_ID:
        waiting_for[user_id] = 'add_user'
        await query.edit_message_text("🆔 Goşmaly ulanyjynyň ID-sini giriziň:")

    elif data == 'remove_user' and user_id == ADMIN_ID:
        waiting_for[user_id] = 'remove_user'
        await query.edit_message_text("🆔 Aýyrmaly ulanyjynyň ID-sini giriziň:")

    elif data == 'list_users' and user_id == ADMIN_ID:
        if not ALLOWED_USERS:
            await query.edit_message_text("📭 Hiç hili ulanyjy goşulmady.")
        else:
            lines = []
            for uid in ALLOWED_USERS:
                try:
                    user = await context.bot.get_chat(uid)
                    display = f"@{user.username}" if user.username else user.first_name
                    lines.append(f"{uid} {display}")
                except:
                    lines.append(f"{uid} ❌ (ulanyjy tapylmady)")
            text = "✅ Rugsat berlen ulanyjylar:\n" + "\n".join(lines)
            await query.edit_message_text(text)

    elif data == 'send_announcement' and user_id == ADMIN_ID:
        waiting_for[user_id] = 'announcement'
        await query.edit_message_text("✍ Ugratmaly bildirişi giriziň:")

    elif data == 'confirm_announcement' and user_id == ADMIN_ID:
        announcement_text = context.user_data.get('announcement_text')
        sent_count = 0
        failed_users = []

        for uid in ALLOWED_USERS.union({ADMIN_ID}):
            try:
                await context.bot.send_message(uid, f"📢 Bildiriş:\n\n{announcement_text}")
                sent_count += 1
            except:
                failed_users.append(uid)

        result_msg = f"✅ Bildiriş {sent_count} ulanyja ugradyldy."
        if failed_users:
            result_msg += f"\n⚠️ Ugratmak başartmady: {', '.join(str(u) for u in failed_users)}"

        await query.edit_message_text(result_msg)
        waiting_for.pop(user_id, None)
        context.user_data.pop('announcement_text', None)

    elif data == 'cancel_announcement' and user_id == ADMIN_ID:
        waiting_for.pop(user_id, None)
        context.user_data.pop('announcement_text', None)
        await query.edit_message_text("❌ Bildiriş ýatyryldy.")

    elif data == 'back':
        await query.edit_message_text("🔙 Yza gaýdýarys...", reply_markup=main_menu_keyboard(user_id))

    elif data == 'reklama':
        if user_id != ADMIN_ID and user_id not in ALLOWED_USERS:
            await query.edit_message_text("❌ Bu bölüme girmek üçin rugsat ýok.")
            return
        await query.edit_message_text(
            "📌 Post görnüşini saýlaň:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🖼 Surat", callback_data='surat'),
                InlineKeyboardButton("✏ Tekst", callback_data='tekst')
            ]])
        )

    elif data in ['surat', 'tekst']:
        if user_id != ADMIN_ID and user_id not in ALLOWED_USERS:
            await query.edit_message_text("❌ Bu bölüme girmek üçin rugsat ýok.")
            return
        user_sessions[user_id] = {'type': data}
        waiting_for[user_id] = 'photo' if data == 'surat' else 'text'
        prompt = "🖼 Surat ugradyň:" if data == 'surat' else "✍ Tekst giriziň:"
        await query.edit_message_text(prompt)

    elif data == 'statistika':
        kanal_sany = len({p['channel'] for p in scheduled_posts})
        post_sany = len(scheduled_posts)
        await query.edit_message_text(f"📊 Statistik:\n📢 Kanallar: {kanal_sany}\n📬 Postlar: {post_sany}")

    elif data == 'postlarym':
        if user_id != ADMIN_ID and user_id not in ALLOWED_USERS:
            await query.edit_message_text("❌ Bu bölüme girmek üçin rugsat ýok.")
            return
        user_posts = [p for p in scheduled_posts if p['user_id'] == user_id]
        if not user_posts:
            await query.edit_message_text("📭 Siziň postlaryňyz ýok.")
            return
        buttons = [
            [InlineKeyboardButton(
                f"{i+1}) {p['channel']} ({'⏸' if p.get('paused') else '▶'})",
                callback_data=f"post_{i}"
            )] for i, p in enumerate(user_posts)
        ]
        await query.edit_message_text("📂 Postlaryňyz:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith('post_'):
        idx = int(data.split('_')[1])
        user_posts = [p for p in scheduled_posts if p['user_id'] == user_id]
        if idx >= len(user_posts): return
        post = user_posts[idx]
        real_idx = scheduled_posts.index(post)
        ctrl = [
            InlineKeyboardButton("🗑 Poz", callback_data=f"delete_{real_idx}"),
            InlineKeyboardButton("▶ Dowam" if post.get('paused') else "⏸ Duruz", callback_data=f"toggle_{real_idx}")
        ]
        await query.edit_message_text(
            f"📤 Kanal: {post['channel']}\n🕒 Minut: {post['minute']}\n📆 Gün: {post['day']}\n📮 Ugradylan: {post['sent_count']}\n🔁 Galyan: {post['max_count'] - post['sent_count']}",
            reply_markup=InlineKeyboardMarkup([ctrl])
        )

    elif data.startswith('delete_'):
        idx = int(data.split('_')[1])
        if idx < len(scheduled_posts):
            scheduled_posts.pop(idx)
        await query.edit_message_text("✅ Post pozuldy.")

    elif data.startswith('toggle_'):
        idx = int(data.split('_')[1])
        if idx < len(scheduled_posts):
            scheduled_posts[idx]['paused'] = not scheduled_posts[idx].get('paused', False)
        await query.edit_message_text("🔄 Status üýtgedildi.")

# 💬 MESSAGE Handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

# Admin üçin ulanyjy dolandyryşy
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID and user_id in waiting_for:
        step = waiting_for[user_id]

        if step == 'add_user':
            try:
                new_id = int(update.message.text)
                ALLOWED_USERS.add(new_id)
                await update.message.reply_text("✅ Ulanyjy goşuldy.")
            except:
                await update.message.reply_text("⚠️ ID san görnüşinde bolmaly.")
            waiting_for.pop(user_id)
            return

        elif step == 'remove_user':
            try:
                rem_id = int(update.message.text)
                ALLOWED_USERS.discard(rem_id)
                await update.message.reply_text("❌ Ulanyjy aýryldy.")
            except:
                await update.message.reply_text("⚠️ ID san görnüşinde bolmaly.")
            waiting_for.pop(user_id)
            return

        elif step == 'announcement':
            announcement_text = update.message.text
            context.user_data['announcement_text'] = announcement_text

            buttons = [
                [InlineKeyboardButton("✅ Tassyklamak", callback_data='confirm_announcement')],
                [InlineKeyboardButton("❌ Goýbolsun", callback_data='cancel_announcement')]
            ]
            await update.message.reply_text(
                f"📢 Bildiriş:\n\n{announcement_text}\n\nTassykla?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    elif step == 'announcement':
        # Bildiriş girizildi — tassyklamak soralýar
        context.user_data['announcement_text'] = update.message.text
        waiting_for[user_id] = 'announcement_confirm'
        await update.message.reply_text(
            f"📢 Bildiriş mazmuny:\n\n{update.message.text}\n\nTassyklamak isleýärsiňizmi?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Tassyklamak", callback_data="confirm_announcement")],
                [InlineKeyboardButton("❌ Goýbolsun", callback_data="cancel_announcement")]
            ])
        )
        return

    elif step == 'announcement_confirm':
        # Bu ädim button_callback arkaly ýerine ýetirilýär — howpsuzlyk üçin saklanyp galýar
        return

    # Adaty ulanyjy üçin:
    if user_id != ADMIN_ID and user_id not in ALLOWED_USERS:
        return

    if user_id in waiting_for:
        step = waiting_for[user_id]
        sess = user_sessions[user_id]

        if step == 'photo' and update.message.photo:
            sess['photo'] = update.message.photo[-1].file_id
            waiting_for[user_id] = 'caption'
            await update.message.reply_text("📝 Surata caption giriziň:")

        elif step == 'text':
            sess['text'] = update.message.text
            waiting_for[user_id] = 'minute'
            await update.message.reply_text("🕒 Her näçe minutda ugradylsyn? (mysal: 10)")

        elif step == 'caption':
            sess['caption'] = update.message.text
            waiting_for[user_id] = 'minute'
            await update.message.reply_text("🕒 Her näçe minutda ugradylsyn? (mysal: 10)")

        elif step == 'minute':
            try:
                sess['minute'] = int(update.message.text)
                waiting_for[user_id] = 'day'
                await update.message.reply_text("📅 Näçe gün dowam etsin? (mysal: 2)")
            except:
                await update.message.reply_text("⚠️ Minuty san bilen giriziň!")

        elif step == 'day':
            try:
                sess['day'] = int(update.message.text)
                waiting_for[user_id] = 'channel'
                await update.message.reply_text("📢 Haýsy kanal? (@username görnüşinde)")
            except:
                await update.message.reply_text("⚠️ Günü san bilen giriziň!")

        elif step == 'channel':
            sess['channel'] = update.message.text.strip()
            waiting_for.pop(user_id)

            post = {
                'user_id': user_id,
                'type': sess['type'],
                'minute': sess['minute'],
                'day': sess['day'],
                'channel': sess['channel'],
                'next_time': time.time(),
                'sent_count': 0,
                'max_count': (sess['day'] * 24 * 60) // sess['minute']
            }
            if sess['type'] == 'surat':
                post['photo'], post['caption'] = sess['photo'], sess['caption']
            else:
                post['text'] = sess['text']
            scheduled_posts.append(post)
            await update.message.reply_text("✅ Post goşuldy, awtomat goýulýar.")

# ⏰ SCHEDULER
async def scheduler(app):
    while True:
        now = time.time()
        for post in scheduled_posts:
            # ⛔ 1. Paused ýa-da limiti dolan bolsa geç
            if post.get('paused') or post['sent_count'] >= post['max_count']:
                continue
            
            # ⛔ 2. Ulanyjy rugsatsyz bolsa, posty duruz
            if post['user_id'] not in ALLOWED_USERS and post['user_id'] != ADMIN_ID:
                post['paused'] = True
                continue

            # ✅ 3. Wagt gelipdir, post goýulýar
            if now >= post['next_time']:
                try:
                    # Öňki posty poz
                    if post['channel'] in previous_messages:
                        try:
                            await app.bot.delete_message(post['channel'], previous_messages[post['channel']])
                        except:
                            pass

                    # Täze post ugrat
                    if post['type'] == 'surat':
                        msg = await app.bot.send_photo(post['channel'], post['photo'], caption=post['caption'])
                    else:
                        msg = await app.bot.send_message(post['channel'], post['text'])

                    previous_messages[post['channel']] = msg.message_id
                    post['sent_count'] += 1
                    post['next_time'] = now + post['minute'] * 60
                except Exception as e:
                    print(f"Ugradyp bolmady: {e}")
        await asyncio.sleep(30)

# ✅ MAIN START
async def main():
    app = ApplicationBuilder().token("8021702862:AAHUPIGxetCj_wCAJ_4KauaAiEg4jJVvqoA").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    asyncio.create_task(scheduler(app))
    print("🤖 Bot işläp başlady...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
