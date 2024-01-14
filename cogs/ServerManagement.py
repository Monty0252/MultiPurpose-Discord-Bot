import discord
from discord.ext import commands

class ServerManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kick a user from the server
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if ctx.author.guild_permissions.kick_members:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked for: {reason}")
        else:
            await ctx.send("You do not have permission to kick members.")

    # Ban a user from the server
    @commands.command(name="ban")
    async def ban_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if ctx.author.guild_permissions.ban_members:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned for: {reason}")
        else:
            await ctx.send("You do not have permission to ban members.")

    # Unban a user from the server
    @commands.command(name="unban")
    async def unban_member(self, ctx, *, member):
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

    # Clear a specified number of messages in a channel
    @commands.command(name="clear")
    async def clear_messages(self, ctx, amount: int):
        if ctx.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"{amount} messages have been cleared by {ctx.author.mention}.")
        else:
            await ctx.send("You do not have permission to manage messages.")

    # Change the nickname of a member
    @commands.command(name="nickname")
    async def change_nickname(self, ctx, member: discord.Member, *, nickname):
        if ctx.author.guild_permissions.manage_nicknames:
            await member.edit(nick=nickname)
            await ctx.send(f"The nickname of {member.mention} has been changed to {nickname}.")
        else:
            await ctx.send("You do not have permission to manage nicknames.")

    # Server Stats
    @commands.command(name="serverinfo")
    async def display_server_info(self, ctx):
        server = ctx.guild

        # Get server statistics
        member_count = len(server.members)
        text_channel_count = len(server.text_channels)
        voice_channel_count = len(server.voice_channels)
        server_owner = server.owner

        # Create an embed to display server statistics
        embed = discord.Embed(
            title="Server Statistics",
            color=0x1E90FF  # Change the color as needed
        )

        # Add server statistics to the embed
        embed.add_field(name="Total Members", value=member_count, inline=True)
        embed.add_field(name="Text Channels", value=text_channel_count, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channel_count, inline=True)
        embed.add_field(name="Server Owner", value=server_owner, inline=True)

        # Send the embed to the channel
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerManagementCog(bot))
