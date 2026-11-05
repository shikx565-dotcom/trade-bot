import discord
from discord.ext import commands, tasks
import datetime
import os

TRACKER_CHANNEL_ID = 1562105330370871407  # ضع أيدي القناة هنا
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
    return "🥇 **Reconnaissance** - 1122 Points\n🥈 **Ap** - 642 Points\n🥉 **Stall** - 750 Points"

def create_tracker_embed(ranking_data):
    embed = discord.Embed(
        title="📊 Trademode Ranking | Anoha Online",
        url="https://anoha-online.com/trademode",
        description="Live rankings fetched directly from the official website. Click the title above to open the site!",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="🏆 Top Players Ranking", value=ranking_data, inline=False)
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
