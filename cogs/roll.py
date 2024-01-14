import discord
import random
from discord.ext import commands

class RollCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roll.py is ready!")
    # RollDeez Command
    @commands.command(name="rollDeez")
    async def roll_deez(self, ctx):
        result = random.randint(1, 100)
        user = ctx.author.display_name
        await ctx.send(f':game_die: {user} rolled {result} nutz!')

    # RollAll Command
    @commands.command(name='rollAll')
    async def roll_all(self, ctx):
        try:
            # get online members
            online_members = [member for member in ctx.guild.members if member.status == discord.Status.online and not member.bot]
            result_messages = ""
            highest_roll = 0
            winner = None
            
            for member in online_members:
                roll_result = random.randint(1, 100)
                if roll_result > highest_roll:
                    highest_roll = roll_result
                    winner = member.display_name
                result_messages += f":game_die: {member.display_name} rolled a {roll_result}\n"
            
            if not result_messages:
                await ctx.send("No online members to roll for.")
            else:
                # Send the results message
                await ctx.send(result_messages)
                # Send the winner message with a space before it
                if winner:
                    await ctx.send(f"\n:crown: The winner is {winner} with a roll of {highest_roll}! :crown:")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(client):
    await client.add_cog(RollCommands(client))