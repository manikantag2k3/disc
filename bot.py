import discord
from discord import Intents
import requests
from datetime import datetime
import logging
import asyncio
from datetime import timedelta
from bs4 import BeautifulSoup
import aiohttp

# Replace with your own bot token
BOT_TOKEN = "MTIwODI4ODk4NzI3ODYxNDU2OQ.Gxb1qb.jHO7PZJL8XtYvDYT-DMorKPOOk-zAIXzXF1uQI"

# Channel ID for contest notifications (or leave empty for DM)
NOTIFICATION_CHANNEL_ID = 1208294030471991308

# Platforms to track, add "leetcode", "geeksforgeeks", etc.
TRACKED_PLATFORMS = ["codeforces", "leetcode"]

# Logging configuration
logging.basicConfig(filename='contest_bot.log', level=logging.INFO)

intents=Intents.default()
client = discord.Client(intents=intents)



async def get_upcoming_contests(platform):
    contests = []
    if platform == "codeforces":
        response = requests.get("https://codeforces.com/api/contest.list")
        data = response.json()
        for contest in data["result"]:
            contests.append({
                "name": contest["name"],
                "start_time": datetime.fromtimestamp(contest["startTimeSeconds"]),
                "link": "https://codeforces.com/contest/"
            })
    elif platform == "leetcode":
        leet_contests =await get_upcoming_contests_leet()
        contests.extend(leet_contests)
    return contests




async def get_upcoming_contests_leet():
    url = "https://leetcode.com/contest/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    soup = BeautifulSoup(text, 'html.parser')
    contest_divs = soup.find_all('div', {'class': 'h-[54px]'})

    contests = []
    for contest_div in contest_divs:
        name_div = contest_div.find('div', {'class': 'truncate'})
        time_div = contest_div.find('div', {'class': 'flex items-center text-[14px] leading-[22px] text-label-2 dark:text-dark-label-2'})
        if name_div and time_div:
            contest_name = name_div.find('span').text.strip().lower().replace(' ', '-')
            contest_time = time_div.text.strip()
            contests.append({
                "name": contest_name,
                "start_time": contest_time,
                "link": url+contest_name+"/"
            })
    return contests
# Notification formatting function (can be customized)
def format_notification(contest):
    return f"Contest alert! Upcoming {contest['name']} starts at {contest['start_time']}. Join here: {contest['link']}"

async def send_notification(message):
    channel = client.get_channel(NOTIFICATION_CHANNEL_ID) or client.user
    await channel.send(message)



async def check_for_new_contests():
    while True:
        for platform in TRACKED_PLATFORMS:
            contests = await get_upcoming_contests(platform)
            for contest in contests:
                if platform == "leetcode" or timedelta(hours=0) < (contest['start_time'] - datetime.now()) <= timedelta(days=1):
                    notification = format_notification(contest)
                    print(f"Sending notification: {notification}")  # Debugging line
                    await send_notification(notification)
        await asyncio.sleep(6 * 60 * 60)  # Sleep for 6 hours

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    asyncio.create_task(check_for_new_contests())

client.run(BOT_TOKEN)