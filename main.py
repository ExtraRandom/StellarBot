import discord
from discord.ext import commands  # from discord.utils import get
from datetime import datetime
import os
from cogs.utils import IO, perms
from cogs.utils.logger import Logger


def get_prefix(d_bot, message):
    prefixes = ["?"]
    return commands.when_mentioned_or(*prefixes)(d_bot, message)


class BlueBot(commands.Bot):
    def __init__(self):
        self.base_directory = os.path.dirname(os.path.realpath(__file__))

        super().__init__(command_prefix=get_prefix,
                         description="Bot Developed by @Extra_Random#2564\n"
                                     "Source code: https://github.com/ExtraRandom/Blue2Bot",
                         pm_help=False)
        self.add_command(self.load)
        self.add_command(self.unload)
        self.add_command(self.reload)
        self.add_command(self.cog_list)

    async def on_ready(self):
        login_time = datetime.now()
        data = IO.read_settings_as_json()

        if data is None:
            raise Exception(IO.settings_fail_read)

        data['info']['last-login-time'] = str(login_time)

        if IO.write_settings(data) is False:
            print(IO.settings_fail_write)

        login_msg = "Bot Logged In at {}".format(login_time)
        Logger.log_write("----------------------------------------------------------\n"
                         "{}\n"
                         "".format(login_msg))
        print(login_msg)

    async def on_message(self, message):
        bot_msg = message.author.bot
        if bot_msg is True:
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        channel = ctx.message.channel

        if error.__cause__ is not None and str(error.__cause__).startswith("could not convert"):
            # workaround for commands.ConversionError seemingly not picking up this error
            # maybe change to be state that issue
            formatter = commands.formatter.HelpFormatter()
            f_help = await formatter.format_help_for(ctx, ctx.command)
            cmd_info = f_help[0]
            await channel.send(cmd_info)
            return

        if isinstance(error, commands.MissingRequiredArgument):
            formatter = commands.formatter.HelpFormatter()
            f_help = await formatter.format_help_for(ctx, ctx.command)
            cmd_info = f_help[0]
            await channel.send(cmd_info)
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            await channel.send("You do not have permission to use that command!")
        elif isinstance(error, commands.CommandOnCooldown):
            await channel.send("This command is currently on cooldown. {}" 
                                             "".format(str(error).split(". ")[1]))
        else:
            cmd = str(ctx.command)
            full_cmd = ctx.message.content
            try:
                cog = self.get_command(cmd).cog_name
            except AttributeError:
                s_cmd = cmd.split(" ")[0]
                cog = self.get_command(s_cmd).cog_name

            err_msg = "----------------------------------------------------------\n" \
                      "An Error Occurred at {}\n" \
                      "Command: {} ({})\n" \
                      "    Cog: {}\n" \
                      "  Error: {}\n" \
                      "   Args: {}\n" \
                      "----------------------------------------------------------" \
                      "".format(Logger.time_now(), cmd, full_cmd, cog, error, error.args)
            Logger.log_write(err_msg)
            await channel.send("**Command Errored:**\n "
                               "{}".format(error))

    @staticmethod
    def get_cogs_in_folder():
        c_dir = os.path.dirname(os.path.realpath(__file__))
        c_list = []
        for file in os.listdir(os.path.join(c_dir, "cogs")):
            if file.endswith(".py"):
                c_list.append(file.replace(".py", ""))
        return c_list

    @staticmethod
    def get_cogs_in_settings():
        c_list = []
        data = IO.read_settings_as_json()
        if data is None:
            return None
        for cog in data['cogs']:
            c_list.append(cog)
        return c_list

    @staticmethod
    def ensure_all_fields(settings_data):
        fields = \
            {
                "keys": {
                    "token": None,
                    "itad-api-key": None,
                    "fixer-io-key": None,
                    "ftn-api-key": None,
                    "trn-api-key": None
                },
                "cogs": {},
                "info": {
                    "last-login-time": None
                }
            }
        sd_len = len(settings_data)
        if sd_len == 0:
            settings_data = fields
            return settings_data
        else:
            for top_field in fields:
                if top_field in settings_data:
                    for inner_field in fields[top_field]:
                        if inner_field not in settings_data[top_field]:
                            settings_data[top_field][inner_field] = None
                            Logger.write("Settings.json - Added inner field '{}' to category '{}'".format(inner_field,
                                                                                                          top_field))
                else:
                    settings_data[top_field] = {}

                    Logger.write("Settings.json - Added category '{}'".format(top_field))

                    for inner_field in fields[top_field]:
                        if inner_field not in settings_data[top_field]:
                            settings_data[top_field][inner_field] = None
                            Logger.write("Settings.json - Added inner field '{}' to category '{}'".format(inner_field,
                                                                                                          top_field))

            return settings_data

    def run(self):
        first_time = False
        s_data = {}

        """First time run check"""
        if os.path.isfile(IO.settings_file_path) is False:
            Logger.write_and_print("First Time Run")
            first_time = True

        else:
            s_data = IO.read_settings_as_json()
            if s_data is None:
                raise Exception(IO.settings_fail_read)

        s_data = self.ensure_all_fields(s_data)

        """Load cogs"""
        folder_cogs = self.get_cogs_in_folder()
        for folder_cog in folder_cogs:
            cog_path = "cogs.{}".format(folder_cog)
            if first_time is True:
                s_data['cogs'][folder_cog] = True
            else:
                try:
                    should_load = s_data['cogs'][folder_cog]
                except KeyError:
                    Logger.write("New Cog '{}'".format(folder_cog))
                    s_data['cogs'][folder_cog] = True
                    should_load = True

                if should_load is True:
                    try:
                        self.load_extension(cog_path)
                    except Exception as exc:
                        print("Failed to load cog '{}', Reason: {}".format(folder_cog, type(exc).__name__))
                        Logger.write(exc)
                        s_data['cogs'][folder_cog] = False

        """Get token"""
        if first_time is True:
            if IO.write_settings(s_data) is False:
                raise Exception(IO.settings_fail_write)
            token = None
        else:
            token = s_data['keys']['token']

        """Clean up removed cogs from settings"""
        r_cogs = self.get_cogs_in_folder()
        f_cogs = self.get_cogs_in_settings()
        for f_cog in f_cogs:
            if f_cog not in r_cogs:
                Logger.write_and_print("Cog '{}' no longer exists, removing settings entry".format(f_cog))
                del s_data['cogs'][f_cog]

        """Write settings to file"""
        if IO.write_settings(s_data) is False:
            raise Exception(IO.settings_fail_write)

        if token:
            super().run(token)
        else:
            Logger.write_and_print("Token is not set! Go to {} and change the token parameter!"
                                   "".format(IO.settings_file_path))

    @commands.command(hidden=True)
    @perms.is_dev()
    async def load(self, ctx, *, cog: str):
        """Load a cog"""
        cog_list = []
        for c_file in os.listdir(os.path.join(self.base_directory, "cogs")):
            if c_file.endswith(".py"):
                cog_list.append("cogs.{}".format(c_file.replace(".py", "")))

        l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

        if l_cog_name in cog_list:
            try:
                self.load_extension(l_cog_name)
                await ctx.send("Successfully loaded cog '{}'.".format(cog))
            except Exception as e:
                Logger.write(e)
                await ctx.send("Failed to load cog '{}'. Reason: {}".format(cog, type(e).__name__))
                return
        else:
            await ctx.send("No cog called '{}'.".format(cog))
            return

        data = IO.read_settings_as_json()
        if data is None:
            await ctx.send(IO.settings_fail_read)
            return

        data['cogs'][cog] = True

        if IO.write_settings(data) is False:
            await ctx.send(IO.settings_fail_write)
            return

    @commands.command(hidden=True)
    @perms.is_dev()
    async def unload(self, ctx, *, cog: str):
        """Unload a cog"""
        ext_list = self.extensions
        cog_list = []
        for cogs in ext_list:
            cog_list.append(cogs)

        l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

        if l_cog_name in cog_list:
            try:
                self.unload_extension(l_cog_name)
                await ctx.send("Successfully unloaded cog '{}'.".format(cog))
            except Exception as e:
                await ctx.say("Failed to unload cog '{}'. Reason: {}".format(cog, type(e).__name__))
                return
        else:
            await ctx.send("No loaded cog called '{}'.".format(cog))
            return

        data = IO.read_settings_as_json()
        if data is None:
            await ctx.send(IO.settings_fail_read)
            return
        data['cogs'][cog] = False
        if IO.write_settings(data) is False:
            await ctx.send(IO.settings_fail_write)
            return

    @commands.command(hidden=True)
    @perms.is_dev()
    async def reload(self, ctx, *, cog: str):
        """Reload a cog"""
        ext_list = self.extensions
        cog_list = [cog for cog in ext_list]

        cog_n = "cogs.{}".format(cog)
        if cog_n in cog_list:
            try:
                self.unload_extension(cog_n)
            except Exception as e:
                Logger.write(e)
                await ctx.send("Failed to unload cog '{}'".format(cog))
                return
        else:
            await ctx.send("No loaded cogs called '{}'".format(cog))
            return

        try:
            self.load_extension(cog_n)
            await ctx.send("Successfully reloaded cog '{}'".format(cog))
        except Exception as e:
            Logger.write(e)
            await ctx.send("Failed to reload cog '{}'")
            return

    @commands.command(hidden=True, name="cogs")
    @perms.is_dev()
    async def cog_list(self, ctx):
        """List loaded and unloaded cogs"""
        ext_list = self.extensions
        loaded = []
        unloaded = []
        for cog in ext_list:
            loaded.append(str(cog).replace("cogs.", ""))

        for cog_f in os.listdir(os.path.join(self.base_directory, "cogs")):
            if cog_f.endswith(".py"):
                if cog_f.replace(".py", "") not in loaded:
                    unloaded.append(cog_f.replace(".py", ""))

        await ctx.send("```diff\n"
                       "+ Loaded Cogs:\n{}\n\n"
                       "- Unloaded Cogs:\n{}"
                       "```"
                       "".format(", ".join(sorted(loaded)),
                                 ", ".join(sorted(unloaded))))


if __name__ == '__main__':
    the_bot = BlueBot()
    the_bot.run()
