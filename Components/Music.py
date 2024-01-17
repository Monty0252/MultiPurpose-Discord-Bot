from ast import alias
import discord
from discord.ext import commands
from discord.ui import Button, View
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio

YTDL_Format_Options = {'format': 'bestaudio/best', 'default_search': 'auto', 'quiet': 'True', 'no_warnings': 'True',
'ignoreerrors': 'False', 'source_address': '0.0.0.0', 'nocheckcertificate': 'True', "noplaylist": 'True'}


class MusicControls(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev_button(self, button: Button, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction.message)
        await self.bot.get_cog('music_cog').prev(ctx)

    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.success, custom_id="play_pause")
    async def play_pause_button(self, button: Button, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction.message)
        await self.bot.get_cog('music_cog').toggle_play_pause(ctx)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.danger, custom_id="next")
    async def next_button(self, button: Button, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction.message)
        await self.bot.get_cog('music_cog').next(ctx)


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.played_music_queue = []
        self.ytdl_format_options = YTDL_Format_Options
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


        self.vc = None
        self.ytdl = YoutubeDL(self.ytdl_format_options)

     #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return{'source':item, 'title':title}
        search = VideosSearch(item, limit=1)
        return{'source':search.result()["result"][0]["link"], 'title':search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Get the first URL
            m_url = self.music_queue[0][0]['source']
            current_song = self.music_queue.pop(0)

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']

            def after_playing(err):
                if not err:
                    self.played_music_queue.append(current_song)
                asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)

            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=after_playing)
        else:
            self.is_playing = False


        # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            current_song = self.music_queue.pop(0)

            # Try to connect to voice channel if not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await current_song[1].connect()

                # In case we fail to connect
                if self.vc is None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(current_song[1])

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']

            def after_playing(err):
                self.played_music_queue.append(current_song)
                asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)

            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=after_playing)
        else:
            self.is_playing = False

    
    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue)+2} -'{song['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")  
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_next(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")
    @commands.command(name="pq", help="Displays the current songs in queue")
    async def pq(self, ctx):
        retval = ""
        for i in range(0, len(self.played_music_queue)):
            retval += f"#{i+1} -" + self.played_music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clearmusic", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clearmusic(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
    
    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")
    
    @commands.command(name="prev",aliases=["pre"], help="Plays the previous song in the queue")
    async def prev(self, ctx):
        if len(self.played_music_queue) > 0:
            last_song = self.played_music_queue.pop()
            self.music_queue.insert(0, last_song)
            await ctx.send(f"Playing previously played song: '{last_song[0]['title']}'")
            if self.is_playing:
                self.vc.stop()
            await self.play_music(ctx)
        else:
            await ctx.send("```No previously played songs```")
    
    @commands.command(name="controls")
    async def controls(self, ctx):
        view = MusicControls(self.bot)
        await ctx.send("Music Controls:", view=view)
    
    async def toggle_play_pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send("Music paused.")
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.send("Music resumed.")
        else:
            await ctx.send("Nothting is currently playing.")

        
    async def next(self, ctx):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            await ctx.send("Skipping to the next song.")
        else:
            await ctx.send("No song is currently playing.")
    
    async def prev(self, ctx):
        if len(self.played_music_queue) > 0:
            last_song = self.played_music_queue.pop()
            self.music_queue.insert(0, last_song)
            if self.vc and self.vc.is_playing():
                self.vc.stop()  # This should trigger play_next
            else:
                await self.play_music(ctx)  # Call play_music if nothing is currently playing
            await ctx.send(f"Playing previously played song: '{last_song[0]['title']}'")
        else:
            await ctx.send("No previously played songs in the queue.")

async def setup(client):
    await client.add_cog(music_cog(client))