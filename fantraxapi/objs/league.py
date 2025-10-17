import re
from datetime import date, datetime
from typing import ParamSpec

from requests import Session

from fantraxapi import NotLoggedIn, NotTeamInLeague, api

from ..exceptions import DateNotInSeason, PeriodNotInSeason
from .player import Player
from .position import Position, PositionCount
from .roster import Roster
from .scoring_period import ScoringPeriod, ScoringPeriodResult
from .standings import Standings
from .status import Status
from .team import Team
from .trade import Trade
from .trade_block import TradeBlock
from .transaction import Transaction

Param = ParamSpec("Param")


class League:
    """League Class to represent a Fantrax League.

    Args:
        league_id (str): Fantrax League ID.
        session (Session | None): Custom Session object.

    Attributes:
        league_id (str): Fantrax League ID.
        session (Session): Request Session Object.
        logged_in (bool): True when there's a logged-in User.
        name (str): Name of the League.
        year (str): Year of the League.
        start_date (datetime): Start date of the League.
        end_date (datetime): End date of the League.
        positions (dict[str, Position]): Dictionary of Position ID to Positions.
        status (dict[str, Status]): Dictionary of Status ID to Status.
        scoring_periods (dict[int, ScoringPeriod]): Dictionary of Scoring Period Number to ScoringPeriod.
        scoring_periods_lookup (dict[str, ScoringPeriod]): Dictionary of Scoring Period Range (%Y/%m/%d-%Y/%m/%d) to ScoringPeriod.
        scoring_dates (dict[int, date]): Dictionary of daily period numbers to dates that have scoring in this season.
        teams (list[Team]): List of Teams in the League.
        team_lookup (dict[str, Team]): Dictionary of Team IDs to Teams.
    """

    def __init__(self, league_id: str, session: Session | None = None) -> None:
        self.league_id: str = league_id
        self.logged_in: bool = False
        self.session: Session = Session() if session is None else session
        self.name: str = ""
        self.year: str = ""
        self.start_date: datetime | None = None
        self.end_date: datetime | None = None
        self.positions: dict[str, Position] = {}
        self.status: dict[str, Status] = {}
        self.scoring_periods: dict[int, ScoringPeriod] = {}
        self._scoring_periods_lookup: dict[str, ScoringPeriod] | None = None
        self.scoring_dates: dict[int, date] = {}
        self._teams: list[Team] | None = None
        self._team_lookup: dict[str, Team] | None = None
        self.reset_info()

    def reset_info(self) -> None:
        responses = api.get_init_info(self)
        self.name = responses[0]["fantasySettings"]["leagueName"]
        self.year = responses[0]["fantasySettings"]["subtitle"]
        self.start_date = datetime.fromtimestamp(responses[0]["fantasySettings"]["season"]["startDate"] / 1e3)
        self.end_date = datetime.fromtimestamp(responses[0]["fantasySettings"]["season"]["endDate"] / 1e3)
        self.positions = {k: Position(self, v) for k, v in responses[0]["positionMap"].items()}
        self.status = {k: Status(self, v) for k, v in responses[1]["allObjs"].items() if "name" in v}
        period_to_day_list = {}
        for s in responses[4]["displayedLists"]["periodList"]:
            period, s = s.split(" ", maxsplit=1)
            period_to_day_list[s[5:-1]] = int(period)
        self.scoring_dates = {}
        for day in responses[2]["dates"]:
            scoring_date = datetime.strptime(day["object1"], "%Y-%m-%d").date()
            key = scoring_date.strftime("%b %d")
            if "0" in key and not key.endswith("0"):
                key = key.replace("0", "")
            self.scoring_dates[period_to_day_list[key]] = scoring_date
        self.scoring_periods = {p["value"]: ScoringPeriod(self, p) for p in responses[3]["displayedLists"]["scoringPeriodList"] if p["name"] != "Full Season"}
        self._scoring_periods_lookup = None
        self._update_teams(responses[3]["fantasyTeams"])

    def _update_teams(self, team_data: dict | list) -> None:
        if isinstance(team_data, list):
            team_data = {data["id"]: data for data in team_data}
        self.teams = [Team(self, team_id, data) for team_id, data in team_data.items()]
        self._team_lookup = None

    @property
    def team_lookup(self) -> dict[str, Team]:
        if self._team_lookup is None:
            self._team_lookup = {t.id: t for t in self.teams}
        return self._team_lookup

    @property
    def scoring_periods_lookup(self) -> dict[str, ScoringPeriod]:
        if self._scoring_periods_lookup is None:
            self._scoring_periods_lookup = {v.range: v for k, v in self.scoring_periods.items()}
        return self._scoring_periods_lookup

    def team(self, team_identifier: str) -> Team:
        """Return a Team object for the given Team ID or where the Team name contains the given value.

        Args:
            team_identifier (str): Team identifier.

        Returns:
            Team: Team object that corresponds with the provided team identifier.

        Raises:
            NotTeamInLeague: When the team identifier provided is not found to be associated with any team in the League.

        """
        if team_identifier in self.team_lookup:
            return self.team_lookup[team_identifier]
        if t := next((t for t in self.teams if team_identifier.lower() in t.name.lower()), None):
            return t
        raise NotTeamInLeague(f"Team Identifier: {team_identifier} not found in League: {self.name}")

    def scoring_period_results(self, season: bool = True, playoffs: bool = True) -> dict[int, ScoringPeriodResult]:
        """Returns Season ScoringPeriodResult objects for the league.

        Args:
            season (bool): Return season Scoring Periods Results for this season.
            playoffs (bool): Return playoff Scoring Periods Results for this season.

        Returns:
            dict[int, ScoringPeriodResult]: Dictionary of Period Number to ScoringPeriodResult object.

        """
        periods = {}
        response = api.get_standings(self, view="SCHEDULE")

        if season:
            for scoring_period_data in response["tableList"]:
                scoring_period = ScoringPeriodResult(self, scoring_period_data)
                periods[scoring_period.period.number] = scoring_period

        if playoffs:
            playoff_responses = api.get_standings(self, views=["PLAYOFFS"] + [tab["id"] for tab in response["displayedLists"]["tabs"] if tab["id"].startswith(".")])

            other_data = {}
            for bracket_response in playoff_responses[1:]:
                other_id = bracket_response["displayedSelections"]["view"]
                name = next((tab["name"] for tab in bracket_response["displayedLists"]["tabs"] if tab["id"] == other_id), None)
                for obj in bracket_response["tableList"]:
                    if obj["caption"] == "Standings":
                        continue
                    playoff_number = int(re.search(r"(\d+)$", obj["caption"]).group())
                    if playoff_number not in other_data:
                        other_data[playoff_number] = []
                    other_data[playoff_number].append((name, obj))

            for obj in reversed(playoff_responses[0]["tableList"]):
                if obj["caption"] == "Standings":
                    continue
                playoff_number = int(re.search(r"(\d+)$", obj["caption"]).group())
                scoring_period = ScoringPeriodResult(self, obj, other_data=other_data[playoff_number] if playoff_number in other_data else None)
                periods[scoring_period.period.number] = scoring_period

        return periods

    def standings(self, scoring_period_number: int | None = None, only_period: bool = False) -> Standings:
        """Returns Standings object that represents either the standings after a period or the latest period's standings when scoring_period_number is None.

        Args:
            scoring_period_number (int | None): Period number, defaults to None.
            only_period (bool): Only that specific period's standings, defaults to False.

        Returns:
            Standings: Standings object that corresponds with the period standing.

        """
        kwargs = {}
        if scoring_period_number is not None:
            kwargs["period"] = scoring_period_number
            kwargs["timeframeType"] = "BY_PERIOD"
            kwargs["timeStartType"] = "PERIOD_ONLY" if only_period else "FROM_SEASON_START"
        response = api.get_standings(self, **kwargs)
        return Standings(self, response["tableList"][0], scoring_period_number=scoring_period_number)

    def pending_trades(self) -> list[Trade]:
        """Returns a list of Trade objects that represent pending trades.

        Returns:
            list[Trade]: List of Trade objects that represent pending trades.

        Raises:
            NotLoggedIn: When there is no logged-in User in the Session object.
        """
        if not self.logged_in:
            self.trade_block()
        response = api.get_pending_transactions(self)
        trades = []
        if "tradeInfoList" in response:
            for trade in response["tradeInfoList"]:
                trades.append(Trade(self, trade))
        return trades

    def trade_block(self) -> list[TradeBlock]:
        """Returns a list of TradeBlock objects that represent each Trade Block.

        Returns:
            list[TradeBlock]: List of TradeBlock objects that represent each Trade Block.

        Raises:
            NotLoggedIn: When there is no logged-in User in the Session object.
        """
        try:
            response = [TradeBlock(self, block) for block in api.get_trade_blocks(self) if len(block) > 2]
            self.logged_in = True
            return response
        except NotLoggedIn:
            self.logged_in = False
            raise

    def transactions(self, count: int = 100) -> list[Transaction]:
        """Returns a list of Transaction objects that represent the latest transactions.

        Args:
            count (int): Number of transactions to return, defaults to 100.

        Returns:
            list[Transaction]: List of Transaction objects that represent the latest transactions.

        """
        response = api.get_transaction_history(self, per_page_results=count)
        transactions = []
        transaction_data = []
        for row in response["table"]["rows"]:
            if transaction_data and row["txSetId"] != transaction_data[0]["txSetId"]:
                transactions.append(Transaction(self, transaction_data))
                transaction_data = []
            transaction_data.append(row)
        if transaction_data:
            transactions.append(Transaction(self, transaction_data))
        return transactions

    def position_counts(self, team_id: str, scoring_period_number: int | None = None) -> dict[str, PositionCount]:
        """Returns a Dictionary of PositionCount objects that represents the positions used for a given Team ID for a specific period or the latest period's standings when scoring_period_number is None.

        Args:
            team_id (str): Team ID to get positions for.
            scoring_period_number (int | None): Period Number, defaults to None.

        Returns:
            dict[str, PositionCount]: Dictionary of Position Short Names to PositionCount objects.

        Raises:
            PeriodNotInSeason: When the period_number is not in the Season

        """
        if scoring_period_number is not None and scoring_period_number not in self.scoring_periods:
            raise PeriodNotInSeason(scoring_period_number)
        response = api.get_team_roster_position_counts(self, team_id, scoring_period_number=scoring_period_number)
        return {p["posShort"]: PositionCount(self, p) for p in response["gamePlayedPerPosData"]["tableData"]}

    def live_scores(self, scoring_date: date) -> dict[str, list[Player]]:
        """Returns a Dictionary of Team IDs to a list of Player objects with scores for that day.

        Args:
            scoring_date (date): Date of the Live Scoring.

        Returns:
            dict[str, list[Player]]: Dictionary of Team IDs to a list of Player objects with scores for that day.

        Raises:
            DateNotInSeason: When the scoring_date is not in the Season.

        """
        if scoring_date not in self.scoring_dates.values():
            raise DateNotInSeason(scoring_date)
        response = api.get_live_scoring_stats(self, scoring_date=scoring_date)
        scorer_map = {}
        for _, data in response["scorerMap"].items():
            for _, data2 in data.items():
                for _, data3 in data2.items():
                    for player in data3:
                        if player["scorer"]["scorerId"] not in scorer_map:
                            scorer_map[player["scorer"]["scorerId"]] = Player(self, player["scorer"])
        active_teams = []
        for matchup in response["matchups"]:
            team1, team2 = matchup.split("_")
            active_teams.append(team1)
            active_teams.append(team2)
        final_scores = {}
        for team_id, data in response["statsPerTeam"]["allTeamsStats"].items():
            if team_id not in active_teams:
                continue
            if team_id not in final_scores:
                final_scores[team_id] = []
            for scorer_id, pts in data["ACTIVE"]["statsMap"].items():
                if not scorer_id.startswith("_"):
                    player = scorer_map[scorer_id]
                    player.update_points(team_id, pts["object1"], scoring_date)
                    final_scores[team_id].append(player)
        return final_scores

    def team_roster(self, team_id: str, period_number: int | None = None) -> Roster:
        """Returns a Roster object that represents the given Team ID's roster for a specific period or the latest period's standings when number is None.

        Args:
            team_id (str): Team ID.
            period_number (int | None): Daily Period Number, defaults to None.

        Returns:
            Roster: Roster object that represent the given Team ID's roster.

        Raises:
            PeriodNotInSeason: When the period_number is not in the Season

        """
        if period_number is not None and period_number not in self.scoring_dates:
            raise PeriodNotInSeason(period_number)
        return Roster(self, team_id, api.get_team_roster_info(self, team_id, period_number=period_number))
