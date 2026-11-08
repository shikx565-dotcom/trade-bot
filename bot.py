import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# 1. سيرفر الويب عشان Railway
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعداد بوت ديسكورد باستخدام commands.Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        # مزامنة الأوامر مع ديسكورد فوراً
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر (Slash Commands) بنجاح!")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")

# تعريف أمر الشارة
@bot.tree.command(name="badge", description="الحصول على تفاعل الشارة")
async def badge(interaction: discord.Interaction):
    await interaction.response.send_message("🎉 تم تفاعل البوت بنجاح! توجه الآن لموقع ديسكورد لاستلام الشارة.")

# تشغيل السيرفر والبوت
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
