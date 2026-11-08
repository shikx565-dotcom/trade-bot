import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@bot.tree.command(name="badge", description="Get Active Developer Badge")
async def badge(interaction: discord.Interaction):
    await interaction.response.send_message("🎉 تفاعل البوت بنجاح!")

if __name__ == "__main__":
    TOKEN = os.environ.get('DISCORD_TOKEN')
    bot.run(TOKEN)
