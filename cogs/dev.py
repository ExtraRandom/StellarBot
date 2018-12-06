from discord.ext import commands
import discord
from cogs.utils import perms, IO
from datetime import datetime, timedelta
import os


class Dev:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bots current uptime"""
        try:
            data = IO.read_settings_as_json()
            if data is None:
                await ctx.send(IO.settings_fail_read)
                return

            login_time = datetime.strptime(data['info']['last-login-time'], "%Y-%m-%d %H:%M:%S.%f")
            now = datetime.now()

            td = timedelta.total_seconds(now - login_time)
            td = int(td)

            m, s = divmod(td, 60)
            h, m = divmod(m, 60)
            uptime = "%d:%02d:%02d" % (h, m, s)

            await ctx.send("Bot Uptime: {}".format(uptime))

        except Exception as e:
            await ctx.send("Error getting bot uptime. Reason: {}".format(type(e).__name__))

    @commands.command()
    async def github(self, ctx):
        """Link to the bot's source code"""
        await ctx.send("https://github.com/ExtraRandom/Blue2Bot")

    @commands.command(aliases=["version", "update"])
    async def changelog(self, ctx):
        """See what was changed in the last few updates"""
        if not os.path.isdir(os.path.join(self.bot.base_directory, ".git")):
            await ctx.send("Bot wasn't installed with Git")
            return

        result = os.popen('cd {} &&'
                          'git show -s -n 3 HEAD --format="%cr|%s|%H"'.format(self.bot.base_directory)).read()

        cl = discord.Embed(title="Bot Changelog")

        lines = result.split("\n")

        for line in lines:
            if line is not "":
                time_ago, changed, c_hash = str(line).split("|")
                cl.add_field(name="Changes committed {}".format(time_ago),
                             value="{}\n".format(changed.replace(" [", "\n[")))

        await ctx.send(embed=cl)

    # @commands.command()
    # async def err(self):
    #    print(10 / 0)
    #    open(self.bot.base_directory)


def setup(bot):
    bot.add_cog(Dev(bot))






