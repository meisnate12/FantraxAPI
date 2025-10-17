import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Self

from fantraxapi import NotTeamInLeague

from .base import FantraxBaseObject
from .team import Team

if TYPE_CHECKING:
    from .league import League


class ScoringPeriod(FantraxBaseObject):
    """Represents a single Period.

    Attributes:
        league (League): The League instance this object belongs to.
        start (date): Date this scoring period starts.
        end (date): Date this scoring period ends.
        number (int): Period number.
        range (str): String display of the Scoring Period range.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        dates = self._data["name"][1:-1].split(" - ")
        self.start: date = datetime.strptime(dates[0], "%b %d/%y").date()
        self.end: date = datetime.strptime(dates[1], "%b %d/%y").date()
        self.number: int = self._data["value"]

    @property
    def range(self) -> str:
        return f"{self.start.strftime('%Y-%m-%d')} - {self.end.strftime('%Y-%m-%d')}"

    def __eq__(self, other: str | int | Self) -> bool:
        if isinstance(other, ScoringPeriod):
            return self.league.league_id == other.league.league_id and self.number == other.number
        elif isinstance(other, int):
            return self.number == other
        elif isinstance(other, str) and other.isnumeric():
            return self.number == int(other)
        return False

    def __str__(self) -> str:
        return f"[{self.number}:{self.range}]"


class ScoringPeriodResult(FantraxBaseObject):
    """Represents a single Scoring Period.

    Attributes:
        league (League): The League instance this object belongs to.
        playoffs (bool): This Scoring Period is Playoffs.
        name (str): Name.
        period (ScoringPeriod): Scoring Period object for this result.
        start (date): Start Date of the Period.
        end (date): End Date of the Period.
        next (date): Next Day after the Period.
        days (int): Number of Days in the Scoring Period.
        complete (bool): Is the Period Complete?
        current (bool): Is it the current Period?
        future (bool): Is the Period in the future?
        matchups (list[Matchup]): List of Matchups.
        other_brackets (dict[str, Matchup]): Dictionary of Matchups in Other Brackets.
        title (str): Title of the Period.

    """

    def __init__(self, league: "League", data: dict, other_data: list[tuple[str, dict]] = None) -> None:
        super().__init__(league, data)
        self.name: str = self._data["caption"]

        self.playoffs: bool = self.name.startswith("Playoffs")
        dates = self._data["subCaption"][1:-1].split(" - ")
        self.start: date = datetime.strptime(dates[0], "%a %b %d, %Y").date()
        self.end: date = datetime.strptime(dates[1], "%a %b %d, %Y").date()

        if self.playoffs:
            self.period: ScoringPeriod = self.league.scoring_periods_lookup[self.range]
        else:
            self.period: ScoringPeriod = self.league.scoring_periods[int(re.search(r"(\d+)$", self.name).group())]

        self.next: date = self.end + timedelta(days=1)
        self.days: int = (self.next - self.start).days
        now = datetime.today().date()
        self.complete: bool = now > self.next
        self.current: bool = self.start < now < self.next
        self.future: bool = now < self.start
        self.matchups: list[Matchup] = [Matchup(self, i, matchup["cells"]) for i, matchup in enumerate(data["rows"], 1)]
        self.other_brackets: dict[str, list[Matchup]] = {}
        if other_data:
            for name, obj in other_data:
                for i, matchup in enumerate(obj["rows"], len(self.matchups) + 1):
                    if name not in self.other_brackets:
                        self.other_brackets[name] = []
                    self.other_brackets[name].append(Matchup(self, i, matchup["cells"]))

    @property
    def range(self) -> str:
        return f"{self.start.strftime('%Y-%m-%d')} - {self.end.strftime('%Y-%m-%d')}"

    @property
    def title(self) -> str:
        return f"{'Playoff ' if self.playoffs else ''}Period {self.period.number}"

    def __str__(self) -> str:
        output = f"{self.name}\n{self.days} Days ({self.start.strftime('%a %b %d, %Y')} - {self.end.strftime('%a %b %d, %Y')})"
        output += f"\n{'Complete' if self.complete else 'Current' if self.current else 'Future'}"
        for matchup in self.matchups:
            output += f"\n{matchup}"
        for name, matchups in self.other_brackets.items():
            output += f"\n{name}"
            for matchup in matchups:
                output += f"\n{matchup}"
        return output


class Matchup(FantraxBaseObject):
    """Represents a single Matchup.

    Attributes:
        league (League): The League instance this object belongs to.
        scoring_period (ScoringPeriodResult): Scoring Period result this instance belongs to.
        matchup_key (int): Team ID.
        away (Team): Away Team.
        away_score (float): Away Team Score.
        home (Team): Home Team.
        home_score (float): Home Team Score.

    """

    def __init__(self, scoring_period: ScoringPeriodResult, matchup_key: int, data: dict) -> None:
        super().__init__(scoring_period.league, data)
        self.scoring_period: ScoringPeriodResult = scoring_period
        self.matchup_key: int = matchup_key
        try:
            self.away: Team | str = self.league.team(self._data[0]["teamId"])
        except NotTeamInLeague:
            self.away: Team | str = self._data[0]["content"]
        self._away_score: Decimal = Decimal(str(self._data[1]["content"]).replace(",", ""))
        try:
            self.home: Team | str = self.league.team(self._data[2]["teamId"])
        except NotTeamInLeague:
            self.home: Team | str = self._data[2]["content"]
        self._home_score: Decimal = Decimal(str(self._data[3]["content"]).replace(",", ""))

    @property
    def away_score(self) -> float:
        return float(self._away_score)

    @property
    def home_score(self) -> float:
        return float(self._home_score)

    def winner(self) -> tuple[Team | str, float, Team | str, float] | tuple[None, None, None, None]:
        if self.away_score > self.home_score:
            return self.away, self.away_score, self.home, self.home_score
        elif self.away_score < self.home_score:
            return self.home, self.home_score, self.away, self.away_score
        else:
            return None, None, None, None

    def difference(self) -> float:
        if self.away_score > self.home_score:
            return float(self._away_score - self._home_score)
        elif self.away_score < self.home_score:
            return float(self._home_score - self._away_score)
        else:
            return 0.0

    def __str__(self) -> str:
        if self.away_score or self.home_score:
            winner, winner_score, loser, loser_score = self.winner()
            return f"{self.scoring_period.title} {winner} ({winner_score}) vs {loser} ({loser_score})"
        else:
            return f"{self.scoring_period.title} {self.away} vs {self.home}"
