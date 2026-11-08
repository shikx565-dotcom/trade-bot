import os
from flask import Flask
from threading import Thread
import discord
from discord import app_commands

# تشغيل سيرفر ويب خفيف (عشان Railway يستقبل طلبات الإضافة)
app = Flask('')

@app.route('/')
def home():
    print("تم تلقي طلب بنجاح!")
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# إعداد بوت ديسكورد وأوامر Slash Command
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()  # مزامنة أمر الـ Slash مع ديسكورد أوتوماتيك
    print(f'✅ تسجيل الدخول بنجاح باسم: {client.user}')
    print('✅ تم مزامنة أمر /badge بنجاح!')

@tree.command(name="badge", description="الحصول على تفاعل الشارة")
async def badge(interaction: discord.Interaction):
    await interaction.response.send_message("🎉 تم تفاعل البوت بنجاح! توجه الآن لموقع ديسكورد لاستلام الشارة.")

# تشغيل السيرفر والبوت معاً
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
