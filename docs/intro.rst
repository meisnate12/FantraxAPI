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

|

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

To connect to the FantraxAPI you use the FantraxAPI object.

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

In this example We grab

In this one we get the ``US`` :class:`~nagerapi.Country` Object and call ``public_holidays`` from that object.

.. code-block:: python

    from fantraxapi import FantraxAPI

    league_id = "96igs4677sgjk7ol"

    api = FantraxAPI(league_id)

    for _, scoring_period in api.scoring_periods().items():
        print("")
        print(scoring_period)

Usage & Contributions
----------------------------------------------------------
* Source is available on the `Github Project Page <https://github.com/meisnate12/FantraxAPI>`_.
* Contributors to FantraxAPI own their own contributions and may distribute that code under
  the `MIT license <https://github.com/meisnate12/FantraxAPI/blob/master/LICENSE.txt>`_.
