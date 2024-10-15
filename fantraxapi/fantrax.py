import logging
from typing import Optional, Union, List, Dict
from requests import Session
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from fantraxapi.exceptions import FantraxException, Unauthorized
from fantraxapi.objs import ScoringPeriod, Team, Standings, Trade, TradeBlock, Position, Transaction, Roster

logger = logging.getLogger(__name__)



class FantraxAPI:
    """ Main Object Class

        Parameters:
            league_id (str): Fantrax League ID.
            session (Optional[Session]): Use you're own Session object

        Attributes:
            league_id (str): Fantrax League ID.
            teams (List[:class:`~Team`]): List of Teams in the League.
    """
    def __init__(self, league_id: str, session: Optional[Session] = None):
        self.league_id = league_id
        self._session = Session() if session is None else session
        self._teams = None
        self._positions = None

    @property
    def teams(self) -> List[Team]:
        if self._teams is None:
            response = self._request("getFantasyTeams")
            self._teams = []
            for data in response["fantasyTeams"]:
                self._teams.append(Team(self, data["id"], data["name"], data["shortName"], data["logoUrl256"]))
        return self._teams

    @property
    def positions(self) -> Dict[str, Position]:
        if self._positions is None:
            self._positions = {k: Position(self, v) for k, v in self._request("getRefObject", type="Position")["allObjs"].items()}
        return self._positions

    def team(self, team_id: str) -> Team:
        """ :class:`~Team` Object for the given Team ID.

            Parameters:
                team_id (str): Team ID.

            Returns:
                :class:`~Team`

            Raises:
                :class:`FantraxException`: When an Invalid Team ID is provided.
        """
        for team in self.teams:
            if team.team_id == team_id:
                return team
        raise FantraxException(f"Team ID: {team_id} not found")

    def _request(self, method, **kwargs):
        data = {"leagueId": self.league_id}
        for key, value in kwargs.items():
            data[key] = value
        json_data = {"msgs": [{"method": method, "data": data}]}
        logger.debug(f"Request JSON: {json_data}")

        try:
            response = self._session.post("https://www.fantrax.com/fxpa/req", params={"leagueId": self.league_id}, json=json_data)
            response_json = response.json()
        except (RequestException, JSONDecodeError) as e:
            raise FantraxException(f"Failed to Connect to {method}: {e}\nData: {data}")
        logger.debug(f"Response ({response.status_code} [{response.reason}]) {response_json}")
        if response.status_code >= 400:
            raise FantraxException(f"({response.status_code} [{response.reason}]) {response_json}")
        if "pageError" in response_json:
            if "code" in response_json["pageError"]:
                if response_json["pageError"]["code"] == "WARNING_NOT_LOGGED_IN":
                    raise Unauthorized("Unauthorized: Not Logged in")
            raise FantraxException(f"Error: {response_json}")
        return response_json["responses"][0]["data"]

    def scoring_periods(self) -> Dict[int, ScoringPeriod]:
        """ :class:`~ScoringPeriod` Objects for the league.

            Returns:
                Dict[int, :class:`~ScoringPeriod`]
        """
        periods = {}
        response = self._request("getStandings", view="SCHEDULE")
        self._teams = []
        for team_id, data in response["fantasyTeamInfo"].items():
            self._teams.append(Team(self, team_id, data["name"], data["shortName"], data["logoUrl512"]))
        for period_data in response["tableList"]:
            period = ScoringPeriod(self, period_data)
            periods[period.week] = period
        return periods

    def standings(self, week: Optional[Union[int, str]] = None) -> Standings:
        """ :class:`~Standings` Object for either the current moment in time or after a specific week..

            Parameters:
                week (Optional[Union[int, str]]): Pulls data for the Standings at the given week.

            Returns:
                :class:`~Standings`
        """
        if week is None:
            response = self._request("getStandings")
        else:
            response = self._request("getStandings", period=week, timeframeType="BY_PERIOD", timeStartType="FROM_SEASON_START")

        self._teams = []
        for team_id, data in response["fantasyTeamInfo"].items():
            self._teams.append(Team(self, team_id, data["name"], data["shortName"], data["logoUrl512"]))
        return Standings(self, response["tableList"][0]["rows"], week=week)

    def pending_trades(self) -> List[Trade]:
        response = self._request("getPendingTransactions")
        trades = []
        if "tradeInfoList" in response:
            for trade in response["tradeInfoList"]:
                trades.append(Trade(self, trade))
        return trades

    def trade_block(self):
        return [TradeBlock(self, block) for block in self._request("getTradeBlocks")["tradeBlocks"] if len(block) > 2]

    def transactions(self, count=100) -> List[Transaction]:
        response = self._request("getTransactionDetailsHistory", maxResultsPerPage=str(count))
        transactions = []
        update = False
        for row in response["table"]["rows"]:
            if update:
                transaction.update(row) # noqa
                update = False
            else:
                transaction = Transaction(self, row)
            if transaction.count > 1 and not transaction.finalized:
                update = True
            else:
                transactions.append(transaction)
        return transactions

    def max_goalie_games_this_week(self) -> int:
        response = self._request("getTeamRosterInfo", teamId=self.teams[0].team_id, view="GAMES_PER_POS")
        for maxes in response["gamePlayedPerPosData"]["tableData"]:
            if maxes["pos"] == "NHL Team Goalies (TmG)":
                return int(maxes["max"])

    def playoffs(self) -> Dict[int, ScoringPeriod]:
        response = self._request("getStandings", view="PLAYOFFS")
        other_brackets = {}
        for tab in response["displayedLists"]["tabs"]:
            if tab["id"].startswith("."):
                other_brackets[tab["name"]] = tab["id"]

        playoff_periods = {}
        for obj in response["tableList"]:
            if obj["caption"] == "Standings":
                continue
            period = ScoringPeriod(self, obj)
            playoff_periods[period.week] = period

        for name, bracket_id in other_brackets.items():
            response = self._request("getStandings", view=bracket_id)
            for obj in response["tableList"]:
                if obj["caption"] == "Standings":
                    continue
                playoff_periods[int(obj["caption"][17:])].add_matchups(obj)

        return playoff_periods

    def roster_info(self, team_id):
        return Roster(self, self._request("getTeamRosterInfo", teamId=team_id), team_id)