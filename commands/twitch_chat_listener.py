import os
import json
import asyncio
import websockets
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TWITCH_NICK = os.getenv("TWITCH_BOT_USERNAME")
TWITCH_TOKEN = f"oauth:{os.getenv('TWITCH_OAUTH_TOKEN')}"
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  
CONFIG_PATH = "twitch_config.json"

def load_twitch_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["twitch_channel"], set(config["target_users"])
    except Exception as e:
        print(f"⚠️ 無法讀取 {CONFIG_PATH}: {e}")
        return None, set()

class TwitchListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_channel, self.target_users = load_twitch_config()
        self.loop = asyncio.create_task(self.connect_to_twitch())

    async def connect_to_twitch(self):
        """建立 Twitch IRC WebSocket 連線"""
        uri = "wss://irc-ws.chat.twitch.tv:443"
        while True:
            try:
                async with websockets.connect(
                    uri, ping_interval=None, ping_timeout=None, close_timeout=None
                ) as ws:
                    await ws.send(f"PASS {TWITCH_TOKEN}")
                    await ws.send(f"NICK {TWITCH_NICK}")
                    await ws.send(f"JOIN #{self.twitch_channel}")

                    print(f"✅ 成功加入 Twitch 頻道: {self.twitch_channel}")

                    while True:
                        try:
                            msg = await ws.recv()
                            print(msg)

                            if "PRIVMSG" in msg:
                                parts = msg.split(":", 2)
                                if len(parts) < 3:
                                    continue

                                meta_info = parts[1].split(" ")
                                sender = meta_info[0].split("!")[0]  
                                message = parts[2].strip()  

                                if sender.lower() in self.target_users:
                                    await self.send_to_discord(sender, message)

                        except websockets.exceptions.ConnectionClosed:
                            print("🔄 WebSocket 連線中斷，正在重連...")
                            break

            except Exception as e:
                print(f"⚠️ Twitch 連線錯誤: {e.__class__.__name__}: {e}")
                await asyncio.sleep(10)  # 10秒後重試

    async def send_to_discord(self, user, message):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            msg = f"📢 **{user} 在 Twitch 說:**\n{user}: {message}"
            await channel.send(msg)
            print(f"📤 已轉發到 Discord: {msg}")

    @commands.command()
    async def reload_twitch_set(self, ctx):
        self.twitch_channel, self.target_users = load_twitch_config()
        await ctx.send("🔄 已重新載入 Twitch 監聽設定！")
        print("🔄 Twitch 設定已更新！")

async def setup(bot):
    await bot.add_cog(TwitchListener(bot))
