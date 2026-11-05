import os
import discord
from discord import app_commands
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class AnohaTradeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.scheduler = AsyncIOScheduler(timezone="Africa/Cairo")  # توقيت مصر
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Successfully synced slash commands!")
        
        # جدول المواعيد التلقائية (الساعة 5، 11، و 12 منتصف الليل بتوقيت مصر)
        self.scheduler.add_job(self.auto_update_rankings, CronTrigger(hour="5,11,0", minute=0))
        self.scheduler.start()
        print("Auto-refresh scheduler started successfully for 5:00, 11:00, and 12:00!")

    async def auto_update_rankings(self):
        print("Triggering scheduled automatic ranking refresh from Anoha website...")
        # هنا سيتم وضع كود سحب البيانات من الموقع وإرسالها للقناة المحددة أوتوماتيكياً

bot = AnohaTradeBot()

@bot.tree.command(name="trademode", description="Displays the latest Trade rankings and rewards from Anoha website.")
async def trademode(interaction: discord.Interaction):
    await interaction.response.defer()

    # بيانات تجريبية (سيتم ربطها بسحب الموقع الفعلي)
    rankings = [
        {"rank": "🥇 1st Place", "player": "ShikX", "points": "15,420 pts", "reward": "500 Silks + Unique Title"},
        {"rank": "🥈 2nd Place", "player": "DragonSlayer", "points": "12,100 pts", "reward": "300 Silks"},
        {"rank": "🥉 3rd Place", "player": "DarkKnight", "points": "9,850 pts", "reward": "150 Silks"},
        {"rank": "🏅 4th Place", "player": "Shadow", "points": "7,400 pts", "reward": "50 Silks"},
    ]

    embed = discord.Embed(
        title="🏆 Anoha Online - Trade & Thief Rankings",
        description="Here is the latest live update of the Trade rankings and rewards:",
        color=discord.Color.gold()
    )

    for item in rankings:
        embed.add_field(
            name=f"{item['rank']} : {item['player']}",
            value=f"🔹 **Score:** {item['points']}\n🎁 **Reward:** {item['reward']}",
            inline=False
        )

    embed.set_footer(text="Anoha Guild Automated System • Scheduled Update", icon_url="https://i.imgur.com/icon.png")
    await interaction.followup.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in successfully as {bot.user} (Ready to serve the Guild Master!)')

# قراءة التوكن بأمان من إعدادات البيئة (Environment Variables) في الاستضافة
token = os.getenv('BOT_TOKEN')
bot.run(token)