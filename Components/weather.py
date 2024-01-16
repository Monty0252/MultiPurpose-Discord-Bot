import os
import discord
import aiohttp
from discord.ext import commands
import random
import datetime
import asyncio
import json

# OpenWeatherMap API Key
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    OPEN_WEATHER_API_KEY = config["OPEN_WEATHER_API_KEY"]
    

class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Weather.py is ready!")


    @commands.command(name="weather")
    async def weather(self, ctx):
        # Ask for the city
        await ctx.send("Please enter the city name:")

        def check_city(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            city_msg = await self.client.wait_for('message', check=check_city, timeout=30.0)  # 30 seconds to reply
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
            forecast_msg = await self.client.wait_for('message', check=check_forecast_type, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("You did not reply in time!")
            return
        else:
            forecast = forecast_msg.content.lower()

        

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



async def setup(client):
    await client.add_cog(Weather(client))