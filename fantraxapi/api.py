from datetime import date
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, ParamSpec

from requests import Session

from fantraxapi import FantraxException
from fantraxapi.exceptions import NotLoggedIn, NotMemberOfLeague

if TYPE_CHECKING:
    from fantraxapi.objs import League


Param: ParamSpec = ParamSpec("Param")
default_session: Session = Session()

debug: bool = False


class Method:
    def __init__(self, name: str, **kwargs: Param.kwargs) -> None:
        self.name: str = name
        self.kwargs: dict = kwargs
        self.response: dict | None = None

    def msg_block(self, league_id: str) -> dict[str, str]:
        output_data = {"leagueId": league_id}
        for key, value in self.kwargs.items():
            if value is not None:
                if isinstance(value, date):
                    output_data[key] = value.strftime("%Y-%m-%d")
                else:
                    output_data[key] = str(value)
        return {"method": self.name, "data": output_data}


def request(league: "League", methods: list[Method] | Method) -> dict:
    return _request(league.league_id, methods, session=league.session)


def _request(league_id: str, methods: list[Method] | Method, session: Session | None = None) -> list[dict] | dict:
    if not isinstance(methods, list):
        methods = [methods]
    json_data = {"msgs": [m.msg_block(league_id) for m in methods]}
    if session is None:
        session = default_session
    if debug:
        print(f"{'_' * 100} Request JSON  {'_' * 100}")
        print(json_data)
    response = session.post("https://www.fantrax.com/fxpa/req", params={"leagueId": league_id}, json=json_data)
    try:
        response_json = response.json()
    except JSONDecodeError as e:
        raise FantraxException(f"Invalid JSON Response to {methods}: {e}\nData: {json_data}")
    if debug:
        print(f"{'-' * 100} Response JSON {'-' * 100}")
        print("-" * 100)
        print(response_json)
        print("^" * 215)
    if response.status_code >= 400:
        raise FantraxException(f"({response.status_code} [{response.reason}]) {response_json}")
    if "pageError" in response_json:
        if "code" in response_json["pageError"]:
            match response_json["pageError"]["code"]:
                case "WARNING_NOT_LOGGED_IN":
                    raise NotLoggedIn("Not Logged in")
                case "NOT_MEMBER_OF_LEAGUE":
                    raise NotMemberOfLeague("Not Member of League")
                case "UNEXPECTED_ERROR":
                    raise FantraxException(f"{response_json['pageError']['title']}")
                case _:
                    raise FantraxException(f"{response_json}")

    return response_json["responses"][0]["data"] if len(methods) == 1 else [r["data"] for r in response_json["responses"]]


def get_init_info(league: "League") -> dict:
    return request(
        league,
        [
            Method("getFantasyLeagueInfo"),
            Method("getRefObject", type="FantasyItemStatus"),
            Method("getLiveScoringStats", newView=True),
            Method("getTeamRosterInfo", view="GAMES_PER_POS"),
            Method("getTeamRosterInfo", view="STATS"),
        ],
    )


def get_pending_transactions(league: "League") -> dict:
    return request(league, Method("getPendingTransactions"))


def get_standings(league: "League", views: list[str] | str | None = None, **kwargs: Param.kwargs) -> dict:
    if "view" in kwargs and views is None:
        views = kwargs.pop("view")
    if "view" in kwargs:
        del kwargs["view"]
    if not isinstance(views, list):
        views = [views]
    response = request(league, [Method("getStandings", view=v, **kwargs) for v in views])
    responses = response if isinstance(response, list) else [response]
    for res in responses:
        if "fantasyTeamInfo" in res:
            league._update_teams(res["fantasyTeamInfo"])
    return response


def get_trade_blocks(league: "League") -> dict:
    return request(league, Method("getTradeBlocks"))["tradeBlocks"]


def get_team_roster_position_counts(league: "League", team_id: str, scoring_period_number: int | None = None) -> dict:
    response = request(league, Method("getTeamRosterInfo", teamId=team_id, scoringPeriod=scoring_period_number, view="GAMES_PER_POS"))
    league._update_teams(response["fantasyTeams"])
    return response


def get_team_roster_info(league: "League", team_id: str, period_number: int | None = None) -> dict:
    responses = request(
        league,
        [
            Method("getTeamRosterInfo", teamId=team_id, period=period_number, view="STATS"),
            Method("getTeamRosterInfo", teamId=team_id, period=period_number, view="SCHEDULE_FULL"),
        ],
    )
    league._update_teams(responses[0]["fantasyTeams"])
    return responses


def get_transaction_history(league: "League", per_page_results: int = 100) -> dict:
    return request(league, Method("getTransactionDetailsHistory", maxResultsPerPage=str(per_page_results)))


def get_live_scoring_stats(league: "League", scoring_date: date | None = None) -> dict:
    return request(league, Method("getLiveScoringStats", date=scoring_date, newView=True, period="1", playerViewType="1", sppId="-1", viewType="1"))
