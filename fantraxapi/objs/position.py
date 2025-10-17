from typing import TYPE_CHECKING, Self

from .base import FantraxBaseObject

if TYPE_CHECKING:
    from .league import League


class Position(FantraxBaseObject):
    """Represents a single Position.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Position ID.
        name (str): Position Name.
        short_name (str): Position Short Name.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        self.id: str = self._data["id"]
        self.name: str = self._data["name"]
        self.short_name: str = self._data["shortName"]

    def __eq__(self, other: Self) -> bool:
        return (self.id, self.name, self.short_name) == (other.id, other.name, other.short_name)

    def __str__(self) -> str:
        return f"[{self.id}:{self.name}:{self.short_name}]"


class PositionCount(FantraxBaseObject):
    """Represents a single Position min/max count for a period.

    Attributes:
        league (League): The League instance this object belongs to.
        min (int | None): Minimum number that have to be played.
        max (int | None): Maximum number that can be played.
        gp (int | None): Total games played.
        name (str): Position Name.
        short_name (str): Position Short Name.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        self.min: int | None = self._data["min"] if isinstance(self._data["min"], int) else None
        self.max: int | None = self._data["max"] if isinstance(self._data["max"], int) else None
        self.gp: int = int(self._data["gp"])
        self.name: str = self._data["pos"]
        self.short_name: str = self._data["posShort"]

    def __str__(self) -> str:
        return f"[{self.name}:{self.gp}{f':Min({self.min})' if self.min else ''}]{f':Max({self.max})' if self.max else ''}]"
