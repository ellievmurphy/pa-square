"""Discord bot event handlers."""

import discord
from discord.ext import commands

from src.pa_square.habitica.manager import HabiticaManager


async def setup_events(bot: commands.Bot, habitica_manager: HabiticaManager) -> None:
    """
    Set up bot event handlers.
    
    Args:
        bot: Discord bot instance
        habitica_manager: Habitica API manager instance
    """
    
    @bot.event
    async def on_connect() -> tuple[int, str]:
        """Handle bot connection to Discord."""
        return habitica_manager.ensure_session()
    
    @bot.event
    async def on_disconnect() -> None:
        """Handle bot disconnection from Discord."""
        await habitica_manager.close_session()
    
    @bot.event
    async def on_ready() -> None:
        """Handle bot ready state."""
        print(f"Roll out, {bot.user.name}")
    
    @bot.event
    async def on_member_join(member: discord.Member) -> None:
        """
        Handle new member joining.
        
        Args:
            member: The member who joined
        """
        await member.send(f"Welcome {member.name}")
    
    @bot.event
    async def on_message(message: discord.Message) -> None:
        """
        Handle incoming messages.
        
        Args:
            message: The message that was sent
        """
        if message.author == bot.user:
            return  # Don't reply to our own bot's message
        
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} THAT'S A NO-NO WORD")
        
        # process_commands allows us to continue handling all the messages sent in the server
        await bot.process_commands(message)
