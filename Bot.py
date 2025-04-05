import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

# 讀取 .env 檔案
load_dotenv()

# 讀取環境變數
TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID")) 
# 啟用機器人
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(f"機器人已上線！當前時間：{current_time}")
        
    # 加載擴展模組
    for ext in ['commands.basic', 'commands.twitch_live', 'commands.twitch_chat_listener']:
        try:
            await bot.load_extension(ext)
            print(f"✅ 已載入模組: {ext}")
        except Exception as e:
            print(f"❌ 加載模組 {ext} 時發生錯誤: {e}")

# 啟動機器人
if __name__ == '__main__':
    bot.run(TOKEN)
