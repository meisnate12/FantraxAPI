Welcome to Fantrax Documentation!
===========================================================================

.. image:: https://img.shields.io/github/v/release/meisnate12/FantraxAPI?style=plastic
    :target: https://github.com/meisnate12/FantraxAPI/releases
    :alt: GitHub release (latest by date)

.. image:: https://img.shields.io/github/actions/workflow/status/meisnate12/FantraxAPI/tests.yml?branch=master&style=plastic
    :target: https://github.com/meisnate12/FantraxAPI/actions/workflows/tests.yml
    :alt: Build Testing

.. image:: https://img.shields.io/codecov/c/github/meisnate12/FantraxAPI?color=greenred&style=plastic
    :target: https://codecov.io/gh/meisnate12/FantraxAPI
    :alt: Build Coverage

.. image:: https://img.shields.io/github/commits-since/meisnate12/FantraxAPI/latest?style=plastic
    :target: https://github.com/meisnate12/FantraxAPI/commits/master
    :alt: GitHub commits since latest release (by date) for a branch

.. image:: https://img.shields.io/pypi/v/FantraxAPI?style=plastic
    :target: https://pypi.org/project/FantraxAPI/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/dm/FantraxAPI.svg?style=plastic
    :target: https://pypi.org/project/FantraxAPI/
    :alt: Downloads

.. image:: https://img.shields.io/readthedocs/fantraxapi?color=%2300bc8c&style=plastic
    :target: https://fantraxapi.kometa.wiki/en/latest/
    :alt: Wiki

.. image:: https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic
    :target: https://discord.gg/NfH6mGFuAB
    :alt: Discord

.. image:: https://img.shields.io/reddit/subreddit-subscribers/Kometa?color=%2300bc8c&label=r%2FKometa&style=plastic
    :target: https://www.reddit.com/r/Kometa/
    :alt: Reddit

.. image:: https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: GitHub Sponsors

.. image:: https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: Sponsor or Donate


Overview
---------------------------------------------------------------------------
Unofficial Python bindings for the Fantrax API. The goal is to make interaction with the API as easy as possible while emulating the endpoints as much as possible.
I built this testing with my NHL H2HPoints League so results may vary for other sports/league types. I'd be happy to add more but im not in any of those leagues.
If you make your league public under `Commissioner` -> `League Setup` -> `Misc` -> `Misc` and create an issue with your league id or url and i will work to get it added.


Installation & Documentation
---------------------------------------------------------------------------

.. code-block:: python

    pip install fantraxapi

Documentation_ can be found at Read the Docs.

.. _Documentation: https://fantraxapi.kometa.wiki


Using the API
===========================================================================

Getting a FantraxAPI Instance
---------------------------------------------------------------------------

To connect to the Fantrax API you use the FantraxAPI object.

.. code-block:: python

    from fantraxapi import League

    league_id = "96igs4677sgjk7ol"

    league = League(league_id)


.. code-block:: python

    import fantraxapi

    league_id = "96igs4677sgjk7ol"

    league = fantraxapi.League(league_id)


Usage Examples
===========================================================================

Example: Get the Scores for the Season.

.. code-block:: python

    from fantraxapi import League

    league_id = "96igs4677sgjk7ol"

    league = League(league_id)

    for _, scoring_period in league.scoring_periods().items():
        print("")
        print(scoring_period)


Connecting with a private league or accessing specific endpoints
===========================================================================

I was unable to decipher the api login method so in order to connect to a private league or specific endpoints in a public
league that are not public you will need to use a cookie. The code below overrides the :code:`api.request` function with
a new function that will automatically log you in using Google Chrome and the :code:`selenium` and :code:`webdriver-manager`
packages or load a saved cookie when :code:`NotLoggedIn` is raised then load the cookie into your current session and save
the logged in cookie to :code:`fantraxloggedin.cookie`.

First install the two packages:

.. code-block:: python

    pip install selenium
    pip install webdriver-manager

Second use the code below to setup the auto login on requests.

.. code-block:: python

    import os
    import pickle
    import time

    from requests import Session
    from selenium import webdriver
    from selenium.webdriver import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager

    from fantraxapi import League, NotLoggedIn, api
    from fantraxapi.api import Method

    username = "YOUR_USERNAME_HERE" # Provide your Fantrax Username here
    password = "YOUR_PASSWORD_HERE" # Provide your Fantrax Password here
    cookie_filepath = "fantraxloggedin.cookie" # Name of the saved Cookie file

    old_request = api.request # Saves the old function


    def new_request(league: "League", methods: list[Method] | Method) -> dict:
        try:
            if not league.logged_in:
                add_cookie_to_session(league.session) # Tries the login function when not logged in
            return old_request(league, methods) # Run old function
        except NotLoggedIn:
            add_cookie_to_session(league.session, ignore_cookie=True) # Adds/refreshes the cookie when NotLoggedIn is raised
            return new_request(league, methods) # Rerun the request


    api.request = new_request # replace the old function with the new function


    def add_cookie_to_session(session: Session, ignore_cookie: bool = False) -> None:
        if not ignore_cookie and os.path.exists(cookie_filepath):
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
                with open(cookie_filepath, "wb") as cookie_file:
                    pickle.dump(driver.get_cookies(), cookie_file)

                for cookie in cookies:
                    session.cookies.set(cookie["name"], cookie["value"])

    league_id = "usglqmvqmelpe6um"

    my_league = League(league_id)

    print(my_league.trade_block())  # The Trade Block Page is always private


Usage & Contributions
---------------------------------------------------------------------------

* Source is available on the `Github Project Page <https://github.com/meisnate12/FantraxAPI>`_.
* Contributors to FantraxAPI own their own contributions and may distribute that code under
  the `MIT license <https://github.com/meisnate12/FantraxAPI/blob/master/LICENSE.txt>`_.
