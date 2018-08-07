import discord
from discord.ext import commands
from GameStoresAPI.Steam.steam import Steam
from GameStoresAPI.ITAD.itad import Itad
from GameStoresAPI.Playstation.playstation import Playstation
from cogs.utils import IO, simplify  # , csgo
from cogs.utils.logger import Logger
from datetime import datetime, timedelta


class Games:
    def __init__(self, bot):
        self.bot = bot
        self.fetching = "Retrieving data... please wait!"

    @commands.command(name="steam", pass_context=True)
    async def steam_search(self, ctx):
        """Search for games on steam"""
        msg = await self.bot.say(self.fetching)

        term = simplify.remove_prefix_in_message(self.bot, ctx.message, "steam")
        if term is None:
            await self.bot.edit_message(msg, "Please provide a search term for the Steam Command")
            return

        results = Steam.search_by_name(Steam.format_search(term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on Steam".format(term),
                              colour=discord.Colour.blue())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(term))
            await self.bot.edit_message(msg, embed=embed)
            return

        g_counter = 0

        for i in range(1, len_res):
            g_counter += 1
            if g_counter >= 5:
                break
            price = results[i]['price']
            steam_url = results[i]['store_url']
            steam_url_split = str(steam_url).split("/")
            steam_link = steam_url_split[0] + "//" + steam_url_split[1] + "/" + steam_url_split[2] \
                + "/" + steam_url_split[3] + "/" + steam_url_split[4]

            if results[i]['discount'] != "None":
                price = "{}\nCurrent Discount: {}".format(price, results[i]['discount'])

            embed.add_field(name="{}".format(results[i]['title']),
                            value="Release: {}\n"
                                  "Price: {}\n"
                                  "URL: {}"
                                  "".format(results[i]['release_date'], price, steam_link))

        await self.bot.edit_message(msg, embed=embed)

    @commands.command(pass_context=True)
    async def itad(self, ctx):
        """Search for games on ITAD.com using Steam App ID's"""
        msg = await self.bot.say(self.fetching)

        term = simplify.remove_prefix_in_message(self.bot, ctx.message, "itad")
        if term is None:
            await self.bot.edit_message(msg, "Please provide a search term for the ITAD Command")
            return

        results = Steam.search_by_name(Steam.format_search(term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on IsThereAnyDeal.com".format(term),
                              colour=discord.Colour.red())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(term))
            await self.bot.edit_message(msg, embed=embed)
            return

        g_counter = 0
        app_id_list = []
        for i in range(1, len_res):
            g_counter += 1
            if g_counter >= 5:
                break
            steam_url = results[i]['store_url']
            steam_url_split = steam_url.split("/")
            app_id = steam_url_split[3] + "/" + steam_url_split[4]
            app_id_list.append(app_id)

        s_data = IO.read_settings_as_json()
        if s_data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        if s_data['keys']['itad-api-key'] is None:
            await self.bot.say("ITAD API Key hasn't been set. Go to the settings file to set it now!")
            return
        else:
            api_key = s_data['keys']['itad-api-key']

        plains = Itad.get_multiple_plains_from_steam_appids(api_key, app_id_list)

        p_counter = 1
        for plain in plains:
            title = results[p_counter]['title']
            p_counter += 1
            price, shop, url = Itad.get_best_price(api_key, plain)
            embed.add_field(name="{}".format(title),
                            value="Price: £{}\n"
                                  "Shop: {}\n"
                                  "URL: {}"
                                  "".format(price, url, shop))

        await self.bot.edit_message(msg, embed=embed)

    @commands.command(pass_context=True)
    async def ps4(self, ctx):
        """Search for PS4 games on the UK Playstation Store"""
        msg = await self.bot.say(self.fetching)

        try:
            term = simplify.remove_prefix_in_message(self.bot, ctx.message, "ps4")
            url_base = "https://store.playstation.com"

            if term is None:
                await self.bot.say("Please provide a search term for the ps4 command")
                return

            s_url = Playstation.format_url(["games", "bundles"],
                                           ["ps4"],
                                           term)

            search_data = Playstation.get_data(s_url)

            results = discord.Embed(title="PS4 PSN Search for '{}'".format(term),
                                    colour=discord.Colour.dark_blue(),
                                    description="Search results from Playstation Store UK")

            for game in search_data:
                results.add_field(name="{}\n".format(game['title']),
                                  value="Price: {}\n"
                                        "Link: {}\n"
                                        "".format(game['price'], (url_base + game['id'])))

            await self.bot.edit_message(msg, embed=results)
        except Exception as e:
            Logger.write(e)
            await self.bot.edit_message(msg, "PS4 Game Search Failed")

    @commands.command(pass_context=True)
    async def ps3(self, ctx):
        """Search for PS3 games on the UK Playstation Store"""
        msg = await self.bot.say(self.fetching)

        try:
            term = simplify.remove_prefix_in_message(self.bot, ctx.message, "ps3")
            url_base = "https://store.playstation.com"

            if term is None:
                await self.bot.say("Please provide a search term for the ps3 command")
                return

            s_url = Playstation.format_url(["games", "bundles"],
                                           ["ps3"],
                                           term)

            search_data = Playstation.get_data(s_url)

            results = discord.Embed(title="PS3 PSN Search for '{}'".format(term),
                                    colour=discord.Colour.dark_blue(),
                                    description="Search results from Playstation Store UK")

            for game in search_data:
                results.add_field(name="{}\n".format(game['title']),
                                  value="Price: {}\n"
                                        "Link: {}\n"
                                        "".format(game['price'], (url_base + game['id'])))

            await self.bot.edit_message(msg, embed=results)
        except Exception as e:
            Logger.write(e)
            await self.bot.edit_message(msg, "PS3 Game Search Failed")

    @commands.command(aliases=["76", "fallout", "f76", "fo76"])
    async def fallout76(self):
        """Fallout 76 Countdown"""
        rd = datetime(year=2018, month=11, day=14, hour=0, minute=0, second=0, microsecond=0)
        now = datetime.now()
        td = timedelta.total_seconds(rd - now)

        m, s = divmod(td, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        cd_str = ("%d:%02d:%02d:%02d" % (d, h, m, s))
        day, hour, minute, second = cd_str.split(":")

        if int(day) <= -1:
            await self.bot.say("Fallout 76 is out now!")
            return
        elif int(day) == 0:
            if int(hour) >= 1:
                await self.bot.say("It's so close! Fallout 76 releases in {} hours, {} minutes and {} seconds"
                                   "".format(hour, minute, second))
                return
            else:  # hour is 0
                if int(minute) >= 1:
                    await self.bot.say("Only {} minutes and {} seconds until Fallout 76 is released!"
                                       "".format(minute, second))
                    return
                else:
                    await self.bot.say("Wew lad, only {} seconds until Fallout 76 is upon us."
                                       "".format(second))
                    return
        else:
            await self.bot.say("Fallout 76 is {} days, {} hours, {} minutes and {} seconds away from release."
                               "".format(day, hour, minute, second))
            return


def setup(bot):
    bot.add_cog(Games(bot))


