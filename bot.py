import discord
from discord.ext import commands, tasks
import asyncio
import datetime

# ==========================================
# 1. إعداد المعرفات والبيانات
# ==========================================
# ضع معرف القناة (Channel ID) التي سيتم نشر وتحديث التتبع فيها هنا
TRACKER_CHANNEL_ID = 1562105330370871407  # استبدل هذا الرقم بـ Channel ID الحقيقي

# متغيّر لحفظ معرف الرسالة المثبتة لكي يتم تعديلها باستمرار
MESSAGE_ID = None

intents = discord.Intents.default()
intents.message_content = True

class AnohaTradeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # بدء مهمة التحديث التلقائي كل 5 دقائق
        auto_update_tracker.start()
        # مزامنة أوامر Slash مع الديسكورد
        await self.tree.sync()

bot = AnohaTradeBot()

# ==========================================
# 2. دالة جلب/تنسيق البيانات (شكل العرض Embed)
# ==========================================
def create_tracker_embed():
    embed = discord.Embed(
        title="📊 Thief & Trader Tracker | Anoha Online",
        description="التحديث المباشر لحالة الصفقات والرانك الحالي داخل اللعبة.",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    
    # قسم التجار (Traders)
    embed.add_field(
        name="🐪 أعلى التجار (Traders)",
        value="1. **Player1** - 15,000 Gold\n2. **Player2** - 12,300 Gold\n3. **Player3** - 9,800 Gold",
        inline=False
    )
    
    # قسم قطاع الطرق (Thieves)
    embed.add_field(
        name="⚔️ أعلى القطاع (Thieves)",
        value="1. **Shadow** - 22 Kills\n2. **HunterX** - 18 Kills\n3. **Rogue** - 14 Kills",
        inline=False
    )
    
    embed.set_footer(text="يتم التحديث تلقائياً كل 5 دقائق • Anoha Online System")
    return embed

# ==========================================
# 3. مهمة التحديث التلقائي كل 5 دقائق (Edit Message)
# ==========================================
@tasks.loop(minutes=5)
async def auto_update_tracker():
    global MESSAGE_ID
    await bot.wait_until_ready()
    
    channel = bot.get_channel(TRACKER_CHANNEL_ID)
    if not channel:
        print(f"لم يتم العثور على القناة المحددة ID: {TRACKER_CHANNEL_ID}")
        return

    embed = create_tracker_embed()

    try:
        # إذا كانت الرسالة مرسلة من قبل، يتم تعديلها فقط
        if MESSAGE_ID:
            msg = await channel.fetch_message(MESSAGE_ID)
            await msg.edit(embed=embed)
            print("[INFO] تم تعديل نفس الرسالة بنجاح.")
        else:
            # أول مرة: إرسال الرسالة وحفظ الـ ID الخاص بها
            msg = await channel.send(embed=embed)
            MESSAGE_ID = msg.id
            print(f"[INFO] تم إرسال الرسالة الأولى وحفظ معرفها: {MESSAGE_ID}")
    except discord.NotFound:
        # في حال تم حذف الرسالة يدوياً من القناة، يرسل واحدة جديدة ويحفظ ID الجديد
        msg = await channel.send(embed=embed)
        MESSAGE_ID = msg.id
        print("[WARNING] الرسالة السابقة حُذفت، تم إرسال رسالة جديدة.")
    except Exception as e:
        print(f"[ERROR] خطأ أثناء تحديث الرسالة: {e}")

# ==========================================
# 4. أحداث البوت وأمر الحصول على الشارة
# ==========================================
@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user} (Ready to serve the Guild Master!)")

# أمر Slash تفاعلي لتسهيل الحصول على Active Developer Badge
@bot.tree.command(name="ping", description="أمر تفاعلي لاختبار البوت وتفعيل شارة المطور")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓 البوت شغال بنجاح والتحديثات مستمرة كل 5 دقائق.")

# تشغيل البوت عبر توكن البيئة
import os
bot.run(os.getenv("BOT_TOKEN"))
