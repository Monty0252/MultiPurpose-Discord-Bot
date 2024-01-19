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

    @commands.command(name='apex-stats', help= "Gets stats of specified player in Apex Legends")
    async def apex_stats(self, ctx, player_name=None, platform=None):

        if player_name is None or platform is None:
            return await ctx.send("Please provide both a player name and a platform when using this command.\nUsage: !apex-stats <player_name> <platform>")
     
        base_url = "https://api.mozambiquehe.re/bridge"

        # Construct the curl command
        curl_command = f'curl "{base_url}?auth={Apex_API_Key}&player={player_name}&platform={platform}"'

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

    @commands.command(name="apex-store", help="Displays the current items in the Apex shop")
    async def get_store_data(self, ctx):
        
        base_url = "https://api.mozambiquehe.re/store"

        curl_command = f'curl "{base_url}?auth={Apex_API_Key}"'

        try:
            result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, check=True)

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


    @commands.command(name="apex-map", help="Displays the map rotation for Apex Legends battle royal")
    async def map_rotation(self, ctx):
        
        base_url = "https://api.mozambiquehe.re/maprotation"

        curl_command = f'curl "{base_url}?auth={Apex_API_Key}"'

        try:
            result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, check=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)

                # Create and send embed for current map
                current_data = data["current"]
                
                current_start_time = current_data["start"]
                current_start_time= datetime.utcfromtimestamp(current_start_time).strftime("%b %d, %Y")
                current_end_time = current_data["end"]
                current_end_time = datetime.utcfromtimestamp(current_end_time).strftime("%b %d, %Y")

    
                current_embed = discord.Embed(
                    title=f"**Current Map: ** {current_data['map']}",
                    description=f"**Start Date:** {current_start_time}\n"
                                f"**End Date:** {current_end_time}\n"
                                f"**Code:** {current_data['code']}\n"
                                f"**Duration (Minutes):** {current_data['DurationInMinutes']}\n"
                                f"**Remaining Time (Minutes):** {current_data['remainingMins']}\n"
                                f"**Remaining Timer:** {current_data['remainingTimer']}",
                    color=discord.Color.blue()
                )

                # Create and send embed for next map
                next_data = data["next"]

                next_start_time = next_data["start"]
                next_start_time= datetime.utcfromtimestamp(next_start_time).strftime("%b %d, %Y")
                next_end_time = next_data["end"]
                next_end_time = datetime.utcfromtimestamp(next_end_time).strftime("%b %d, %Y")

                next_embed = discord.Embed(
                    title=f"**Next Map: ** {next_data['map']}",
                    description=f"**Start Date:** {next_start_time}\n"
                                f"**End Date:** {next_end_time}\n"
                                f"**Code:** {next_data['code']}\n"
                                f"**Duration (Minutes):** {next_data['DurationInMinutes']}",
                    color=discord.Color.green()
                )

                # Send the embeds
                await ctx.send(embed=current_embed)
                await ctx.send(embed=next_embed)

                
            else:
                await ctx.send("Error in executing curl command:" + result.stderr)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(client):
    await client.add_cog(Apex(client))
