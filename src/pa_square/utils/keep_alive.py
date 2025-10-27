"""Keep-alive Flask server for bot monitoring."""

from threading import Thread

from flask import Flask

from src.pa_square.config import config

app = Flask(__name__)


@app.route("/")
def home() -> str:
    """Health check endpoint."""
    return "Bot is running!"


def run() -> None:
    """Run Flask server."""
    app.run(host=config.KEEP_ALIVE_HOST, port=config.KEEP_ALIVE_PORT)


def keep_alive() -> None:
    """Start keep-alive server in background thread."""
    t = Thread(target=run, daemon=True)
    t.start()
