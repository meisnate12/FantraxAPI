import os, sys, time, unittest
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fantraxapi import FantraxAPI

"""
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""

load_dotenv()

league_id = os.environ["LEAGUE_ID"]
local = os.environ["LOCAL"] == "True"
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

team_names = [
    "Bunch of Yahoos",
    "Carry Me Ovi",
    "Dude Where’s Makar?",
    "Former Ice Dancers",
    "Girouxsalem",
    "High and Draisaitl",
    "Kashyyyk Wookies 🏴‍☠️",
    "Momma Ain't Raise No Bitch",
    "Rantanen With The Devil",
    "Sonk squad",
    "Tage Against The Machine",
    "Tease McBulge"
]

class APITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = FantraxAPI(league_id)

    def test_teams(self):
        for team in self.api.teams:
            self.assertIn(team.name, team_names)

