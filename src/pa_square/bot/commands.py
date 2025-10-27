"""Discord bot commands."""

import discord
from discord.ext import commands

from src.pa_square.config import config
from src.pa_square.habitica.manager import HabiticaManager


async def setup_commands(bot: commands.Bot, habitica_manager: HabiticaManager) -> None:
    """
    Set up bot commands.
    
    Args:
        bot: Discord bot instance
        habitica_manager: Habitica API manager instance
    """
    
    @bot.command()
    async def hello(ctx: commands.Context) -> None:
        """Say hello to the user."""
        await ctx.send(f"Hello {ctx.author.mention}")
    
    @bot.command()
    async def habitica(ctx: commands.Context) -> None:
        """Test Habitica connection."""
        print("Checking habitica session...")
        await habitica_manager.fetch_token()
        await ctx.send("Done!")
    
    @bot.command()
    async def todo(ctx: commands.Context) -> None:
        """Get todos from Habitica."""
        todos = await habitica_manager.get_todos("todos")
        print(f"todos: {todos['data']}")
        await ctx.send(todos["data"][0])
    
    @bot.command()
    async def assign(ctx: commands.Context) -> None:
        """Assign default role to user."""
        role = discord.utils.get(ctx.guild.roles, name=config.DEFAULT_ROLE)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned to {config.DEFAULT_ROLE}")
        else:
            await ctx.send("Role doesn't exist. Stop with your tomfoolery")
    
    @bot.command()
    async def dm(ctx: commands.Context, *, msg: str) -> None:
        """
        Send a direct message to the user.
        
        Args:
            :param msg: Message to send to user in ctx
            :param ctx: Represents Discord command context containing target user info
        """
        await ctx.author.send(f"Psst: {msg}")
    
    @bot.command()
    async def reply(ctx: commands.Context) -> None:
        """Reply to user message."""
        await ctx.reply(f"Psst back {ctx.author.mention}")
    
    @bot.command()
    async def poll(ctx: commands.Context, *, question: str) -> None:
        """
        Create a poll.
        
        Args:
            :param question: Represents the Discord poll question
            :param ctx: Discord command context
        """
        embed = discord.Embed(title="Poll", description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")
    
    @bot.command()
    async def unassign(ctx: commands.Context) -> None:
        """Unassign default role from user."""
        role = discord.utils.get(ctx.guild.roles, name=config.DEFAULT_ROLE)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} is unassigned from {config.DEFAULT_ROLE}")
        else:
            await ctx.send("Role doesn't exist. Stop with your tomfoolery")
    
    @bot.command()
    @commands.has_role(config.DEFAULT_ROLE)
    async def secret(ctx: commands.Context) -> None:
        """Secret command only for users with default role."""
        await ctx.send(f"One of us. One of us. {ctx.author.mention}")
    
    @secret.error
    async def secret_error(ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle secret command errors."""
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"You can't do that 0.0 {error}")
