from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from fantraxapi.exceptions import DateNotInSeason

from .base import FantraxBaseObject
from .player import Player
from .team import Team

if TYPE_CHECKING:
    from .league import League


class Trade(FantraxBaseObject):
    """Represents a single Trade.

    Attributes:
        league (League): The League instance this object belongs to.
        proposed_by (Team): Team Trade Proposed By.
        proposed (datetime): Datetime Trade was Proposed.
        accepted (datetime): Datetime Trade was Accepted.
        executed (datetime): Datetime Trade will be Executed.
        moves (list[TradeDraftPick | TradePlayer]): List of Moves in this Trade.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        info = {i["name"]: i["value"] for i in self._data["usefulInfo"]}

        self.trade_id: str = self._data["txSetId"]
        self.proposed_by = self.league.team(self._data["creatorTeamId"])
        self.proposed: datetime = self._parse_datetime(info["Proposed"])
        self.accepted: datetime = self._parse_datetime(info["Accepted"])
        self.executed: datetime = self._parse_datetime(info["To be executed"])
        self.moves: list[TradeDraftPick | TradePlayer] = []
        for move in self._data["moves"]:
            self.moves.append(TradeDraftPick(self, move) if "draftPick" in move else TradePlayer(self, move))

    def _parse_datetime(self, data: str) -> datetime:
        start = datetime.strptime(data.replace("EDT", str(self.league.start_date.year)), "%b %d, %I:%M %p %Y")
        end = datetime.strptime(data.replace("EDT", str(self.league.end_date.year)), "%b %d, %I:%M %p %Y")
        if self.league.end_date >= start >= self.league.start_date:
            return start
        elif self.league.end_date >= end >= self.league.start_date:
            return end
        raise DateNotInSeason(data)

    def __str__(self) -> str:
        return "\n".join([str(m) for m in self.moves])


class TradeItem(FantraxBaseObject, ABC):
    def __init__(self, trade: "Trade", data: dict) -> None:
        super().__init__(trade.league, data)
        self.trade: Trade = trade
        self.from_team: Team = self.league.team(self._data["from"]["teamId"])
        self.to_team: Team = self.league.team(self._data["to"]["teamId"])

    def __str__(self) -> str:
        return f"From: {self.from_team.name} To: {self.to_team.name} {self._item_description()}"

    @abstractmethod
    def _item_description(self) -> str:
        pass


class TradeDraftPick(TradeItem):
    """Represents a single Traded Draft Pick.

    Attributes:
        league (League): The League instance this object belongs to.
        trade (Trade): The Trade instance this TradeDraftPick belongs to.
        from_team (Team): Fantasy Team Traded From.
        to_team (Team): Fantasy Team Traded To.
        round (int): Draft Pick Round.
        year (int): Draft Pick Year.
        owner (Team): Fantasy Team of Original Pick Owner.

    """

    def __init__(self, trade: Trade, data: dict) -> None:
        super().__init__(trade, data)
        self.round: int = self._data["draftPick"]["round"]
        self.year: int = self._data["draftPick"]["year"]
        self.owner: Team = self.league.team(self._data["draftPick"]["origOwnerTeam"]["id"])

    def _item_description(self) -> str:
        return f"Pick: {self.year}, Round {self.round} ({self.owner.name})"


class TradePlayer(TradeItem):
    """Represents a single Traded Player.

    Attributes:
        league (League): The League instance this object belongs to.
        trade (Trade): The Trade instance this TradePlayer belongs to.
        from_team (Team): Fantasy Team Traded From.
        to_team (Team): Fantasy Team Traded To.
        player (Player): The Player instance this TradePlayer belongs to.
        fantasy_points_per_game (float): Fantasy Points Per Game.
        total_fantasy_points (float): Total Fantasy Points.

    """

    def __init__(self, trade: Trade, data: dict) -> None:
        super().__init__(trade, data)
        self.player: Player = Player(self.league, data["scorer"])
        self.fantasy_points_per_game: float = self._data["scorePerGame"]
        self.total_fantasy_points: float = self._data["score"]

    def _item_description(self) -> str:
        return f"TradePlayer: {self.player.name} {self.player.pos_short_name} - {self.player.team_short_name} {self.fantasy_points_per_game} {self.total_fantasy_points}"
