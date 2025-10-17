from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fantraxapi import League


class FantraxBaseObject:
    def __init__(self, league: "League", data: dict | list[dict]) -> None:
        self.league: "League" = league
        self._data: dict | list[dict] = data

    def __repr__(self) -> str:
        return self.__str__()
