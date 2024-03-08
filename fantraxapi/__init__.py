import importlib.metadata

from fantraxapi.fantrax import FantraxAPI
from fantraxapi.exceptions import FantraxException
from fantraxapi.objs import DraftPick, Matchup, Player, Position, Record, ScoringPeriod, Standings, Team, Trade, TradeBlock, TradePlayer, Transaction

try:
    __version__ = importlib.metadata.version("fantraxapi")
except importlib.metadata.PackageNotFoundError:
    __version__ = ""
__author__ = "Nathan Taggart"
__credits__ = "meisnate12"
__package_name__ = "fantraxapi"
__project_name__ = "FantraxAPI"
__description__ = "A lightweight Python library for The Fantrax API."
__url__ = "https://github.com/meisnate12/FantraxAPI"
__email__ = "meisnate12@gmail.com"
__license__ = "MIT License"
__all__ = [
    "FantraxAPI",
    "FantraxException",
    "DraftPick",
    "Matchup",
    "Player",
    "Position",
    "Record",
    "ScoringPeriod",
    "Standings",
    "Team",
    "Trade",
    "TradeBlock",
    "TradePlayer",
    "Transaction"
]
