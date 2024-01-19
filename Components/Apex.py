import discord
from discord.ext import commands
import subprocess
import json
from datetime import datetime

# Apex API Key
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    Apex_API_Key = config["APEX_API_KEY"]

class Apex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='apexstats')
    async def apex_stats(self, ctx, player_name, platform):
        auth_key = Apex_API_Key 
        base_url = "https://api.mozambiquehe.re/bridge"

        # Construct the curl command
        curl_command = f'curl "{base_url}?auth={auth_key}&player={player_name}&platform={platform}"'

        # Execute the curl command
        try:
            result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # Extract player information
            player_name = data["global"]["name"]
            player_platform = data["global"]["platform"]
            player_level = data["global"]["level"]
            selected_legend = data["legends"]["selected"]["LegendName"]
            selected_legend_icon = data["legends"]["selected"]["ImgAssets"]["icon"]

            # Extract global statistics
            total_kills = data["total"]["kills"]["value"]
            total_wins = data["total"]["wins_season_9"]["value"]

            # Create an embed to display the information
            embed = discord.Embed(title="Apex Legends Player Stats", color=0x00ff00)
            embed.add_field(name="Player Name", value=player_name, inline=False)
            embed.add_field(name="Player Platform", value=player_platform, inline=False)
            embed.add_field(name="Player Level", value=player_level, inline=False)
            embed.add_field(name="Selected Legend", value=selected_legend, inline=False)
            embed.add_field(name="Total Kills", value=total_kills, inline=False)
            embed.add_field(name="Total Wins", value=total_wins, inline=False)
            
            # Add the selected legend's icon
            embed.set_image(url=selected_legend_icon)

            await ctx.send(embed=embed)

        except subprocess.CalledProcessError as e:
            await ctx.send(f"Error executing curl command: {e}")
        except json.JSONDecodeError as e:
            await ctx.send(f"Error parsing JSON data: {e}")

    @commands.command(name="ApexStore")
    async def get_store_data(self, ctx):
        auth_key = Apex_API_Key
        base_url = "https://api.mozambiquehe.re/store"

        curl_command = f'curl "{base_url}?auth={auth_key}"'

        try:
            result = subprocess.run(curl_command,
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=10)  # Adding a timeout to prevent hanging

            if result.returncode == 0:
                data = json.loads(result.stdout)

                for entry in data:
                    title = entry["title"]
                    pricing_quantity = entry["pricing"][0]["quantity"]
                    pricing_ref = entry["pricing"][0]["ref"]
                    expire_timestamp = entry["expireTimestamp"]
                    expire_timestamp = datetime.utcfromtimestamp(expire_timestamp).strftime("%b %d, %Y")
                    asset_url = entry["asset"]

                    # Create a Discord embed for each entry
                    embed = discord.Embed(
                        title=f" {title}",
                        description=f"**Pricing:**\n {pricing_quantity} {pricing_ref}\n\n**Expiration Date:**\n {expire_timestamp}",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url=asset_url)

                    # Send the embed
                    await ctx.send(embed=embed)
            else:
                await ctx.send("Error in executing curl command:" + result.stderr)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(client):
    await client.add_cog(Apex(client))
