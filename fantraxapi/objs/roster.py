from datetime import date
from typing import TYPE_CHECKING

from .base import FantraxBaseObject
from .game import Game
from .player import Player
from .position import Position

if TYPE_CHECKING:
    from .league import League
    from .team import Team


class Roster(FantraxBaseObject):
    """Represents a Player's Roster.

    Attributes:
        league (League): The League instance this object belongs to.
        team (Team): Team who made te Transaction.
        period_number (int): Daily Period Number.
        period_date (date): Daily Period Date.
        active (int): Number of Players in Active Slots.
        active_max (int): Max Number of Players that can be in Active Slots.
        reserve (int): Number of Players in Reserve Slots.
        reserve_max (int): Max Number of Players that can be in Reserve Slots.
        injured (int): Number of Players in Injured Slots.
        injured_max (int): Max Number of Players that can be in Injured Slots.
        rows (list[RosterRow]): List of RosterRows in the Roster.

    """

    def __init__(self, league: "League", team_id: str, data: dict) -> None:
        super().__init__(league, data[0])
        self.team: Team = self.league.team(team_id)
        self.period_number: int = int(self._data["displayedSelections"]["displayedPeriod"])
        self.period_date: date = self.league.scoring_dates[self.period_number]
        lookup: dict[str, dict] = {d["name"]: d for d in self._data["miscData"]["statusTotals"]}
        self.active: int = int(lookup["Active"]["total"]) if "Active" in lookup else 0
        self.active_max: int = int(lookup["Active"]["max"]) if "Active" in lookup else 0
        self.reserve: int = int(lookup["Reserve"]["total"]) if "Reserve" in lookup else 0
        self.reserve_max: int = int(lookup["Reserve"]["max"]) if "Reserve" in lookup else 0
        self.injured: int = int(lookup["Inj Res"]["total"]) if "Inj Res" in lookup else 0
        self.injured_max: int = int(lookup["Inj Res"]["max"]) if "Inj Res" in lookup else 0
        self.rows = []
        for stats_group, schedule_group in zip(self._data["tables"], data[1]["tables"]):
            stats_header = stats_group["header"]["cells"]
            schedule_header = schedule_group["header"]["cells"]
            for stats_row, schedule_row in zip(stats_group["rows"], schedule_group["rows"]):
                if "posId" not in stats_row:
                    continue
                stuff = {"posId": stats_row["posId"], "future_games": {}, "total_fantasy_points": None, "fantasy_points_per_game": None}
                if "scorer" in stats_row or stats_row["statusId"] == "1":
                    if "scorer" in stats_row:
                        stuff["scorer"] = stats_row["scorer"]
                        for header, cell in zip(schedule_header, schedule_row["cells"]):
                            if cell["content"] and "eventStr" in header and header["eventStr"]:
                                key = header["shortName"]
                                stuff["future_games"][key] = cell

                        for header, cell in zip(stats_header, stats_row["cells"]):
                            if "sortKey" in header:
                                match header["sortKey"]:
                                    case "SCORE":
                                        stuff["total_fantasy_points"] = float(cell["content"])
                                    case "FPTS_PER_GAME":
                                        stuff["fantasy_points_per_game"] = float(cell["content"])
                            if cell["content"] and "eventStr" in header and header["eventStr"]:
                                stuff["game_today"] = cell
                self.rows.append(RosterRow(self, stuff))

    def __str__(self) -> str:
        rows = "\n".join([str(r) for r in self.rows])
        return f"{self.team} Roster\n{rows}"


class RosterRow(FantraxBaseObject):
    """Represents a single Row on a Player's Roster.

    Attributes:
        league (League): The League instance this object belongs to.
        roster (Roster): The Roster instance this RosterRow belongs to.
        position (Position): The Position object associated with the RosterRow.
        player (Player | None): The Player in the RosterRow.
        total_fantasy_points (float | None): The Total Fantasy Points for the Player in the RosterRow.
        fantasy_points_per_game (float | None): The Fantasy Points Per Game for the Player in the RosterRow.
        game_today (Game): Game for the Player in the RosterRow.
        future_games (dict[str, Game]): Dictionary of dates to future Games or the last game of the season if it's over.

    """

    def __init__(self, roster: Roster, data: dict) -> None:
        super().__init__(roster.league, data)
        self.roster: Roster = roster
        self.position: Position = self.league.positions[self._data["posId"]]
        self.player: Player | None = Player(self.league, self._data["scorer"]) if "scorer" in self._data else None
        self.total_fantasy_points: float | None = self._data["total_fantasy_points"]
        self.fantasy_points_per_game: float | None = self._data["fantasy_points_per_game"]
        self.game_today: Game | None = Game(self.league, self.player, roster.period_date.strftime("%a %m/%d"), self._data["game_today"]) if "game_today" in self._data else None
        self.future_games: dict[str, Game] = {k: Game(self.league, self.player, k, v) for k, v in self._data["future_games"].items()}

    def __str__(self) -> str:
        return f"{self.position.short_name}: {self.player if self.player else 'Empty'}"
