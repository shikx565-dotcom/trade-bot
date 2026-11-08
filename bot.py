import os
from flask import Flask
from threading import Thread
import discord
from discord import app_commands

# 1. إعداد سيرفر الويب
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and alive!"

def run():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعداد بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'✅ البوت يعمل الآن بنجاح متصل بـ: {client.user}')

@tree.command(name="badge", description="Active Developer Badge Command")
async def badge(interaction: discord.Interaction):
    await interaction.response.send_message("🎉 تم تفاعل البوت بنجاح! توجه الآن لموقع ديسكورد لاستلام الشارة.")

# 3. التشغيل
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في المتغيرات!")
    else:
        client.run(TOKEN)
