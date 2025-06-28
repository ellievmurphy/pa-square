import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from utils.keep_alive import keep_alive
from models.habitica import HabiticaManager

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN") # get discord token

keep_alive()

# creates an IO connection to the discord.log file in our project to read and write content
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# initialize intent handler
intents = discord.Intents.default()
# manually enable the intents we actually need
intents.message_content = True
intents.members = True

# initializes a bot that can be given commands with '!' prefix and permissions determined by intents
bot = commands.Bot(command_prefix='!', intents=intents)
# initializes the manager for our habitica api and state management
habitica = HabiticaManager()

default_role = "PAPA Follower"

@bot.event
async def login():
    await habitica.ensure_session()

@bot.event
async def logout():
    await habitica.close_session()

@bot.event
async def on_ready():
    print(f"We are able to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return # don't want to reply to our own bot's message
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} THAT'S A NO-NO WORD")
    # process_commands allows us to continue handling all the messages sent in the server
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}") # send message in current channel (ctx)

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=default_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {default_role}")
    else:
        await ctx.send("Role doesn't exist. Stop with your tomfoolery")

# The '*, msg' syntax denotes that anything after the command 'dm' will be stored in variable msg
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"Psst: {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply(f"Psst back {ctx.author.mention}")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def unassign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=default_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} is unassigned from {default_role}")
    else:
        await ctx.send("Role doesn't exist. Stop with your tomfoolery")

@bot.command()
@commands.has_role(default_role)
async def secret(ctx):
    await ctx.send(f"One of us. One of us. {ctx.author.mention}")
# if the above def errors, the following will run
@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You can't do that 0.0 {error}")

bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)

