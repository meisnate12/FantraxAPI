from typing import TYPE_CHECKING, Self

from .base import FantraxBaseObject

if TYPE_CHECKING:
    from .league import League


class Status(FantraxBaseObject):
    """Represents a single Status.

    Attributes:
        league (League): The League instance this object belongs to.
        id (str): Status ID.
        code (str): Status code.
        name (str): Status name.
        short_name (str): Status short name.
        description (str): Status description.

    """

    def __init__(self, league: "League", data: dict) -> None:
        super().__init__(league, data)
        self.id: str = self._data["id"]
        self.code: str = self._data["code"]
        self.name: str = self._data["name"]
        self.short_name: str = self._data["shortName"]
        self.description: str = self._data["description"]

    def __eq__(self, other: Self) -> bool:
        return (self.id, self.name, self.short_name) == (other.id, other.name, other.short_name)

    def __str__(self) -> str:
        return f"[{self.id}:{self.name}]"
