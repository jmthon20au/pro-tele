from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from datetime import datetime
import pytz
import random
import asyncio
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.types import PeerUser
from telethon.tl.custom.button import Button
import os# لاستخدام الأزرار إذا قررنا إضافتها لاحقًا، حاليًا ما راح نستخدمها

# بيانات الجلسة
api_id = 27482849
api_hash = 'deb6dc38b1af6b940b94f843caf151e5'
session_string = '1ApWapzMBu0nQAnuyqki8oxu4FOjG8bb2Adhd-cHhXQUQBsORliF8Nfw6NyawJnllNpkdrVoo5HUBtcaRk8P5hwNmIM6M6cdtMKtfnpuIYq8LJ70HPtaBv-V6KnstAXYcHOqDOQLIp_Gyz5MWwKXl3wkTpUgZwa3Z7LgTraB-Accyr4vJGLq2TYMy__yVNPmJBmNuS5UZyIm09wF8zAn7fYSVGTaM95dOaUYGVrMGfMDAa3jtQso2BazDbVrxMcgnDahaJ_u0JmyNtcBhhrTM_8UAL_mcfDLpZJZGYukcmqTIl3dBG8RcbRnte0dMnha-BMIU0YwSM3hK_Rrl4Qk_SX4F_zEsLPU='

client = TelegramClient(StringSession(session_string), api_id, api_hash)

target_group_id = -1002836920777

# فقط المالك يقدر يتحكم
owner_id = 6454550864  # ← غيّره إلى ID مالك الحقيقي
self_destruct_save_enabled = False
bold_text_enabled = False 
# الردود التلقائية
auto_reply_enabled = True
name_update_enabled = False
original_name = None
keywords = {
    "السلام": "وعليكم ا السلام ورحمة الله",
    "شلونك": "تمام وانت؟"
}
morning_replies = [
    "صباح الخير 🌞، علاوي غير متوفر الآن.",
    "أهلاً وسهلاً، سيتم الرد لاحقًا إن شاء الله ☕",
    "علي حالياً غير موجود، صباحكم ورد 🌼"
]
night_replies = [
    "مساء الخير 🌙، علي مشغول حاليًا.",
    "علي غير متوفر، شكرًا لتواصلك ✨",
    "حاليًا غير متاح، سيتم الرد لاحقًا إن شاء الله 🌌"
]

# تم تحويل هذه القائمة إلى set لتحسين الأداء ولتجنب التكرار
banned_words = {'aydgdgd', 'كلمة2', 'احتيال', 'شتيمة', 'ممنوع'}
ban_message = "🚫 تم حظرك لأنك قلت كلمة ممنوعة."

# قائمة الأشخاص المكتومين
muted_users = set()

# قائمة الأشخاص المستثنين من الرد التلقائي
excluded_users = set()

