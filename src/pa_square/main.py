"""Main bot runner for PA-Square Discord bot."""

import logging

import discord
from discord.ext import commands

from src.pa_square.bot.commands import setup_commands
from src.pa_square.bot.events import setup_events
from src.pa_square.config import config
from src.pa_square.habitica.manager import HabiticaManager
from src.pa_square.utils.keep_alive import keep_alive


def setup_logging() -> logging.FileHandler:
    """
    Set up logging configuration.
    
    Returns:
        Configured file handler
    """
    handler = logging.FileHandler(
        filename=config.LOG_FILE,
        encoding="utf-8",
        mode="w"
    )
    logging.getLogger("asyncio").setLevel(getattr(logging, config.LOG_LEVEL))
    return handler


def create_bot() -> commands.Bot:
    """
    Create and configure Discord bot instance.
    
    Returns:
        Configured Discord bot
    """
    # Initialize intent handler
    intents = discord.Intents.default()
    # Manually enable the intents we actually need
    intents.message_content = True
    intents.members = True
    
    # Initialize bot with command prefix and permissions determined by intents
    bot = commands.Bot(command_prefix=config.DISCORD_COMMAND_PREFIX, intents=intents)
    
    return bot


async def run_bot() -> None:
    """Run the Discord bot with all configurations."""
    # Validate configuration
    config.validate()
    
    # Start keep-alive server
    keep_alive()
    
    # Set up logging
    handler = setup_logging()
    
    # Create bot and Habitica manager
    bot = create_bot()
    habitica_manager = HabiticaManager()
    
    # Set up events and commands
    await setup_events(bot, habitica_manager)
    await setup_commands(bot, habitica_manager)
    
    # Run the bot
    await bot.start(config.DISCORD_TOKEN)


def main() -> None:
    """Entry point for the bot."""
    import asyncio
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
        raise


if __name__ == "__main__":
    main()
