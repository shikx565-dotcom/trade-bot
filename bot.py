import discord
from discord.ext import commands
import datetime
import os
import asyncio
from aiohttp import web

TRACKER_CHANNEL_ID = 1562105330370871407  # ضع أيدي القناة هنا
MESSAGE_ID = None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
latest_rankings = []

def create_tracker_embed(rankings_list):
    embed = discord.Embed(
        title="📊 Trademode Ranking | Anoha Online",
        url="https://anoha-online.com/trademode",
        description="Complete live rankings updated via Chrome Extension. Click above to view site!",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    formatted_list = []
    
    for idx, item in enumerate(rankings_list, 1):
        name = item.get("name", "Unknown")
        score = item.get("score", "0")
        
        if idx == 1:
            emoji = medals[0]
        elif idx == 2:
            emoji = medals[1]
        elif idx == 3:
            emoji = medals[2]
        else:
            emoji = f"`#{idx}`"
            
        formatted_list.append(f"{emoji} **{name}** — {score}")
    
    full_text = "\n".join(formatted_list) if formatted_list else "Waiting for sync..."
    
    # حماية حدود ديسكورد للرسائل الطويلة
    if len(full_text) > 1000:
        full_text = full_text[:1000] + "\n...(and more)"
        
    embed.add_field(name="🏆 All Players Ranking", value=full_text, inline=False)
    embed.set_footer(text="Auto-updated via Chrome Extension • Active Mode")
    return embed

async def update_discord_message():
    global MESSAGE_ID
    channel = bot.get_channel(TRACKER_CHANNEL_ID)
    if not channel:
        return

    embed = create_tracker_embed(latest_rankings)
    try:
        if MESSAGE_ID:
            msg = await channel.fetch_message(MESSAGE_ID)
            await msg.edit(embed=embed)
        else:
            msg = await channel.send(embed=embed)
            MESSAGE_ID = msg.id
    except Exception as e:
        print(f"[ERROR] {e}")

async def handle_update(request):
    global latest_rankings
    try:
        data = await request.json()
        latest_rankings = data.get("rankings", [])
        bot.loop.create_task(update_discord_message())
        return web.json_response({"status": "success", "count": len(latest_rankings)})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def start_webserver():
    app = web.Application()
    app.router.add_post('/update-rank', handle_update)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Webserver running on port {port}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    bot.loop.create_task(start_webserver())

bot.run(os.getenv("BOT_TOKEN"))