@client.on(events.NewMessage(pattern=r"\.مسح"))
async def delete_conversation(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    if not event.is_reply:
        await event.reply("❗ يجب الرد على رسالة من الشخص الذي تريد حذف المحادثة معه.")
        return

    try:
        replied_msg = await event.get_reply_message()
        user = await replied_msg.get_sender()
        user_entity = await client.get_entity(user.id)

        await client(DeleteHistoryRequest(
            peer=PeerUser(user_entity.id),
            max_id=0,
            revoke=True
        ))

        await event.reply("✅ تم حذف المحادثة بالكامل من الطرفين.")
        print(f"🗑️ تم حذف المحادثة بالكامل مع: {user.id}")

    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء محاولة الحذف: {e}\nقد يكون الشخص الآخر قد حظر حسابك، أو هناك مشكلة في الصلاحيات.")


@client.on(events.NewMessage(pattern=r"\.ايدي"))
async def get_user_info(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    if not event.is_reply:
        await event.reply("❗ يجب الرد على رسالة الشخص اللي تريد معلوماته.")
        return

    try:
        replied = await event.get_reply_message()
        user = await replied.get_sender()

        full = await client(functions.users.GetFullUserRequest(user.id))

        try:
            photo = await client.download_profile_photo(user.id, file=f"profile_{user.id}.jpg")
        except:
            photo = None

        info_text = (
            f"👤 الاسم: {user.first_name or 'لا يوجد'}\n"
            f"🆔 ID: `{user.id}`\n"
            f"🔗 Username: @{user.username if user.username else 'لا يوجد'}\n"
            f"🤖 بوت: {'نعم' if user.bot else 'لا'}\n"
            f"📝 Bio: {full.full_user.about or 'لا يوجد'}\n"
            f"🌐 رابط الحساب: tg://user?id={user.id}"
        )

        if photo:
            await event.reply(info_text, file=photo)
        else:
            await event.reply(info_text)

    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء جلب المعلومات: {e}")

@client.on(events.NewMessage(pattern=r"\.كتم"))
async def mute_user(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    if not event.is_reply:
        await event.reply("❗ يجب الرد على رسالة الشخص الذي تريد كتمه.")
        return

    replied = await event.get_reply_message()
    user = await replied.get_sender()
    user_id = user.id

    muted_users.add(user_id)
    await event.reply(f"🔇 تم كتم هذا المستخدم. سيتم حذف رسائله تلقائيًا.")

@client.on(events.NewMessage(pattern=r"\.الغاء"))
async def unmute_user(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    if not event.is_reply:
        await event.reply("❗ يجب الرد على رسالة الشخص الذي تريد فك كتمه.")
        return

    replied = await event.get_reply_message()
    user = await replied.get_sender()
    user_id = user.id

    if user_id in muted_users:
        muted_users.remove(user_id)
        await event.reply(f"🔊 تم فك الكتم عن هذا المستخدم.")
    else:
        await event.reply("ℹ️ هذا المستخدم غير مكتوم.")

@client.on(events.NewMessage)
async def delete_muted_messages(event):
    if event.is_private and not event.out:
        if event.sender_id in muted_users:
            try:
                await event.delete()
                await client.send_message(event.sender_id, "❌ أنتَ مكتوم، لتضل تدز 🌚")
                print(f"🗑️ حذف + رد على مكتوم: {event.sender_id}")
            except Exception as e:
                print(f"❌ خطأ أثناء حذف أو الرد على مكتوم: {e}")

# أوامر ميزة الاستثناء الجديدة
@client.on(events.NewMessage(pattern=r"\.استثناء (اضافة|حذف)(?: (.+))?"))
async def manage_exclusion(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return

    parts = event.pattern_match.groups()
    action = parts[0] # "اضافة" أو "حذف"
    identifier = parts[1] # الـ ID أو اليوزرنيم إذا كان موجود

    user_to_exclude = None
    user_id = None

    try:
        if event.is_reply:
            replied_msg = await event.get_reply_message()
            user_to_exclude = await replied_msg.get_sender()
            user_id = user_to_exclude.id
        elif identifier:
            try: # محاولة اعتبارها ID
                user_id = int(identifier)
                user_to_exclude = await client.get_entity(user_id)
            except ValueError: # إذا لم تكن ID، فاعتبرها يوزرنيم
                if identifier.startswith('@'):
                    identifier = identifier[1:]
                user_to_exclude = await client.get_entity(identifier)
                user_id = user_to_exclude.id
        else:
            await event.reply("❗ يجب الرد على رسالة أو تزويدي بـ ID أو يوزرنيم.")
            return

        if user_id:
            if action == "اضافة":
                if user_id not in excluded_users:
                    excluded_users.add(user_id)
                    await event.reply(f"✅ تم إضافة {user_to_exclude.first_name or user_id} إلى قائمة الاستثناء. لن يتلقى ردود تلقائية.")
                else:
                    await event.reply(f"ℹ️ {user_to_exclude.first_name or user_id} موجود مسبقًا في قائمة الاستثناء.")
            elif action == "حذف":
                if user_id in excluded_users:
                    excluded_users.remove(user_id)
                    await event.reply(f"✅ تم حذف {user_to_exclude.first_name or user_id} من قائمة الاستثناء. سيتلقى ردود تلقائية الآن.")
                else:
                    await event.reply(f"ℹ️ {user_to_exclude.first_name or user_id} ليس في قائمة الاستثناء.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ: تأكد من صحة الـ ID أو اليوزرنيم. الخطأ: {e}")

@client.on(events.NewMessage(pattern=r"\.قائمة الاستثناء"))
async def list_excluded_users(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    if not excluded_users:
        await event.reply("ℹ️ قائمة المستثنين فارغة.")
        return

    list_text = "📋 **قائمة المستثنين من الرد التلقائي:**\n"
    for user_id in excluded_users:
        try:
            user = await client.get_entity(user_id)
            list_text += f"- {user.first_name or 'غير معروف'} (`{user_id}`)\n"
        except Exception:
            list_text += f"- مستخدم غير معروف (`{user_id}`)\n"
    await event.reply(list_text)

# أوامر التحكم بالكلمات الممنوعة
@client.on(events.NewMessage(pattern=r"\.اضف ممنوع (.+)"))
async def add_banned_word(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    word = event.pattern_match.group(1).strip().lower()
    if word not in banned_words:
        banned_words.add(word)
        await event.reply(f"✅ تم إضافة الكلمة `«{word}»` إلى قائمة الممنوعات.")
    else:
        await event.reply(f"ℹ️ الكلمة `«{word}»` موجودة مسبقًا في قائمة الممنوعات.")

@client.on(events.NewMessage(pattern=r"\.حذف ممنوع (.+)"))
async def remove_banned_word(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    word = event.pattern_match.group(1).strip().lower()
    if word in banned_words:
        banned_words.remove(word)
        await event.reply(f"✅ تم حذف الكلمة `«{word}»` من قائمة الممنوعات.")
    else:
        await event.reply(f"ℹ️ الكلمة `«{word}»` غير موجودة في قائمة الممنوعات.")

@client.on(events.NewMessage(pattern=r"\.قائمة الممنوع"))
async def list_banned_words(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    if not banned_words:
        await event.reply("ℹ️ قائمة الكلمات الممنوعة فارغة.")
    else:
        words_list = "\n".join(f"- `{word}`" for word in sorted(list(banned_words)))
        await event.reply(f"🚫 **قائمة الكلمات الممنوعة:**\n{words_list}")

@client.on(events.NewMessage(pattern=r"\.السورس"))
async def show_source_info(event):
    if event.sender_id != owner_id:
        await event.reply("⚠️ لا تملك صلاحية استخدام هذا الأمر.")
        return

    # رسالة التشغيل نفسها
    startup_message_text = (
        "✅ تم تشغيل السورس بنجاح\n\n"
        "🛠️ **الأوامر المتاحة:**\n"
        "`/on` - تفعيل الرد التلقائي\n"
        "`/off` - إيقاف الرد التلقائي\n"
        "`/nameon` - تفعيل الساعة في الاسم\n"
        "`/nameoff` - إرجاع الاسم السابق\n"
        "`/id` - لمعرفة ايديك\n"
        "`.ايدي` - جلب معلومات عن شخص عبر الرد\n"
        "`.كتم` - كتم شخص (بالرد)\n"
        "`.الغاء` - فك الكتم (بالرد)\n"
        "`.خط` - تفعيل الخط الغامق لرسائلك الصادرة\n"
        "`.الغاءخط` - إيقاف الخط الغامق\n"
        "`.مسح` - حذف المحادثة بالكامل (بالرد)\n"
        "\n"
        "🆕 **أوامر الاستثناء:**\n"
        "`.استثناء اضافة` `[ID/@username]` - إضافة شخص لقائمة الاستثناء (يمكنك الرد على رسالته بدلاً من ID/Username)\n"
        "`.استثناء حذف` `[ID/@username]` - حذف شخص من قائمة الاستثناء (يمكنك الرد على رسالته بدلاً من ID/Username)\n"
        "`.قائمة الاستثناء` - عرض قائمة الأشخاص المستثنين\n"
        "\n"
        "🚨 **أوامر الكلمات الممنوعة:**\n"
        "`.اضف ممنوع` `[كلمة]` - إضافة كلمة لقائمة الممنوعات\n"
        "`.حذف ممنوع` `[كلمة]` - حذف كلمة من قائمة الممنوعات\n"
        "`.قائمة الممنوع` - عرض قائمة الكلمات الممنوعة\n"
        "\n"
        "💡 **أوامر أخرى:**\n"
        "`.السورس` - لعرض هذه الرسالة مرة أخرى"
    )
    
    await event.reply(startup_message_text)

@client.on(events.NewMessage)
async def all_messages_handler(event):
    # هنا تضيف السطر
    global auto_reply_enabled, name_update_enabled, original_name, bold_text_enabled, self_destruct_save_enabled

    sender = await event.get_sender()
    sender_id = event.sender_id
    # ... بقية الكود يضل مثل ما هو

    sender_name = sender.first_name or "غير معروف"
    sender_username = f"@{sender.username}" if sender.username else "لا يوجد"
    message_text = event.raw_text.strip()

    # فلترة الكلمات الممنوعة
    for word in banned_words:
        if word in message_text.lower():
            try:
                await event.respond(ban_message)
            except:
                pass # إذا فشل الرد، لا تتوقف
            try:
                await client(functions.contacts.BlockRequest(event.sender_id))
                print(f"🚫 تم حظر {sender_id} بسبب الكلمة: {word}")
            except Exception as e:
                print(f"❌ فشل الحظر: {e}")
            return # توقف هنا بعد الحظر والرد

    if not event.out and event.is_private:
        if self_destruct_save_enabled and event.media:
            if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
                try:
                    file_path = await event.download_media()
                    if file_path:
                        await client.send_message(
                            'me', 
                            f"📥 **تم حفظ وسائط ذاتية التدمير من:**\n"
                            f"👤 الاسم: {sender_name}\n"
                            f"🆔 ID: `{sender_id}`\n"
                            f"🔗 Username: {sender_username}\n", 
                            file=file_path
                        )
                        os.remove(file_path) # حذف الملف بعد إرساله للرسائل المحفوظة
                        print(f"✅ تم حفظ وحذف وسائط ذاتية التدمير من: {sender_id}")
                        # لا تقوم بتحويلها للكروب المستهدف لأنها تم حفظها بالفعل
                        return 
                except Exception as e:
                    print(f"❌ خطأ في حفظ الوسائط ذاتية التدمير: {e}")
                     # فقط الرسائل الخاصة اللي أنتَ مو راسلها
        try:
            sender_info_caption = (
                f"📤 **تم استلام رسالة من مستخدم**\n"
                f"👤 الاسم: {sender_name}\n"
                f"🆔 ID: `{sender_id}`\n"
                f"🔗 Username: {sender_username}\n"
            )

            if event.media:
                await client.send_file(
                    target_group_id,
                    file=event.media,
                    caption=sender_info_caption + (f"\n💬 **التعليق:** {message_text}" if message_text else "")
                )
                print(f"📎 تم تحويل الوسائط من: {sender_id}")
            elif message_text:
                await client.send_message(
                    target_group_id,
                    sender_info_caption + f"\n\n**الرسالة:**\n{message_text}"
                )
                print(f"💬 تم تحويل الرسالة النصية من: {sender_id}")

        except Exception as e:
            print(f"❌ خطأ في تحويل الرسالة/الوسائط: {e}")

    # أوامر التحكم (مسموح بها فقط لصاحب الحساب)
    if sender_id == owner_id:
        if message_text.lower() == "/id":
            me = await client.get_me()
            await event.respond(f"🆔 ايدي حسابك هو: `{me.id}`")
            print(f"✅ تم طلب ID المالك من قبل: {sender_id}")
            return
        elif message_text.lower() == '/off':
            auto_reply_enabled = False
            await event.respond("🚫 تم إيقاف الرد التلقائي.")
            print("✅ تم إيقاف الرد التلقائي من:", sender_id)
            return

        elif message_text.lower() == '/on':
            auto_reply_enabled = True
            await event.respond("✅ تم تشغيل الرد التلقائي.")
            print("✅ تم تشغيل الرد التلقائي من:", sender_id)
            return

        elif message_text.lower() == '/nameon':
            if not name_update_enabled:
                name_update_enabled = True
                me = await client.get_me()
                original_name = me.first_name
                await event.respond("🕒 تم تفعيل الاسم الوقتي (الساعة الرقمية).")
            else:
                await event.respond("ℹ️ الاسم الوقتي مفعل مسبقًا.")
            return

        elif message_text.lower() == '/nameoff':
            if name_update_enabled:
                name_update_enabled = False
                await client(UpdateProfileRequest(first_name=original_name, last_name=""))
                await event.respond("✅ تم إيقاف الاسم الوقتي وإعادة الاسم السابق.")
                print("✅ تم استرجاع الاسم السابق:", original_name)
            else:
                await event.respond("ℹ️ الاسم الوقتي غير مفعل.")
            return
        elif message_text.lower() == '.خط':
            bold_text_enabled = True
            await event.respond("✅ تم تفعيل وضع الخط الغامق. أي رسالة ترسلها الآن ستكون بخط غامق.")
            return
        elif message_text.lower() == '.الغاءخط' or message_text.lower() == '.الغاء الخط':
            bold_text_enabled = False
            await event.respond("🚫 تم إيقاف وضع الخط الغامق. الرسائل ستعود لطبيعتها.")
            return
        elif message_text.lower() == '.ذاتيه':
            self_destruct_save_enabled = True
            await event.respond("✅ تم تفعيل حفظ الوسائط ذاتية التدمير إلى الرسائل المحفوظة.")
            print("✅ تم تفعيل حفظ الوسائط ذاتية التدمير من:", sender_id)
            return
        elif message_text.lower() == '.تعطيل الذاتيه':
            self_destruct_save_enabled = False
            await event.respond("🚫 تم إيقاف حفظ الوسائط ذاتية التدمير.")
            print("🚫 تم إيقاف حفظ الوسائط ذاتية التدمير من:", sender_id)
            return            

    else: # إذا لم يكن المرسل هو المالك
        # هذه الأوامر يفضل حمايتها في بداية كل دالة مخصصة لها، مثل ما سوينا بالفعل
        # حتى لا يتداخل مع الأوامر الأخرى أو تظهر رسائل خطأ غير ضرورية هنا
        pass 
            
    # معالجة رسائلك الصادرة لتطبيق الخط الغامق
    if event.out and bold_text_enabled:
        if not message_text.lower().startswith('.') and not message_text.lower().startswith('/'):
            try:
                await event.edit(f"**{message_text}**")
                print(f"✅ تم تعديل رسالة بخط غامق في: {event.chat_id}")
                return
            except Exception as e:
                print(f"❌ خطأ أثناء تعديل الرسالة إلى خط غامق: {e}")

    # الرد التلقائي للخاص فقط (باستثناء المكتومين والمستثنين)
    if auto_reply_enabled and event.is_private and not event.out and event.sender_id not in muted_users and event.sender_id not in excluded_users:
        try:
            async with event.client.action(event.chat_id, 'typing'):
                await asyncio.sleep(1.5)

            current_hour = datetime.now().hour
            if 5 <= current_hour < 17:
                reply = random.choice(morning_replies)
            else:
                reply = random.choice(night_replies)

            await asyncio.sleep(1)
            await event.respond(reply)

            with open("log.txt", "a", encoding="utf-8") as log:
                log.write(f"[{datetime.now()}] From {sender_id}: {event.raw_text}\n")

            print(f"✅ تم الرد على {sender_id}")

        except Exception as e:
            print(f"❌ خطأ أثناء الرد: {str(e)}")

# تحديث الاسم الوقتي تلقائيًا
async def update_name_periodically():
    global name_update_enabled
    while True:
        if name_update_enabled:
            try:
                baghdad_time = datetime.now(pytz.timezone('Asia/Baghdad'))
                formatted_time = baghdad_time.strftime("%I:%M %p")
                formatted_time = formatted_time.replace("AM", "ص").replace("PM", "م")
                new_name = f"🕒 {formatted_time}"
                await client(UpdateProfileRequest(first_name=new_name, last_name=""))
                print(f"✅ تم تحديث الاسم إلى: {new_name}")
            except Exception as e:
                print(f"❌ فشل تحديث الاسم: {e}")
        await asyncio.sleep(60)

print("💡 البوت شغال كحساب شخصي...")
client.loop.create_task(update_name_periodically())
client.start()

# ⬇️ إضافة مهمة رسالة التشغيل بالصورة
async def send_startup_message():
    try:
        await client.send_file(
            'me',  # ← الرسائل المحفوظة
            file='A.jpg',  # ← تأكد أن الصورة موجودة
            caption=(
                "✅ تم تشغيل السورس بنجاح\n\n"
                "🛠️ **الأوامر المتاحة:**\n"
                "`/on` - تفعيل الرد التلقائي\n"
                "`/off` - إيقاف الرد التلقائي\n"
                "`/nameon` - تفعيل الساعة في الاسم\n"
                "`/nameoff` - إرجاع الاسم السابق\n"
                "`/id` - لمعرفة ايديك\n"
                "`.ايدي` - جلب معلومات عن شخص عبر الرد\n"
                "`.كتم` - كتم شخص (بالرد)\n"
                "`.الغاء` - فك الكتم (بالرد)\n"
                "`.خط` - تفعيل الخط الغامق لرسائلك الصادرة\n"
                "`.الغاءخط` - إيقاف الخط الغامق\n"
                "`.مسح` - حذف المحادثة بالكامل (بالرد)\n"
                "لتفعيل الذاتية 🤖ارسل `.ذاتيه` \n"
                "لتعطيل الذاتية 🔘 ارسل `تعطيل الذاتيه` \n"
                
                "\n"
                "🆕 **أوامر الاستثناء:**\n"
                "`.استثناء اضافة` `[ID/@username]` - إضافة شخص لقائمة الاستثناء (يمكنك الرد على رسالته بدلاً من ID/Username)\n"
                "`.استثناء حذف` `[ID/@username]` - حذف شخص من قائمة الاستثناء (يمكنك الرد على رسالته بدلاً من ID/Username)\n"
                "`.قائمة الاستثناء` - عرض قائمة الأشخاص المستثنين\n"
                "\n"
                "🚨 **أوامر الكلمات الممنوعة:**\n"
                "`.اضف ممنوع` `[كلمة]` - إضافة كلمة لقائمة الممنوعات\n"
                "`.حذف ممنوع` `[كلمة]` - حذف كلمة من قائمة الممنوعات\n"
                "`.قائمة الممنوع` - عرض قائمة الكلمات الممنوعة\n"
                "\n"
                "💡 **أوامر أخرى:**\n"
                "`.السورس` - لعرض هذه الرسالة مرة أخرى"
            )
        )
        print("📩 تم إرسال رسالة التشغيل إلى الرسائل المحفوظة.")
    except Exception as e:
        print(f"❌ فشل إرسال رسالة التشغيل: {e}")

client.loop.create_task(send_startup_message())

client.run_until_disconnected()
