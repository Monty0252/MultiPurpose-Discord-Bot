import discord
import random
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py is ready!")

    # Ping Command
    @commands.command()
    async def ping(self, ctx):
        bot_latency = round(self.client.latency * 1000)
        await ctx.send(f"Pong! {bot_latency} ms.")

    # Magic Eightball Command
    @commands.command(name='8ball')
    async def magic_eightball(self, ctx, *, question):
        with open("TextFiles\eightball_responses.txt", "r") as file:
            responses = file.readlines()

        response = random.choice(responses).strip()
        await ctx.send(f"Question: {question}\nAnswer: {response}")
    
async def setup(client):
    await client.add_cog(Ping(client))
