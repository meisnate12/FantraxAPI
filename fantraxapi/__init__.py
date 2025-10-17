import importlib.metadata

from .exceptions import FantraxException, NotLoggedIn, NotMemberOfLeague, NotTeamInLeague
from .objs import League
from .objs import League as FantraxAPI

try:
    __version__ = importlib.metadata.version("fantraxapi")
except importlib.metadata.PackageNotFoundError:
    __version__ = ""
__author__ = "Nathan Taggart"
__credits__ = "meisnate12"
__package_name__ = "fantraxapi"
__project_name__ = "FantraxAPI"
__description__ = "A lightweight Python library for The Fantrax API."
__url__ = "https://github.com/meisnate12/FantraxAPI"
__email__ = "meisnate12@gmail.com"
__license__ = "MIT License"
__all__ = [
    "FantraxAPI",
    "FantraxException",
    "NotLoggedIn",
    "NotMemberOfLeague",
    "NotTeamInLeague",
    "League",
]
