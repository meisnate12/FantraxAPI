from datetime import datetime
from typing import TYPE_CHECKING

from .base import FantraxBaseObject
from .player import Player
from .team import Team

if TYPE_CHECKING:
    from .league import League


class Transaction(FantraxBaseObject):
    """Represents a single Transaction.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Transaction ID.
        team (Team): Team who made the Transaction.
        date (datetime): Transaction Date.
        players (list[TransactionPlayer]): Players in the Transaction.

    """

    def __init__(self, league: "League", data: list[dict]) -> None:
        super().__init__(league, data)
        self.id: str = self._data[0]["txSetId"]
        self.team: Team = self.league.team(self._data[0]["cells"][0]["teamId"])
        self.date: datetime = datetime.strptime(self._data[0]["cells"][1]["content"], "%a %b %d, %Y, %I:%M%p")
        tc = "transactionCode"
        self.players: list[TransactionPlayer] = [TransactionPlayer(self.league, p["scorer"], p["claimType"] if p[tc] == "CLAIM" else p[tc]) for p in self._data]

    def __str__(self) -> str:
        return str(self.players)


class TransactionPlayer(Player):
    """Represents a single Player from a Transaction.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Player ID.
        name (str): Player Name.
        short_name (str): Player Short Name.
        team_name (str): Team Name.
        team_short_name (str): Team Short Name.
        pos_short_name (str): Player Positions.
        positions (list[Position]): Player Positions.
        all_positions (list[Position]): Positions Player can be placed into.
        day_to_day (bool): Player Day-to-Day.
        out (bool): Player Out.
        injured_reserve (bool): Player on Injured Reserve.
        suspended (bool): Player Suspended.
        injured (bool): Player either Day-to-Day, Out, or on Injured Reserve.
        type (str): Transaction Type.
    """

    def __init__(self, league: "League", data: dict, transaction_type: str) -> None:
        super().__init__(league, data)
        self.type: str = transaction_type

    def __str__(self) -> str:
        return f"{self.type} {self.name}"
