from datetime import date
from typing import TYPE_CHECKING

from .base import FantraxBaseObject
from .position import Position

if TYPE_CHECKING:
    from .league import League
    from .team import Team


class Player(FantraxBaseObject):
    """Represents a single Player.

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
        team (Team): Fantasy Team Player is on.
        points (float): Player Fantasy Points for the Points Date.
        points_date (date): date Player scored points.
        injured (bool): Player either Day-to-Day, Out, or on Injured Reserve.
    """

    def __init__(self, league: "League", data: dict, transaction_type: str | None = None) -> None:
        super().__init__(league, data)
        self.type: str | None = transaction_type
        self.id: str = self._data["scorerId"]
        self.name: str = self._data["name"]
        self.short_name: str = self._data["shortName"]
        self.team_name: str = self._data["teamName"]
        self.team_short_name: str = self._data["teamShortName"] if "teamShortName" in self._data else self.team_name
        self.pos_short_name: str = self._data["posShortNames"]
        self.positions: list[Position] = [self.league.positions[d] for d in self._data["posIdsNoFlex"]]
        self.all_positions: list[Position] = [self.league.positions[d] for d in self._data["posIds"]]
        self.day_to_day: bool = False
        self.out: bool = False
        self.injured_reserve: bool = False
        self.suspended: bool = False
        self.team: Team | None = None
        self.points: float | None = None
        self.points_date: date | None = None
        if "icons" in self._data:
            for icon in self._data["icons"]:
                match icon["typeId"]:
                    case "1":
                        self.day_to_day = True
                    case "2":
                        self.injured_reserve = True
                    case "30":
                        self.out = True
                    case "6":
                        self.suspended = True

    @property
    def injured(self) -> bool:
        return self.day_to_day or self.out or self.injured_reserve

    def __str__(self) -> str:
        return f"{self.type} {self.name}" if self.type else self.name

    def update_points(self, team_id: str, points: float, points_date: date) -> None:
        self.team = self.league.team(team_id)
        self.points = points
        self.points_date = points_date
