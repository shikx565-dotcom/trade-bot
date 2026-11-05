import discord
from discord.ext import commands, tasks
import datetime
import os
import requests
from bs4 import BeautifulSoup  # مكتبة خفيفة جداً لتحليل الصفحة وسحب كل الجداول

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

def fetch_anoha_data():
    try:
        url = "https://anoha-online.com/trademode"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # هنا بنبحث عن الجداول أو العناصر اللي فيها الترتيب والأسماء في الموقع
            # (كمثال عام للبحث عن صفوف الجدول أو عناصر الترتيب)
            rows = soup.find_all('tr') # أو التاج الخاص بالأسماء في الموقع
            
            rankings = []
            medals = ["🥇", "🥈", "🥉"]
            
            count = 1
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    name = cols[0].text.strip()
                    score = cols[1].text.strip()
                    
                    if count == 1:
                        emoji = medals[0]
                    elif count == 2:
                        emoji = medals[1]
                    elif count == 3:
                        emoji = medals[2]
                    else:
                        emoji = f"{count}."
                        
                    rankings.append(f"{emoji} **{name}** - {score} Points")
                    count += 1
            
            if rankings:
                # ديسكورد بيقبل في الـ Embed الواحد لحد 1024 حرف في الـ Field، 
                # فلو القائمة كبيرة هنقسمها أو نعرضها مرتبة
                return "\n".join(rankings[:25]) # أول 25 لاعب كمرحلة أولى عشان ما نعديش حدود ديسكورد
                
        return "⚠️ Could not fetch live data automatically yet."
    except Exception as e:
        print(f"[ERROR] {e}")
        return "⚠️ Error fetching data from website."

def create_tracker_embed(ranking_data):
    embed = discord.Embed(
        title="📊 Trademode Ranking | Anoha Online",
        url="https://anoha-online.com/trademode",
        description="Full live rankings fetched automatically. Click the title above to open the site!",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    
    embed.add_field(name="🏆 All Players Ranking", value=ranking_data, inline=False)
    embed.set_footer(text="Auto-refreshed every 5 minutes • Stable Mode")
    return embed

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
        else:
            msg = await channel.send(embed=embed)
            MESSAGE_ID = msg.id
    except discord.NotFound:
        msg = await channel.send(embed=embed)
        MESSAGE_ID = msg.id
    except Exception as e:
        print(f"[ERROR] {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (Stable & Ready!)")

bot.run(os.getenv("BOT_TOKEN"))
