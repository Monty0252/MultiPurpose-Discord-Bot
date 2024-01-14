from dotenv import load_dotenv
import os
import discord
import aiohttp
from discord.ext import commands
import random
import datetime
import asyncio

load_dotenv()
def run_discord_bot():
    bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())
   

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running')

    @bot.command(name='hi')  # This creates a command !hi
    async def hi(ctx):
        await ctx.send('Hello')
    
    @bot.command(name="deez")
    async def deez(ctx):
        await ctx.send('You dont got any fam :saluting_face:')
    
    @bot.command(name="changeName")
    @commands.has_permissions(manage_nicknames=True)
    async def changeName(ctx, member: discord.Member, nickname: str):
        try:
            await member.edit(nick=nickname)
            await ctx.send(f"Changed {member}'s name to `{nickname}`!")
        except discord.Forbidden:
            await ctx.send("I do not have permission to change nicknames!")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to change nickname. Error: {e}")

    @bot.command(name="rollDeez")
    async def roll(ctx):
        result = random.randint(1, 100)
        user = ctx.author.display_name
        await ctx.send(f':game_die: {user} rolled {result} nutz!')

    @bot.command(name='rollAll')
    async def rollAll(ctx):
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
   
    @bot.command(name="weather")
    async def weather(ctx):
        # Ask for the city
        await ctx.send("Please enter the city name:")

        def check_city(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            city_msg = await bot.wait_for('message', check=check_city, timeout=30.0)  # 30 seconds to reply
        except asyncio.TimeoutError:
            await ctx.send("You did not reply in time!")
            return
        else:
            city = city_msg.content

        # Ask for the type of forecast
        await ctx.send("Do you want the 'current' weather or '5-day' forecast? Enter 'current' or '5'.")

        def check_forecast_type(m):
            return m.author == ctx.author and m.channel == ctx.channel and (m.content.lower() in ['current', '5'])

        try:
            forecast_msg = await bot.wait_for('message', check=check_forecast_type, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("You did not reply in time!")
            return
        else:
            forecast = forecast_msg.content.lower()

        # OpenWeatherMap API Key
        OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')  # Make sure to set this environment variable

        if forecast == "5":
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPEN_WEATHER_API_KEY}&units=imperial"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        city_name = data['city']['name']
                        
                        embed = discord.Embed(
                            title=f"5-Day Forecast for {city_name}",
                            description="",
                            color=0x1E90FF
                        )
                        
                        # Process each forecast entry
                        for forecast in data['list']:
                            # Only process the first entry of each day (around noon)
                            forecast_time = datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S')
                            if forecast_time.hour == 12:
                                temp = forecast['main']['temp']
                                feels_like = forecast['main']['feels_like']
                                wind_speed = forecast['wind']['speed']
                                description = forecast['weather'][0]['description']
                                icon = forecast['weather'][0]['icon']
                                icon_url = f"http://openweathermap.org/img/wn/{icon}.png"
                                
                                temp_emoji = '❄️' if temp <= 32 else '☀️' if temp <= 75 else '🔥'
                                wind_emoji = '🍃' if wind_speed < 5 else '🌬️' if wind_speed < 15 else '💨'
                                

                                embed = discord.Embed(
                                    title=f"Weather Forecast for {data['city']['name']} on {forecast_time.strftime('%A, %B %d')}",
                                    description=f"{description.title()}",
                                    color=0x1E90FF
                                )
                                embed.set_thumbnail(url=icon_url)
                                embed.add_field(name="Temperature", value=f"{temp_emoji} {temp}°F", inline=True)
                                embed.add_field(name="Feels Like", value=f"{temp_emoji} {feels_like}°F", inline=True)
                                embed.add_field(name="Wind Speed", value=f"{wind_emoji} {wind_speed} mph", inline=True)
                                
                                await ctx.send(embed=embed)
                    else:
                        await ctx.send("Could not retrieve weather information.")

        else: 
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API_KEY}&units=imperial"

            async with aiohttp.ClientSession() as session:  
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()  # Parse JSON response

                        # Extract weather data
                        name = data['name']
                        temp = data['main']['temp']
                        feels_like_temp = data['main']['feels_like']

                        wind_speed = data['wind']['speed']
                        weather_description = data['weather'][0]['description']
                        icon = data['weather'][0]['icon']
                        
                        # URL to the weather icon image
                        icon_url = f"http://openweathermap.org/img/wn/{icon}.png"

                        temp_emoji = '❄️' if temp <= 32 else '☀️' if temp <= 75 else '🔥'
                        wind_emoji = '🍃' if wind_speed < 5 else '🌬️' if wind_speed < 15 else '💨'

                        # Create embed
                        embed = discord.Embed(title=f"The current weather in {name}", description=f"{weather_description.title()}", color=0x1E90FF)
                        embed.add_field(name="Temperature", value=f"{temp}°F {temp_emoji}", inline=True)
                        embed.add_field(name="Wind Speed", value=f"{wind_emoji} {wind_speed} m/s", inline=True)
                        embed.add_field(name="Feels Like", value=f"{feels_like_temp}°F", inline=True)  

                        embed.set_thumbnail(url=icon_url) 

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("Could not retrieve weather information.")
    

    DISCORD_BOT_TOKEN= os.getenv('TOKEN')
    bot.run(DISCORD_BOT_TOKEN)
run_discord_bot()