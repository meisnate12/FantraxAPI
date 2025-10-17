from datetime import date, datetime


class FantraxException(Exception):
    """Base class for all FantraxAPI exceptions."""

    pass


class DateNotInSeason(FantraxException):
    """Exception thrown when trying to query with a date not in the Season"""

    def __init__(self, error_date: str | date | datetime) -> None:
        super().__init__(f"Date: {error_date if isinstance(error_date, str) else error_date.strftime('%Y-%m-%d')} not in the Season.")


class NotLoggedIn(FantraxException):
    """Exception thrown when accessing a private endpoint without being Logged In"""

    pass


class NotMemberOfLeague(FantraxException):
    """Exception thrown when accessing an endpoint without being part of that League"""

    pass


class NotTeamInLeague(FantraxException):
    """Exception thrown when trying to query for a Team not part of that League"""

    pass


class PeriodNotInSeason(FantraxException):
    """Exception thrown when trying to query with a period not in the Season"""

    def __init__(self, error_date: str | int) -> None:
        super().__init__(f"Period: {error_date} not in the Season.")
