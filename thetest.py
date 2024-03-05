from fantraxapi import FantraxAPI

last_year = "96idm2rtl8mjk7ol"
this_year = "yae6qgmoljsmydnu"

api = FantraxAPI(this_year)

response = api.standings(week=10)

print(response)

print(api.max_goalie_games_this_week())