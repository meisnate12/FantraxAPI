Welcome to Fantrax Documentation!
==========================================================

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

.. image:: https://img.shields.io/readthedocs/plex-meta-manager?color=%2300bc8c&style=plastic
    :target: https://fantraxapi.metamanager.wiki/en/latest/
    :alt: Wiki

.. image:: https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic
    :target: https://discord.gg/NfH6mGFuAB
    :alt: Discord

.. image:: https://img.shields.io/reddit/subreddit-subscribers/PlexMetaManager?color=%2300bc8c&label=r%2FPlexMetaManager&style=plastic
    :target: https://www.reddit.com/r/PlexMetaManager/
    :alt: Reddit

.. image:: https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: GitHub Sponsors

.. image:: https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: Sponsor or Donate


Overview
----------------------------------------------------------
Unofficial Python bindings for the Fantrax API. The goal is to make interaction with the API as easy as possible while emulating the endpoints as much as possible


Installation & Documentation
----------------------------------------------------------

.. code-block:: python

    pip install fantraxapi

Documentation_ can be found at Read the Docs.

.. _Documentation: https://fantraxapi.metamanager.wiki


Using the API
==========================================================

Getting a FantraxAPI Instance
----------------------------------------------------------

To connect to the Fantrax API you use the FantraxAPI object.

.. code-block:: python

    from fantraxapi import FantraxAPI

    league_id = "96igs4677sgjk7ol"

    api = FantraxAPI(league_id)


.. code-block:: python

    import fantraxapi

    api = fantraxapi.FantraxAPI()


Usage Examples
==========================================================

Example: Get the Scores for the Season.

.. code-block:: python

    from fantraxapi import FantraxAPI

    league_id = "96igs4677sgjk7ol"

    api = FantraxAPI(league_id)

    for _, scoring_period in api.scoring_periods().items():
        print("")
        print(scoring_period)


Connecting with a private League
==========================================================

I was unable to decipher the api login method so in order to connect to a private league or specific pages in a public
league that are not public you need to use a cookie. The code below uses Google Chrome and the :code:`selenium` and
:code:`webdriver-manager` packages to open a chrome instance where you can login and after 30 seconds a cookie file with
that login will be save to :code:`fantraxloggedin.cookie`.

First install the two packages:

.. code-block:: python

    pip install selenium
    pip install webdriver-manager

Second run the code below and login when the chrome window loads the Fantrax login page:

.. code-block:: python

    import pickle
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    service = Service(ChromeDriverManager().install())

    options = Options()
    options.add_argument("--window-size=1920,1600")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")

    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get("https://www.fantrax.com/login")
        time.sleep(30)
        pickle.dump(driver.get_cookies(), open("fantraxloggedin.cookie", "wb"))


Third use the saved cookie file with the wrapper:

.. code-block:: python

    import pickle
    from fantraxapi import FantraxAPI
    from requests import Session

    session = Session()

    with open("fantraxloggedin.cookie", "rb") as f:
        for cookie in pickle.load(f):
            session.cookies.set(cookie["name"], cookie["value"])

    league_id = "96igs4677sgjk7ol"

    api = FantraxAPI(league_id, session=session)

    print(api.trade_block()) # The Trade Block Page is always private


Usage & Contributions
----------------------------------------------------------

* Source is available on the `Github Project Page <https://github.com/meisnate12/FantraxAPI>`_.
* Contributors to FantraxAPI own their own contributions and may distribute that code under
  the `MIT license <https://github.com/meisnate12/FantraxAPI/blob/master/LICENSE.txt>`_.
