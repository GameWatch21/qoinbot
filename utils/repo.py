from utils import default

version = "v1.0.0"
invite = "https://discord.gg/Fjd3h2Q"
owners = default.get("config.json").owners


def is_owner(ctx):
    return ctx.author.id in owners
