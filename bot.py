import discord
from discord.ext import commands, tasks
import datetime
import os
from DrissionPage import ChromiumPage, ChromiumOptions

# ==========================================
# 1. الإعدادات والمعرفات
# ==========================================
TRACKER_CHANNEL_ID = 123456789012345678  # ضع أيدي القناة هنا
MESSAGE_ID = None

intents = discord.Intents.default()
intents.message_content = True

class AnohaTradeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        auto_update_tracker.start()
        await self.tree.sync()

bot = AnohaTradeBot()

# ==========================================
# 2. دالة جلب البيانات الحقيقية وسحب الجدول من الموقع
# ==========================================
def fetch_anoha_data():
    try:
        co = ChromiumOptions()
        co.headless(True)  # تشغيل في الخلفية على السحابة
        co.no_imgs(True)
        
        page = ChromiumPage(addr_or_opts=co)
        page.get("https://anoha-online.com/trademode")
        
        # الانتظار ومحاكاة النقرات المتعددة لتجاوز Cloudflare
        page.wait(3)
        page.actions.click(100, 100)
        page.wait(1)
        page.actions.click(200, 200)
        page.wait(1)
        page.actions.click(300, 150)
        page.wait(4)  # انتظار تحميل البيانات بالكامل بعد التخطي
        
        # سحب صفوف الجدول (Rows) الحقيقية من الموقع
        rows = page.eles('tag:tr')
        
        players_list = []
        for row in rows[1:6]:  # جلب أول 5 مراكز
            cols = row.eles('tag:td')
            if len(cols) >= 3:
                rank = cols[0].text.strip()
                name = cols[1].text.strip()
                points = cols[2].text.strip()
                players_list.append((rank, name, points))
                
        page.quit()
        
        if not players_list:
            return None
            
        # تنسيق الأسماء مع إيموجيات المراكز
        formatted_text = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        
        for i, item in enumerate(players_list):
            medal = medals[i] if i < len(medals) else f"#{item[0]}"
            formatted_text += f"{medal} **{item[1]}** - {item[2]} Points\n"
            
        return formatted_text

    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None

def create_tracker_embed(ranking_data):
    # إضافة رابط الموقع هنا لكي يصبح العنوان قابل للضغط ويفتح الموقع مباشرة
    embed = discord.Embed(
        title="📊 Trademode Ranking | Anoha Online",
        url="https://anoha-online.com/trademode",
        description="Live rankings fetched directly from the official website. Click the title above to open the site!",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    
    if ranking_data:
        embed.add_field(name="🏆 Top Players Ranking", value=ranking_data, inline=False)
    else:
        embed.add_field(name="⚠️ Status", value="Waiting for website data sync...", inline=False)
        
    embed.set_footer(text="Auto-refreshed every 5 minutes • Cloudflare Bypassed")
    return embed

# ==========================================
# 3. مهمة التحديث التلقائي كل 5 دقائق
# ==========================================
@tasks.loop(minutes=5)
async def auto_update_tracker():
    global MESSAGE_ID
    await bot.wait_until_ready()
    
    channel = bot.get_channel(TRACKER_CHANNEL_ID)
    if not channel:
        return

    ranking_text = fetch_anoha_data()
    embed = create_tracker_embed(ranking_text)

    try:
        if MESSAGE_ID:
            msg = await channel.fetch_message(MESSAGE_ID)
            await msg.edit(embed=embed)
            print("[SUCCESS] Message updated.")
        else:
            msg = await channel.send(embed=embed)
            MESSAGE_ID = msg.id
            print(f"[SUCCESS] Initial message sent: {MESSAGE_ID}")
    except discord.NotFound:
        msg = await channel.send(embed=embed)
        MESSAGE_ID = msg.id
    except Exception as e:
        print(f"[ERROR] {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (Clickable Embed Ready!)")

@bot.tree.command(name="ping", description="Test bot status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is online and click-to-open link is active!")

bot.run(os.getenv("BOT_TOKEN"))
