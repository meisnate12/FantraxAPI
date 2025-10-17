from datetime import date, datetime, time
from typing import TYPE_CHECKING, Self

from ..exceptions import DateNotInSeason
from .base import FantraxBaseObject
from .player import Player

if TYPE_CHECKING:
    from .league import League


class Game(FantraxBaseObject):
    """Represents a single Game.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Game ID.
        player (Player): Player to view this game from.
        date (date): The date this game is played.
        opponent (str): NHL Short Name of the opponent.
        time (time): Time of the game start if it hasn't been played yet.
        home (bool): Is Player Home?
        away (bool): Is Player Away?

    """

    def __init__(self, league: "League", player: Player, game_date: str, data: dict) -> None:
        super().__init__(league, data)
        self.id: str = self._data["eventId"]
        self.player: Player = player
        start = datetime.strptime(f"{game_date} {self.league.start_date.year}", "%a %m/%d %Y").date()
        end = datetime.strptime(f"{game_date} {self.league.end_date.year}", "%a %m/%d %Y").date()
        league_start = self.league.start_date.date()
        league_end = self.league.end_date.date()
        if league_end >= start >= league_start:
            self.date: date = start
        elif league_end >= end >= league_start:
            self.date: date = end
        else:
            raise DateNotInSeason(game_date)

        self.time: time | None = None
        parts = data["content"].removesuffix(" F").split("\u003cbr/\u003e")
        if ":" in parts[1]:
            self.opponent: str = parts[0]
            if self.opponent.startswith("@"):
                self.opponent = self.opponent[1:]
                home = self.player.team_short_name
            else:
                home = self.opponent

            self.time = datetime.strptime(parts[1].split(" ")[1], "%I:%M%p").time()
        else:
            home = "".join(i for i in parts[0] if not i.isdigit() and i not in [" ", "@"])
            away = "".join(i for i in parts[1] if not i.isdigit() and i not in [" ", "@"])
            self.opponent = away if home == self.player.team_short_name else home
        self.home: bool = home == self.player.team_short_name
        self.away: bool = home != self.player.team_short_name

    def __eq__(self, other: Self) -> bool:
        return self.id == other.id

    def __str__(self) -> str:
        return f"[{self.id}:{f'{self.opponent} @{self.player.team_short_name}' if self.home else f'{self.player.team_short_name} @{self.opponent}'}{f' {self.time}' if self.time else ''}]"
