from datetime import date
from typing import TYPE_CHECKING

from .base import FantraxBaseObject
from .player import Player
from .position import PositionCount
from .roster import Roster

if TYPE_CHECKING:
    from .league import League


class Team(FantraxBaseObject):
    """Represents a single Team.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Team ID.
        name (str): Team Name.
        short (str): Team Short Name.

    """

    def __init__(self, league: "League", team_id: str, data: dict) -> None:
        super().__init__(league, data)
        self.id: str = team_id
        self.name: str = self._data["name"]
        self.short: str = self._data["shortName"]
        if "logoUrl512" in self._data:
            self.logo: str = self._data["logoUrl512"]
        elif "logoUrl256" in self._data:
            self.logo: str = self._data["logoUrl256"]
        else:
            self.logo: str = self._data["logoUrl128"]

    def __str__(self) -> str:
        return self.name

    def position_counts(self, scoring_period_number: int | None = None) -> dict[str, PositionCount]:
        """Returns a Dictionary of PositionCount objects that represents the positions used for a specific period or the latest period's standings when scoring_period_number is None.

        Args:
            scoring_period_number (int | None): Period Number, defaults to `None`.

        Returns:
            dict[str, PositionCount]: Dictionary of Position Short Names to PositionCount objects.

        """
        return self.league.position_counts(self.id, scoring_period_number=scoring_period_number)

    def live_scores(self, score_date: date) -> list["Player"]:
        """Returns a list of Player objects with scores for that day.

        Args:
            score_date (date): Date of the Live Scoring.

        Returns:
            list[Player]: List of Player objects with scores for that day.

        """
        return self.league.live_scores(score_date)[self.id]

    def roster(self, period_number: int | None = None) -> Roster:
        """Returns a Roster object that represents the Team's roster.

        Args:
            period_number (int | None): Daily Period Number, defaults to None.

        Returns:
            Roster: Roster object that represents the Team's roster.

        """
        return self.league.team_roster(team_id=self.id, period_number=period_number)
