import discord
import os
import asyncio
from discord.ext import commands, tasks
from itertools import cycle
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    bot_token = config["DISCORD_BOT_TOKEN"]

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot_status = cycle(["Chilling", "Chilling More", "Chilling Expeditiously"])

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(bot_status)))


@bot.event
async def on_ready():
    print("Bot is connected to Discord Bitchesss")
    change_status.start()

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} is loaded!")


async def main():
    async with bot:
        await load()
        await bot.start(bot_token)

asyncio.run(main())

