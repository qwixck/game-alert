import discord
from discord.ext import commands, tasks

import aiohttp
import json
import datetime

class EpicGames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.epicGamesIcon = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/1764px-Epic_Games_logo.svg.png"
        self.epicGames.start()

    @tasks.loop(minutes=1)
    async def epicGames(self):
        try:
            await self.bot.wait_until_ready()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions") as request:
                    if not request.ok:
                        print(f"Something wrong with Epic Games API! HTTP code: {request.status}")
                    epicGames = await request.json()
            await session.close()
            list = []
            with open("./src/data/games.json", "r") as f:
                games: dict = json.load(f)
            for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
                if i["promotions"]:
                    if i["promotions"]["promotionalOffers"]:
                        if not i["price"]["totalPrice"]["discountPrice"]:
                            if not i["title"] in games["games"]:
                                embed = discord.Embed(title=i["title"], description=i["description"], url=f"https://epicgames.com/store/product/{i['productSlug']}", color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
                                embed.set_image(url=i["keyImages"][0]["url"])
                                embed.set_author(name="Epic Games", icon_url=self.epicGamesIcon)
                                list.append(embed)
                                games["games"].append(i["title"])
            with open("./src/data/games.json", "w") as f:
                json.dump(games, f, indent=2)
            with open("./src/data/channels.json", "r") as f:
                channels: dict = json.load(f)
            for channel in channels:
                try:
                    _channel = self.bot.get_channel(channels[str(channel)]["channel"])
                    await _channel.send(embeds=list)
                except discord.errors.HTTPException:
                    pass
                except AttributeError:
                    pass
                except Exception as e:
                    print(f"Unknown error: {e}")
        # why all try/except all this shit? cause when site is down (prob) it still gives 200 OK but just no arrays, and bot crashes
        except Exception as e:
            print("Error")
            print(e)

def setup(bot: commands.Bot):
    bot.add_cog(EpicGames(bot))