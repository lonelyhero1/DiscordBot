from discord.ext import commands
import requests
import os
import json
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_OAUTH_TOKEN = os.getenv("TWITCH_OAUTH_TOKEN")

HEADERS = {
    "Client-ID": TWITCH_CLIENT_ID,
    "Authorization": f"Bearer {TWITCH_OAUTH_TOKEN}"
}

# 讀取 twitch_channels.json
with open("twitch_channels.json", "r", encoding="utf-8") as f:
    CHANNELS = json.load(f)

class TwitchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 開台(self, ctx):
        twitch_ids = list(CHANNELS.values())
        query_string = "&user_login=".join(twitch_ids)
        url = f"https://api.twitch.tv/helix/streams?user_login={query_string}"
        
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            await ctx.send(f"❌ API 請求失敗，錯誤碼: {response.status_code}")
            return
        
        data = response.json()
        if "data" not in data or len(data["data"]) == 0:
            await ctx.send("🚫 目前沒有主播開台。")
            return

        live_list = []
        for stream_info in data["data"]:
            twitch_id = stream_info["user_login"]
            name = next((k for k, v in CHANNELS.items() if v == twitch_id), twitch_id)
            live_list.append(
                f"🎥 {name} ({twitch_id})\n"
                f"📌 標題: {stream_info['title']}\n"
                f"👥 觀看人數: {stream_info['viewer_count']}\n"
                f"🎮 遊戲: {stream_info['game_name']}\n"
                f"🔗 [直播網址](https://www.twitch.tv/{twitch_id})\n"
            )

        message = "**🔥 目前開台的主播:**\n\n" + "\n".join(live_list)
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(TwitchCommands(bot))
