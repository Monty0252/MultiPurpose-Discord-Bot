import discord
from discord.ext import commands
import youtube_dl

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        # Youtube DL options
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music.py is ready!")

    @commands.command()
    async def join(self, ctx):
        """Join voice channel."""
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

async def setup(client):
    await client.add_cog(Music(client))


