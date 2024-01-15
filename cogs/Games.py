import discord
from discord.ext import commands, tasks
import requests
import datetime
import asyncio

class CheapSharkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_game_deals.start()

    def cog_unload(self):
        self.post_game_deals.cancel()

    @tasks.loop(seconds=10)
    async def post_game_deals(self):
        channel = discord.utils.get(self.bot.get_all_channels(), name='game-deals')
        if channel:
            game_deals = await self.fetch_game_deals()
            if game_deals:
                for deal in game_deals:
                    try:
                        embed = self.create_game_embed(deal)
                        await channel.send(embed=embed)
                        await asyncio.sleep(10)  # Wait for 10 seconds before posting next deal
                    except Exception as e:
                        print(f"Failed to post deal for '{deal['title']}': {str(e)}")

    @post_game_deals.before_loop
    async def before_post_game_deals(self):
        print('Waiting for bot to get ready...')
        await self.bot.wait_until_ready()

    async def fetch_game_deals(self):
        url = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15"
        headers = {}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None

    def create_game_embed(self, deal):
        title = deal["title"]
        sale_price = deal["salePrice"]
        normal_price = deal["normalPrice"]
        release_date_timestamp = deal.get("releaseDate", "N/A")
        steam_rating_percent = deal.get("steamRatingPercent", "N/A")
        steam_rating_text = deal.get("steamRatingText", "N/A")
        thumb = deal["thumb"]
        deal_id = deal["dealID"]

        if release_date_timestamp != "N/A":
            release_date = datetime.datetime.utcfromtimestamp(release_date_timestamp)
            formatted_release_date = release_date.strftime('%B %d, %Y')
        else:
            formatted_release_date = "N/A"

        embed = discord.Embed(
            title=title,
            description=f"**Price:** ~~${normal_price}~~ ${sale_price}\n\n**Release Date:** {formatted_release_date}\n\n**Steam Rating:** {steam_rating_text} - {steam_rating_percent}%",color=discord.Color.green())
        embed.set_image(url=thumb)
        embed.url = f"https://www.cheapshark.com/redirect?dealID={deal_id}"
        return embed

async def setup(bot):
    await bot.add_cog(CheapSharkCog(bot))
