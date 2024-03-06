from fantraxapi import FantraxAPI

last_year = "96idm2rtl8mjk7ol"
this_year = "yae6qgmoljsmydnu"

api = FantraxAPI(last_year)

sep = '", "'
print(f'["{sep.join([team.name for team in api.teams])}"]')