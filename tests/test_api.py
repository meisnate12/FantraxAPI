import os, sys, time, unittest
from datetime import datetime, timedelta
from dotenv import load_dotenv
from github import Auth, Github
from tmdbapis.api3 import API3
from tmdbapis.exceptions import NotFound, Invalid, Authentication
from tmdbapis.objs.reload import Movie, Person, TVShow
from tmdbapis.tmdb import TMDbAPIs

"""
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""

load_dotenv()

apikey = os.environ["TMDB_APIKEY"]
session_id = os.environ["TMDB_SESSION"]
v4 = os.environ["TMDB_V4_TOKEN"]
access = os.environ["TMDB_V4_ACCESS"]
username = os.environ["TMDB_USERNAME"]
password = os.environ["TMDB_PASSWORD"]
gh_token = os.environ["PAT"]
local = os.environ["LOCAL"] == "True"
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

movie_ids = {
    "3.8": {"id": 1892, "name": "Return of the Jedi"},
    "3.9": {"id": 1893, "name": "Star Wars: Episode I - The Phantom Menace"},
    "3.10": {"id": 1894, "name": "Star Wars: Episode II - Attack of the Clones"},
    "3.11": {"id": 1895, "name": "Star Wars: Episode III - Revenge of the Sith"},
    "3.12": {"id": 140607, "name": "Star Wars: The Force Awakens"},
}

show_ids = {
    "3.8": {"id": 4194, "name": "Star Wars: The Clone Wars"},
    "3.9": {"id": 105971, "name": "Star Wars: The Bad Batch"},
    "3.10": {"id": 60554, "name": "Star Wars Rebels"},
    "3.11": {"id": 203085, "name": "Star Wars: Tales of the Jedi"},
    "3.12": {"id": 83867, "name": "Star Wars: Andor"},
}

episode_ids = {
    "3.8": {"id": 1, "name": "Ambush"},
    "3.9": {"id": 2, "name": "Rising Malevolence"},
    "3.10": {"id": 3, "name": "Shadow of Malevolence"},
    "3.11": {"id": 4, "name": "Destroy Malevolence"},
    "3.12": {"id": 5, "name": "Rookies"},
}

class APITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = TMDbAPIs(apikey, v4_access_token=access, session_id=session_id)
        cls.api_v4 = TMDbAPIs(apikey, v4_access_token=access)
        cls.api_v3_session = TMDbAPIs(apikey)
        cls.api_v4_session = TMDbAPIs(apikey)
        cls.raw = API3(apikey, session_id=session_id)

    def test_aa_session(self):
        self.assertIsNotNone(self.api_v4.session_id)

        self.api_v3_session.language = "en"
        self.assertEqual(self.api_v3_session.language, "en")
        self.api_v3_session.language = "en-US"
        self.assertEqual(self.api_v3_session.language, "en-US")
        self.api_v3_session.language = None
        self.assertIsNone(self.api_v3_session.language)
        with self.assertRaises(Invalid):
            self.api_v3_session.language = "invalid_value"

        self.api_v3_session.include_language = "en,null,en-US"
        self.assertEqual(self.api_v3_session.include_language, "en,null,en-US")
        self.api_v3_session.include_language = None
        self.assertIsNone(self.api_v3_session.include_language)
        with self.assertRaises(Invalid):
            self.api_v3_session.include_language = "invalid_value"

        with self.assertRaises(Authentication):
            print(self.api_v3_session.account_id)
        self.api_v3_session.authenticate(username, password)
        self.api_v4_session._api._session_id = self.api_v3_session.session_id

        with self.assertRaises(Authentication):
            self.api_v4_session.v4_approved()
        account = self.api_v4_session.account()
        with self.assertRaises(Authentication):
            account.movie_recommendations()
        self.api_v4_session.v4_access(v4)
        with self.assertRaises(Authentication):
            account.movie_recommendations()
        v4_url = self.api_v4_session.v4_authenticate()
        if local:
            print(f"\n\nApprove URL: {v4_url}")
            with open("url.txt", "w") as file1:
                file1.write(v4_url)
            time.sleep(120)
        else:
            git = Github(auth=Auth.Token(gh_token))
            repo = git.get_user("meisnate12").get_repo("TMDbAPIs")
            issue_id = repo.create_issue(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')} {py_version}", body=v4_url,
                                         assignee="meisnate12", labels=["approval-needed"]).number
            while True:
                issue = repo.get_issue(issue_id)
                if "approval-needed" not in [la.name for la in issue.labels]:
                    issue.edit("Delete", body="delete", state="closed")
                    break
                time.sleep(10)
        self.api_v4_session.v4_approved()
        print("\ntest_aa_session: ", end="")

    def test_ab_variables(self):
        print("\ntest_ab_variables: ", end="")
        self.assertEqual(self.api.session_id, session_id)
        self.assertIsNotNone(self.api.v4_access_token)
        self.assertEqual(self.api.account_id, 8568268)
        self.assertEqual(self.api.v4_account_id, "5d339fb42f8d097bccd118c7")

    def test_account(self):
        print("\ntest_account: ", end="")
        account = self.api.account()
        self.assertEqual(account.id, 8568268)
        self.assertEqual(account.username, "meisnate12")
        self.assertGreater(len(account.created_lists(v3=True).results), 0)
        self.assertGreater(len(account.created_lists().results), 0)
        self.assertGreater(len(account.favorite_movies(v3=True).results), 0)
        self.assertGreater(len(account.favorite_movies().results), 0)
        self.assertGreater(len(account.favorite_tv_shows(v3=True).results), 0)
        self.assertGreater(len(account.favorite_tv_shows().results), 0)
        self.assertGreater(len(account.rated_movies(v3=True).results), 0)
        self.assertGreater(len(account.rated_movies().results), 0)
        self.assertGreater(len(account.rated_tv_shows(v3=True).results), 0)
        self.assertGreater(len(account.rated_tv_shows().results), 0)
        self.assertGreater(len(account.rated_episodes().results), 0)
        self.assertGreater(len(account.movie_watchlist(v3=True).results), 0)
        self.assertGreater(len(account.movie_watchlist().results), 0)
        self.assertGreater(len(account.tv_show_watchlist(v3=True).results), 0)
        self.assertGreater(len(account.tv_show_watchlist().results), 0)
        self.assertGreater(len(account.movie_recommendations().results), 0)
        self.assertGreater(len(account.tv_show_recommendations().results), 0)

    def test_certifications(self):
        print("\ntest_certifications: ", end="")
        movie = self.api.movie_certifications()
        tv = self.api.tv_certifications()
        self.assertIn("US", movie)
        self.assertIn("US", tv)
        self.assertIn("Certifications", f"{movie['US']}")

    def test_changes(self):
        print("\ntest_changes: ", end="")
        now = datetime.now()
        with self.assertRaises(Invalid):
            self.api.movie_change_list(start_date=f"fa/01/{now.year}")
        self.assertGreater(len(self.api.movie_change_list(start_date=now - timedelta(days=7), end_date=now)), 0)
        self.assertGreater(len(self.api.movie_change_list()), 0)
        self.assertGreater(len(self.api.tv_change_list()), 0)
        self.assertGreater(len(self.api.person_change_list()), 0)

    def test_collections(self):
        print("\ntest_collections: ", end="")
        collection = self.api.collection(10)
        with self.assertRaises(AttributeError):
            collection.name = "New Name"
        with self.assertRaises(AttributeError):
            del collection.name
        self.assertTrue(collection == collection)
        self.assertTrue(collection == 10)
        self.assertTrue(collection == "Star Wars Collection")
        self.assertEqual(collection.name, "Star Wars Collection")
        self.assertGreater(len(collection.movies), 0)

    def test_companies(self):
        print("\ntest_companies: ", end="")
        company = self.api.company(1)
        self.assertEqual(company.name, "Lucasfilm Ltd.")
        self.assertGreater(len(company.movies), 0)
        self.assertGreater(len(company.tv_shows), 0)

    def test_credit(self):
        print("\ntest_credit: ", end="")
        credit = self.api.credit("52fe420dc3a36847f8000441")
        self.assertEqual(credit.name, "Mark Hamill")
        self.assertEqual(credit.person_id, 2)
        self.assertEqual(credit.character, "Luke Skywalker")
        credit2 = self.api.credit("5beb247f92514143e6058194")
        self.assertEqual(credit2.name, "Pedro Pascal")

    def test_discover(self):
        print("\ntest_discover: ", end="")
        with self.assertRaises(Invalid):
            self.api.discover_movies(invalid_attr=1)
        with self.assertRaises(Invalid):
            self.api.discover_movies(sort_by="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(region="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(include_video="y", certification_country="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(include_video="n", certification_country="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(certification="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(**{"release_date.gte": datetime.now(), "release_date.lte": "gg/gg/gggg"})
        with self.assertRaises(Invalid):
            self.api.discover_movies(**{"vote_average.gte": 5, "vote_average.lte": 0})
        with self.assertRaises(Invalid):
            self.api.discover_movies(**{"vote_count.gte": 5, "vote_count.lte": 0})
        with self.assertRaises(Invalid):
            self.api.discover_movies(certification="PG", certification_country="US", with_watch_monetization_types="invalid_value")
        with self.assertRaises(Invalid):
            self.api.discover_movies(with_watch_monetization_types="free")
        with self.assertRaises(Invalid):
            self.api.discover_movies(with_watch_monetization_types="free", watch_region="US", include_video="g")
        movies = self.api.discover_movies(with_companies=1, sort_by="popularity.asc")
        self.assertEqual(len(movies.results), 20)
        movies.load_next()
        self.assertEqual(len(movies.results), 20)
        with self.assertRaises(Invalid):
            movies.load_page(0)
        with self.assertRaises(Invalid):
            movies.get_results(-1)
        self.assertEqual(len(movies.get_results(50)), 50)
        self.assertGreater(len(movies.get_results()), 50)
        movies.load_page(1)
        self.assertIsNotNone([m for m in movies])
        self.assertIsNotNone(movies[1])
        tv_shows = self.api.discover_tv_shows(with_companies=1)
        self.assertGreater(len(tv_shows), 0)

    def test_find(self):
        print("\ntest_find: ", end="")
        self.assertGreater(len(self.api.find_by_id(imdb_id="tt0076759").movie_results), 0)
        self.assertGreater(len(self.api.find_by_id(facebook_id="StarWars").movie_results), 0)
        self.assertGreater(len(self.api.find_by_id(twitter_id="starwars").movie_results), 0)
        self.assertGreater(len(self.api.find_by_id(instagram_id="starwars").movie_results), 0)
        self.assertGreater(len(self.api.find_by_id(freebase_mid="/m/0524b41").tv_results), 0)
        self.assertGreater(len(self.api.find_by_id(freebase_id="/en/game_of_thrones").tv_results), 0)
        self.assertGreater(len(self.api.find_by_id(tvdb_id="121361").tv_results), 0)
        self.assertGreater(len(self.api.find_by_id(tvrage_id="24493").tv_results), 0)
        with self.assertRaises(Invalid):
            self.api.find_by_id()
        with self.assertRaises(NotFound):
            self.api.find_by_id(imdb_id="tt00764596759")

    def test_genres(self):
        print("\ntest_genres: ", end="")
        self.assertGreater(len(self.api.movie_genres(reload=True)), 0)
        self.assertGreater(len(self.api.tv_genres(reload=True)), 0)

    def test_keyword(self):
        print("\ntest_keyword: ", end="")
        keyword = self.api.keyword(4270)
        self.assertEqual(keyword.name, "galaxy")
        self.assertGreater(len(keyword.movies), 0)
        self.assertGreater(len(keyword.tv_shows), 0)

    def test_lists(self):
        print("\ntest_lists: ", end="")
        with self.assertRaises(Invalid):
            self.api.create_list("PMM Fail", "fail", load=True)
        for test_list in [
            self.api_v3_session.create_list("PMM Test V3", "en", load=True),
            self.api.create_list("PMM Test V4", self.api._iso_639_1["en"], load=True)
        ]:
            test_list.add_items([(524434, "movie")])
            self.assertGreater(len(test_list), 0)
            self.assertTrue(test_list.has_item((524434, "movie")))
            test_list.remove_items((524434, "movie")) # noqa
            self.assertFalse(test_list.has_item((524434, "movie")))
            test_list.add_items((524434, "movie")) # noqa
            if "V4" in test_list.name:
                with self.assertRaises(Invalid):
                    test_list.update()
                with self.assertRaises(Invalid):
                    test_list.update(sort_by="not valid")
                test_list.update(name="PMM Test V4 V2", description="Test Description")
                self.assertEqual(test_list.name, "PMM Test V4 V2")
                self.assertEqual(test_list.description, "Test Description")
                test_list.update_items(((524434, "movie"), "test description")) # noqa

            test_list.clear()
            self.assertFalse(test_list.has_item((524434, "movie")))
            self.assertEqual(len(test_list), 0)
            test_list.delete()
            with self.assertRaises(NotFound):
                test_list.reload()

    def test_movie(self):
        print("\ntest_movie: ", end="")
        with self.assertRaises(NotFound):
            self.api.movie(10)
        with self.assertRaises(Invalid):
            self.api.now_playing_movies(region="fail")
        movie = self.api.movie(movie_ids[py_version]["id"])
        self.assertIsNotNone(str(movie.watch_providers))
        self.assertEqual(movie.title, movie_ids[py_version]["name"])
        self.assertIsInstance(self.api.latest_movie(), Movie)
        self.assertGreater(len(self.api.now_playing_movies(region="us")), 0)
        self.assertGreater(len(self.api.popular_movies(region=self.api._iso_3166_1["us"])), 0)
        self.assertGreater(len(self.api.top_rated_movies()), 0)
        self.assertGreater(len(self.api.upcoming_movies()), 0)
        with self.assertRaises(Invalid):
            movie.rate(11.0)
        movie.rate(8.5)
        time.sleep(2)
        movie.mark_as_favorite()
        time.sleep(2)
        movie.add_to_watchlist()
        time.sleep(2)
        movie.reload()
        self.assertEqual(movie.rated, 8.5)
        self.assertTrue(movie.favorite)
        self.assertTrue(movie.watchlist)
        time.sleep(2)
        movie.delete_rating()
        time.sleep(2)
        movie.remove_as_favorite()
        time.sleep(2)
        movie.remove_from_watchlist()
        time.sleep(2)
        movie.reload()
        self.assertIsNone(movie.rated)
        self.assertFalse(movie.favorite)
        self.assertFalse(movie.watchlist)
        movie.lists.load_page(1)
        self.assertGreater(len(movie.lists), 0)
        movie.reviews.load_page(1)
        self.assertGreater(len(movie.reviews), 0)
        movie.recommendations.load_next()
        self.assertGreater(len(movie.recommendations), 0)
        movie.similar.load_next()
        self.assertGreater(len(movie.similar), 0)

    def test_movie_lists(self):
        print("\ntest_movie_lists: ", end="")
        with self.assertRaises(Invalid):
            self.api_v3_session.movie_watchlist(sort_by="invalid_value")
        with self.assertRaises(Invalid):
            self.api.movie_recommendations(sort_by="invalid_value")
        with self.assertRaises(Invalid):
            self.api.tv_show_recommendations(sort_by="invalid_value")
        self.assertGreater(len(self.api.movie_recommendations()), 0)

    def test_network(self):
        print("\ntest_network: ", end="")
        network = self.api.network(1)
        self.assertEqual(network.name, "Fuji TV")
        self.assertGreater(len(network.tv_shows), 0)

    def test_person(self):
        print("\ntest_person: ", end="")
        person = self.api.person(2)
        self.assertEqual(person.name, "Mark Hamill")
        self.assertIn("Tagged", str(person.tagged))
        self.assertIsInstance(self.api.latest_person(), Person)
        self.assertGreater(len(self.api.popular_people()), 0)

    def test_providers(self):
        print("\ntest_providers: ", end="")
        self.assertGreater(len(self.api.provider_regions()), 0)
        movie_providers = self.api.movie_providers()
        self.assertIn(movie_providers[0].name, f"{movie_providers[0]}")
        self.assertGreater(len(movie_providers), 0)
        self.assertGreater(len(self.api.tv_providers()), 0)

    def test_review(self):
        print("\ntest_review: ", end="")
        review = self.api.review("58a231c5925141179e000674")
        self.assertEqual(review.author, "Cat Ellington")

    def test_search(self):
        print("\ntest_search: ", end="")
        movies = self.api.movie_search("The Lord of the Rings")
        self.assertGreater(movies.total_results, 0)
        self.assertEqual(len(movies.results), 20)
        movies.load_next()
        self.assertGreater(len(movies.results), 0)
        with self.assertRaises(NotFound):
            movies.load_next()
        with self.assertRaises(NotFound):
            self.api.movie_search("fgdhsdfghsdfghsdgf")

        self.assertGreater(self.api.company_search("Disney").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.company_search("fgdhsdfghsdfghsdgf")
        self.assertGreater(self.api.collection_search("Star Wars").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.collection_search("fgdhsdfghsdfghsdgf")
        self.assertGreater(self.api.keyword_search("fantasy").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.keyword_search("fgdhsdfghsdfghsdgf")
        self.assertGreater(self.api.multi_search("Star Wars").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.multi_search("fgdhsdfghsdfghsdgf")
        self.assertGreater(self.api.people_search("George Lucas").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.people_search("fgdhsdfghsdfghsdgf")
        self.assertGreater(self.api.tv_search("Star Wars").total_results, 0)
        with self.assertRaises(NotFound):
            self.api.tv_search("fgdhsdfghsdfghsdgf")

    def test_trending(self):
        print("\ntest_trending: ", end="")
        self.assertGreater(len(self.api.trending("movie", "day")), 0)
        self.assertGreater(len(self.api.trending("tv", "day")), 0)
        self.assertGreater(len(self.api.trending("movie", "week")), 0)
        self.assertGreater(len(self.api.trending("tv", "week")), 0)
        with self.assertRaises(Invalid):
            self.api.trending("test", "day")
        with self.assertRaises(Invalid):
            self.api.trending("all", "test")

    def test_tv_episode(self):
        print("\ntest_tv_episode: ", end="")
        episode = self.api.tv_episode(4194, 1, episode_ids[py_version]["id"])
        self.assertEqual(episode.name, episode_ids[py_version]["name"])
        with self.assertRaises(Invalid):
            episode.rate(11.0)
        episode.rate(8.5)
        time.sleep(2)
        episode.reload()
        time.sleep(2)
        self.assertEqual(episode.rated, 8.5)
        time.sleep(4)
        episode.delete_rating()
        time.sleep(4)
        episode.reload()
        self.assertIsNone(episode.rated)

    def test_tv_episode_group(self):
        print("\ntest_tv_episode_group: ", end="")
        episode_group = self.api.episode_group("5b11ba820e0a265847002c6e")
        self.assertEqual(episode_group.name, "Chronological Order")

    def test_tv_season(self):
        print("\ntest_tv_season: ", end="")
        season = self.api.tv_season(4194, 1)
        self.assertEqual(season.name, "Season 1")

    def test_tv_show(self):
        print("\ntest_tv_show: ", end="")
        show = self.api.tv_show(show_ids[py_version]["id"])
        self.assertEqual(show.name, show_ids[py_version]["name"])
        self.assertIsInstance(self.api.latest_tv(), TVShow)
        self.assertGreater(len(self.api.tv_airing_today()), 0)
        self.assertGreater(len(self.api.tv_on_the_air()), 0)
        self.assertGreater(len(self.api.popular_tv()), 0)
        self.assertGreater(len(self.api.top_rated_tv()), 0)
        with self.assertRaises(Invalid):
            show.rate(11.0)
        show.rate(8.5)
        time.sleep(2)
        show.mark_as_favorite()
        time.sleep(2)
        show.add_to_watchlist()
        time.sleep(2)
        show.reload()
        self.assertEqual(show.rated, 8.5)
        self.assertTrue(show.favorite)
        self.assertTrue(show.watchlist)
        time.sleep(2)
        show.delete_rating()
        time.sleep(2)
        show.remove_as_favorite()
        time.sleep(2)
        show.remove_from_watchlist()
        time.sleep(2)
        show.reload()
        self.assertIsNone(show.rated)
        self.assertFalse(show.favorite)
        self.assertFalse(show.watchlist)
        show.recommendations.load_next()
        self.assertGreater(len(show.recommendations), 0)
        show.similar.load_next()
        self.assertGreater(len(show.similar), 0)

    def test_zz_logout(self):
        print("\ntest_logout: ", end="")
        self.api_v4_session.logout()
