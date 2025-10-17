import os
import pickle
import sys
import time
import unittest
from datetime import date

from dotenv import load_dotenv
from requests import Session
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from fantraxapi import League, NotLoggedIn, NotTeamInLeague
from fantraxapi.exceptions import DateNotInSeason, FantraxException, NotMemberOfLeague, PeriodNotInSeason

"""
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""

load_dotenv()

league_id = os.environ["LEAGUE_ID"]
local = os.environ["LOCAL"] == "True"
username = os.environ["FANTRAX_USERNAME"]
password = os.environ["FANTRAX_PASSWORD"]
cookie_filepath = "fantraxloggedin.cookie"
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

team_names = [
    "Bunch of Yahoos",
    "Pirate Horde",
    "Dude Where’s Makar?",
    "Former Ice Dancers",
    "MacKstreet Boys",
    "Son of a Mich",
    "Kashyyyk Wookies 🏴‍☠️",
    "Momma Ain't Raise No Bitch",
    "Rantanen With The Devil",
    "Maple leaving in the first",
    "Team Will",
    "The Teasiest of McBulges",
]


def add_cookie_to_session(session: Session) -> None:
    if local and os.path.exists(cookie_filepath):
        with open(cookie_filepath, "rb") as f:
            for cookie in pickle.load(f):
                session.cookies.set(cookie["name"], cookie["value"])
    else:
        service = Service(ChromeDriverManager().install())

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1600")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")

        with webdriver.Chrome(service=service, options=options) as driver:
            driver.get("https://www.fantrax.com/login")
            username_box = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']")))
            username_box.send_keys(username)
            password_box = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@formcontrolname='password']")))
            password_box.send_keys(password)
            password_box.send_keys(Keys.ENTER)
            time.sleep(5)

            cookies = driver.get_cookies()
            if local:
                with open(cookie_filepath, "wb") as cookie_file:
                    pickle.dump(driver.get_cookies(), cookie_file)

            for cookie in cookies:
                session.cookies.set(cookie["name"], cookie["value"])


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.league = League(league_id)

    def test_info(self) -> None:
        self.assertRaises(FantraxException, League, "jdaffngkjfngjkdf")
        self.assertEqual(self.league.name, "Cowley's Chaos")
        self.assertEqual(self.league.year, "2024-25 NHL")

    def test_positions(self) -> None:
        self.assertIn("206", self.league.positions)
        self.assertEqual(self.league.positions["206"].name, "Center")

    def test_status(self) -> None:
        self.assertEqual(self.league.status["3"].name, "Inj Res")
        self.assertEqual(self.league.status["4"].code, "FREE_AGENT")

    def test_scoring_dates(self) -> None:
        self.assertEqual(len(self.league.scoring_dates), 178)
        values = self.league.scoring_dates.values()
        for day_date in [
            date(year=2024, month=10, day=4),
            date(year=2024, month=10, day=5),
            date(year=2024, month=10, day=8),
            date(year=2024, month=10, day=9),
            date(year=2025, month=4, day=16),
            date(year=2025, month=4, day=17),
        ]:
            self.assertIn(day_date, values)

        self.assertEqual(self.league.scoring_dates[77], date(year=2024, month=12, day=19))
        for day_date in [
            date(year=2024, month=10, day=2),
            date(year=2024, month=10, day=3),
            date(year=2024, month=10, day=6),
            date(year=2024, month=10, day=7),
            date(year=2025, month=4, day=18),
            date(year=2025, month=4, day=19),
        ]:
            self.assertNotIn(day_date, values)

    def test_scoring_periods(self) -> None:
        self.assertEqual(len(self.league.scoring_periods), 25)
        self.assertEqual(str(self.league.scoring_periods[3]), "[3:2024-10-21 - 2024-10-27]")
        self.assertNotEqual(self.league.scoring_periods[8], self.league.scoring_periods[12])
        self.assertEqual(self.league.scoring_periods[9], "9")
        self.assertEqual(self.league.scoring_periods[17], 17)
        self.assertEqual(self.league.scoring_periods[5].start, date(year=2024, month=11, day=4))
        self.assertEqual(self.league.scoring_periods[5].end, date(year=2024, month=11, day=10))
        self.assertEqual(self.league.scoring_periods[13].start, date(year=2024, month=12, day=30))
        self.assertEqual(self.league.scoring_periods[21].end, date(year=2025, month=3, day=16))

    def test_teams(self) -> None:
        for team in self.league.teams:
            self.assertIn(team.name, team_names)
        self.assertRaises(NotTeamInLeague, self.league.team, "NotAProperTeamID")
        self.assertEqual(self.league.team("wookie").name, "Kashyyyk Wookies 🏴‍☠️")

    def test_scoring_period_results(self) -> None:
        results = self.league.scoring_period_results()
        self.assertTrue(len(results) == 25)
        self.assertTrue(results[10].days == 7)
        self.assertTrue(results[19].days == 21)
        self.assertTrue(results[19].matchups[2].winner()[1] == 630.2)
        self.assertTrue(results[19].matchups[2].winner()[3] == 541.4)
        self.assertFalse(results[22].playoffs)
        self.assertTrue(results[23].playoffs)
        self.assertTrue(results[23].days == 7)
        self.assertTrue(results[25].playoffs)
        self.assertTrue(results[25].days == 11)
        self.assertTrue(results[25].matchups[0].winner()[1] == 762.2)
        self.assertTrue(results[25].matchups[0].winner()[3] == 685.5)
        self.assertTrue(str(results[21].matchups[3]) == "Period 21 Bunch of Yahoos (400.0) vs Kashyyyk Wookies 🏴‍☠️ (368.6)")
        self.assertTrue(results[21].matchups[2].difference() == 178.3)
        self.assertTrue(results[21].matchups[3].difference() == 31.4)
        self.assertEqual(
            str(results[25]),
            (
                "Playoffs - Round 3\n"
                "11 Days (Mon Apr 07, 2025 - Thu Apr 17, 2025)\n"
                "Complete\n"
                "Playoff Period 25 Bunch of Yahoos (762.2) vs The Teasiest of McBulges (685.5)\n"
                "3rd Place\n"
                "Playoff Period 25 Kashyyyk Wookies 🏴‍☠️ (835.9) vs Son of a Mich (778.6)\n"
                "7th Place\n"
                "Playoff Period 25 Pirate Horde (535.7) vs Dude Where’s Makar? (432.7)\n"
                "Toilet Bowl\n"
                "Playoff Period 25 MacKstreet Boys (668.9) vs Maple leaving in the first (597.8)"
            ),
        )

    def test_standings(self) -> None:
        standings = self.league.standings()

        self.assertEqual(
            str(standings),
            (
                "Standings\n"
                "1: Kashyyyk Wookies 🏴‍☠️ (18-4-0)\n"
                "2: Bunch of Yahoos (18-4-0)\n"
                "3: Son of a Mich (15-7-0)\n"
                "4: Maple leaving in the first (15-7-0)\n"
                "5: The Teasiest of McBulges (13-9-0)\n"
                "6: MacKstreet Boys (10-12-0)\n"
                "7: Dude Where’s Makar? (10-12-0)\n"
                "8: Pirate Horde (10-12-0)\n"
                "9: Momma Ain't Raise No Bitch (8-14-0)\n"
                "10: Rantanen With The Devil (8-14-0)\n"
                "11: Former Ice Dancers (6-16-0)\n"
                "12: Team Will (1-21-0)"
            ),
        )

        self.assertTrue(standings.ranks[4].points == 30)
        self.assertTrue(standings.ranks[6].team.name == "MacKstreet Boys")
        self.assertTrue(standings.ranks[1].points_for == 10813.2)
        self.assertTrue(str(standings.ranks[6]) == "6: MacKstreet Boys (10-12-0)")

        standings = self.league.standings(scoring_period_number=11)
        self.assertTrue(standings.ranks[7].points == 10)
        self.assertTrue(standings.ranks[3].team.name == "Son of a Mich")
        self.assertTrue(standings.ranks[12].points_for == 3479.8)

        standings = self.league.standings(scoring_period_number=6, only_period=True)
        self.assertTrue(standings.ranks[5].points == 2)
        self.assertTrue(standings.ranks[2].team.name == "Bunch of Yahoos")
        self.assertTrue(standings.ranks[1].points_for == 532.8)

    def test_trade_block(self) -> None:
        self.assertRaises(NotLoggedIn, self.league.pending_trades)
        self.assertRaises(NotLoggedIn, self.league.trade_block)
        add_cookie_to_session(self.league.session)
        trade_block = self.league.trade_block()
        self.assertEqual(
            str(trade_block),
            (
                "[Looking to swap a 9th rd pick and trade up in the next draft\n"
                "Barkov +9th for a 5th\n"
                "Zbad +9th for a 5th\n"
                "Breadman +9th for an 8th, I’d be willing to let these guys go for the right picks, Looking for picks., "
                "Looking to add a producing winger, send dem picks, These players are keepers for next 10 years, draft pics send them!]"
            ),
        )
        self.assertEqual(str(trade_block[1]), "I’d be willing to let these guys go for the right picks")
        self.assertEqual(str(trade_block[1]), "I’d be willing to let these guys go for the right picks")
        self.assertEqual(len(trade_block[4].players_offered), 2)
        self.assertIn("C", trade_block[4].players_offered)
        self.assertIn("D", trade_block[4].players_offered)
        self.assertEqual(len(trade_block[4].players_offered["C"]), 3)
        self.assertEqual(len(trade_block[4].players_offered["D"]), 1)
        self.assertEqual(len(trade_block[4].positions_wanted), 0)
        self.assertEqual(len(trade_block[5].players_offered), 0)
        self.assertEqual(len(trade_block[5].positions_wanted), 2)

        league = League("fdutr5ehmgr5bjm6")
        add_cookie_to_session(league.session)
        self.assertRaises(NotMemberOfLeague, league.trade_block)

    def test_transactions(self) -> None:
        transactions = self.league.transactions(count=160)
        self.assertTrue(len(transactions) == 160)
        self.assertTrue(len(transactions[147].players) == 2)
        self.assertTrue(transactions[147].players[0].type == "WW")
        self.assertTrue(transactions[147].players[0].name == "Pavel Dorofeyev")
        self.assertTrue(transactions[147].players[1].type == "DROP")
        self.assertTrue(transactions[147].players[1].name == "Owen Tippett")
        self.assertTrue(len(transactions[83].players) == 1)
        self.assertTrue(transactions[83].players[0].type == "DROP")
        self.assertTrue(transactions[83].players[0].name == "Brock Faber")
        self.assertTrue(len(transactions[46].players) == 2)
        self.assertTrue(transactions[46].players[0].type == "FA")
        self.assertTrue(transactions[46].players[0].name == "Filip Hronek")
        self.assertTrue(transactions[46].players[1].type == "DROP")
        self.assertTrue(transactions[46].players[1].name == "Ryan Leonard")

    def test_position_counts(self) -> None:
        team = self.league.team("wookie")
        counts = team.position_counts()
        for position in ["W", "C", "D", "TmG"]:
            self.assertIn(position, counts)
        self.assertTrue(counts["C"].gp == 17)
        self.assertIsNone(counts["W"].min)
        self.assertIsNone(counts["D"].max)
        self.assertTrue(counts["TmG"].gp == 8)
        self.assertTrue(counts["TmG"].max == 7)
        counts = team.position_counts(11)
        self.assertTrue(counts["C"].gp == 7)
        self.assertIsNone(counts["W"].min)
        self.assertIsNone(counts["D"].max)
        self.assertTrue(counts["TmG"].gp == 4)
        self.assertTrue(counts["TmG"].max == 4)

    def test_live_scores(self) -> None:
        team = self.league.team("wookie")
        scores = team.live_scores(date(year=2024, month=10, day=18))
        self.assertEqual(str(scores), "[Anthony Beauvillier, Samuel Girard]")
        self.assertEqual(scores[0].name, "Anthony Beauvillier")
        self.assertEqual(scores[1].points, 7.0)
        self.assertRaises(DateNotInSeason, team.live_scores, date(year=2024, month=10, day=6))
        self.assertRaises(DateNotInSeason, team.live_scores, date(year=2024, month=7, day=18))

    def test_team_roster(self) -> None:
        team = self.league.team("wookie")
        self.assertRaises(PeriodNotInSeason, team.roster, 500)
        roster = team.roster(8)
        self.assertEqual(
            str(roster),
            (
                "Kashyyyk Wookies 🏴‍☠️ Roster\n"
                "C: Joel Eriksson Ek\n"
                "C: Jack Hughes\n"
                "W: Jake Guentzel\n"
                "W: David Pastrnak\n"
                "W: Mark Stone\n"
                "W: Alex Tuch\n"
                "D: Adam Fox\n"
                "D: Seth Jones\n"
                "D: Alec Martinez\n"
                "D: Empty\n"
                "Skt: Tomas Hertl\n"
                "C: Josh Norris\n"
                "W: Viktor Arvidsson\n"
                "W: Andrei Kuzmenko\n"
                "W: Tom Wilson\n"
                "D: Darnell Nurse\n"
                "D: Alexander Romanov\n"
                "C: Boone Jenner\n"
                "TmG: Vegas\n"
                "TmG: Nashville"
            ),
        )
        self.assertEqual(roster.active, 11)
        self.assertEqual(roster.active_max, 12)
        self.assertEqual(roster.reserve, 7)
        self.assertEqual(roster.reserve_max, 18)
        self.assertEqual(roster.injured, 1)
        self.assertEqual(roster.injured_max, 3)
        self.assertEqual(str(roster.rows[1].position), "[206:Center:C]")
        self.assertEqual(str(roster.rows[1].player), "Jack Hughes")
        self.assertEqual(roster.rows[1].total_fantasy_points, 21.8)
        self.assertIsNone(roster.rows[1].game_today)
        self.assertEqual(str(roster.rows[2].player), "Jake Guentzel")
        self.assertEqual(roster.rows[2].total_fantasy_points, 14.7)
        self.assertEqual(str(roster.rows[2].game_today), "[062yw:CAR @TBL]")
        self.assertIn("Thu 4/17", roster.rows[2].future_games)
        self.assertEqual(str(roster.rows[2].future_games["Thu 4/17"]), "[063yr:NYR @TBL]")
