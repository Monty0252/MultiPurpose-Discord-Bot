import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class ServerManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(lambda: [])
        self.SPAM_MESSAGE_THRESHOLD = 8
        self.SPAM_TIME_WINDOW = timedelta(seconds=30)
        self.MUTE_DURATION = 60  # Mute duration in seconds

    # Welcomes new user when they join the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            await guild.system_channel.send(f'Hello {member.mention}, welcome to {guild.name}!')


    # Kick a user from the server
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Command to kick member."""
        if ctx.author.guild_permissions.kick_members:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked for: {reason}")
        else:
            await ctx.send("You do not have permission to kick members.")

    # Ban a user from the server
    @commands.command(name="ban")
    async def ban_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Command to ban member."""
        if ctx.author.guild_permissions.ban_members:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned for: {reason}")
        else:
            await ctx.send("You do not have permission to ban members.")

    # Unban a user from the server
    @commands.command(name="unban")
    async def unban_member(self, ctx, *, member):
        """Command to unban member."""
        if ctx.author.guild_permissions.ban_members:
            banned_users = await ctx.guild.bans()
            for entry in banned_users:
                user = entry.user
                if user.name + "#" + user.discriminator == member:
                    await ctx.guild.unban(user)
                    await ctx.send(f"{user.mention} has been unbanned.")
                    return
            await ctx.send("User not found in the ban list.")
        else:
            await ctx.send("You do not have permission to unban members.")

    
    # Spam detection
    @commands.Cog.listener()
    async def spam_detection(self, message):
        if message.author.bot:
            return

        # Initialize message list if not already present
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []

        messages = self.user_messages[message.author.id]
        messages.append((message, datetime.now()))

        # Filter out messages outside the time window
        messages = [msg for msg in messages if msg[1] > datetime.now() - self.SPAM_TIME_WINDOW]
        self.user_messages[message.author.id] = messages

        if len(messages) >= self.SPAM_MESSAGE_THRESHOLD:
            await message.channel.send(f"{message.author.mention}, please stop spamming.")
            try:
                muted_role = discord.utils.get(message.guild.roles, name="Muted")
                if muted_role:
                    await message.author.add_roles(muted_role)
                    await message.channel.send(f"{message.author.mention} has been muted for spamming.")

                    # Schedule unmute after MUTE_DURATION
                    await asyncio.sleep(self.MUTE_DURATION)
                    await message.author.remove_roles(muted_role)
                    await message.channel.send(f"{message.author.mention} has been unmuted.")
                    # Remove user from the dictionary after unmuting
                    del self.user_messages[message.author.id]
                else:
                    await message.channel.send("No 'Muted' role found.")
            except discord.errors.Forbidden:
                await message.channel.send("I don't have permission to mute members.")

    # Clear a specified number of messages in a channel
    @commands.command(name="clear")
    async def clear_messages(self, ctx, amount: int = None):
        """Clear messages: !clear [number of messages]"""
        if amount is None:
            await ctx.send("Provide number of messages to delete")
            return
         
        if ctx.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"{amount} messages have been cleared by {ctx.author.mention}.")
        else:
            await ctx.send("You do not have permission to manage messages.")

    # Change the nickname of a member
    @commands.command(name="nickname")
    async def change_nickname(self, ctx, member: discord.Member, *, nickname=None):
        """change nickname: !nickname @member "newnickname" """
        # Check if the user has the required permissions
        if ctx.author.guild_permissions.manage_nicknames:
            # If the command includes 'reset' or no nickname, reset the member's nickname
            if nickname == "reset" or nickname is None:
                nickname = None  # This will reset the nickname
                action = "reset"
            else:
                action = "changed to " + nickname

            await member.edit(nick=nickname)
            await ctx.send(f"The nickname of {member.mention} has been {action}.")
        else:
            await ctx.send("You do not have permission to manage nicknames.")

    # Server Stats
    @commands.command(name="info")
    async def display_server_info(self, ctx):
        """Command to display server stats."""
        server = ctx.guild
        # Get server statistics
        member_count = len(server.members)
        text_channel_count = len(server.text_channels)
        voice_channel_count = len(server.voice_channels)
        server_owner = server.owner
        member_count = len(server.members)
        online_member_count = sum(1 for member in server.members if member.status != discord.Status.offline)
        server_creation_date = server.created_at.strftime("%Y-%m-%d")
        # server_region = server.region
        server_roles = "\n".join(role.name for role in server.roles)
        text_channels = "\n".join(text_channel.name for text_channel in server.text_channels)
        voice_channels = "\n".join(voice_channel.name for voice_channel in server.voice_channels)

        # Create an embed to display server statistics
        embed = discord.Embed(
            title="Server Statistics",
            color=0x1E90FF  # Change the color as needed
        )

        # Add server statistics to the embed
        # embed.set_image(url=server.icon_url)
        embed.add_field(name="Total Members", value=member_count, inline=True)
        embed.add_field(name="Online Members", value=online_member_count, inline=True)
        embed.add_field(name="Text Channels", value=text_channel_count, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channel_count, inline=True)
        embed.add_field(name="Server Owner", value=server_owner, inline=True)
        embed.add_field(name="Server Creation Date", value=server_creation_date, inline=True)
        embed.add_field(name="Server Roles", value=server_roles, inline=True)
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)

        # Send the embed to the channel
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()  # Ensure only the bot owner can use this command
    async def leave(self, ctx, guild_id: int = None):
        """Command for the bot to leave a server."""
        if guild_id is None:
            await ctx.send("Please provide a valid server ID.")
            return

        try:
            guild = self.bot.get_guild(guild_id)
            if guild:
                await guild.leave()
                await ctx.send(f"I have left {guild.name}.")
            else:
                await ctx.send("I am not in that server or invalid server ID.")
        except discord.Forbidden:
            await ctx.send("I don't have the permissions to leave this server.")
        except discord.HTTPException as e:
            await ctx.send(f"An HTTP error occurred: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")





async def setup(bot):
    await bot.add_cog(ServerManagementCog(bot))
