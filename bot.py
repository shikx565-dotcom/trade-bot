import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands

# 1. سيرفر الويب الخفيف لضمان عمل البوت على Railway
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات بوت ديسكورد
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ضع الـ Client ID الخاص ببوتك هنا بين العلامتين (أو اتركه فارغاً لتتم المزامنة التلقائية)
MY_GUILD_ID = discord.Object(1567734847672164392) 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        # مزامنة الأوامر مباشرة مع سيرفرك لضمان ظهورها فوراً
        bot.tree.copy_global_to(guild=MY_GUILD_ID)
        synced = await bot.tree.sync(guild=MY_GUILD_ID)
        print(f"✅ تم مزامنة {len(synced)} أمر (Slash Commands) بنجاح!")
    except Exception as e:
        print(f"خطأ في المزامنة: {e}")

# 3. تعريف أمر الشارة /badge
@bot.tree.command(name="badge", description="Active Developer Badge Command")
async def badge(interaction: discord.Interaction):
    await interaction.response.send_message("🎉 تم تفاعل البوت بنجاح! توجه الآن لموقع ديسكورد لاستلام الشارة.")

# تشغيل السيرفر والبوت معاً
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
