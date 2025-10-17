from datetime import datetime
from typing import TYPE_CHECKING

from .base import FantraxBaseObject
from .player import Player
from .position import Position
from .team import Team

if TYPE_CHECKING:
    from .league import League


class TradeBlock(FantraxBaseObject):
    """Represents a single Trade Block.

    Attributes:
        league (League): The League instance this object belongs to.
        team (Team): Team of the Trade Block.
        update_date (datetime): Last Updated Date.
        note (str): Trading Block Note.
        players_offered (dict[str, list[Player]]): Players Offered.
        positions_wanted (dict[str, list[Player]]): Players Wanted.
        positions_offered (list[Position]): Positions Offered.
        positions_wanted (list[Position]): Positions Wanted.
        stats_offered (list[str]): Stats Offered.
        stats_wanted (list[str]): Stats Wanted.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        self.team: Team = self.league.team(self._data["teamId"])
        self.update_date: datetime = datetime.fromtimestamp(self._data["lastUpdated"]["date"] / 1e3)
        self.note: str = self._data["comment"]["body"] if "comment" in self._data else ""
        self.players_offered: dict[str, list[Player]] = {}
        if "scorersOffered" in self._data:
            self.players_offered = {self.league.positions[k].short_name: [Player(self.league, p) for p in ps] for k, ps in self._data["scorersOffered"]["scorers"].items()}
        self.players_wanted: dict[str, list[Player]] = {}
        if "scorersWanted" in self._data:
            self.players_wanted = {self.league.positions[k].short_name: [Player(self.league, p) for p in players] for k, players in self._data["scorersWanted"]["scorers"].items()}
        self.positions_offered: list[Position] = [self.league.positions[pos] for pos in self._data["positionsOffered"]["positions"]] if "positionsOffered" in self._data else []
        self.positions_wanted: list[Position] = [self.league.positions[pos] for pos in self._data["positionsWanted"]["positions"]] if "positionsWanted" in self._data else []
        self.stats_offered: list[str] = [s["shortName"] for s in self._data["statsOffered"]["stats"]] if "statsOffered" in self._data else []
        self.stats_wanted: list[str] = [s["shortName"] for s in self._data["statsWanted"]["stats"]] if "statsWanted" in self._data else []

    def __str__(self) -> str:
        return self.note
