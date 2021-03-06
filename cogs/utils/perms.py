from discord.ext import commands
import discord


def is_server_owner():
    def predicate(ctx):
        return ctx.message.author.id == ctx.message.channel.server.owner

    return commands.check(predicate)


def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == 92562410493202432

    return commands.check(predicate)


"""
taken from
https://github.com/ExtraRandom/Discord-Bot/blob/2aee29b05becd612757197d76777e05b807cacb6/helpers/checks.py
"""


def is_owner_check(message):
    return message.author.id == message.channel.server.owner


def check_permissions(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    if ch.is_private:
        return False  # can't have roles in PMs

    role = discord.utils.find(check, author.roles)
    return role is not None


def mod_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name in ('Epic', 'Legendary'), **perms)

    return commands.check(predicate)


def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name == 'Bot Admin', **perms)
    return commands.check(predicate)


