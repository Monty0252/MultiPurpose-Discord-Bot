import discord
from discord.ext import commands
from discord.ui import Button, View 
from yt_dlp import YoutubeDL


# Define a View that contains your buttons
class MusicControls(View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # A timeout of None means the buttons will persist indefinitely
        self.bot = bot

    # Now you define each button and its callback
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.grey)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Here you would call your pause functionality
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('pause'))

    @discord.ui.button(label="Play", style=discord.ButtonStyle.green)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Here you would call your play functionality
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('play'))

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Here you would call your next track functionality
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('next'))

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Here you would call your stop functionality
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('stop'))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music.py is ready!")

    @commands.command()
    async def join(self, ctx):
        """Command to join the voice channel."""
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            try:
                await channel.connect()
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays audio from a URL (no playlist)."""
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command('join'))

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **self.FFMPEG_OPTIONS)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send(f'Now playing: {info["title"]}')
        controls = MusicControls(self.bot)
        await ctx.send("Controls:", view=controls)

    @commands.command()
    async def pause(self, ctx):
        """Pauses the audio."""
        ctx.voice_client.pause()
        await ctx.send("Paused the audio.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the audio."""
        ctx.voice_client.resume()
        await ctx.send("Resumed the audio.")

    @commands.command()
    async def stop(self, ctx):
        """Stops the audio and clears the queue."""
        ctx.voice_client.stop()
        await ctx.send("Stopped the audio.")

    @commands.command()
    async def gone(self, ctx):
        """Leaves the voice channel."""
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")

    # You can add more commands like 'next', which would require you to manage a queue system.

# Add setup function for this cog
async def setup(bot):
    
    await bot.add_cog(Music(bot))


