# Regan Givens
# 8/24/23
# This py file calls the necessary APIs and convers the json returns to dataframes to be manipulated
import requests
import pandas as pd
import espn_league_info
import json


class espnAPILeague:
    
    def __init__(self):
        self.leagueID = espn_league_info.leagueID
        self.year = espn_league_info.year
        self.espnS2 = espn_league_info.espnS2
        self.swid = espn_league_info.swid
        self.cookies = {'swid':self.swid, 'espn_s2':self.espnS2}

        # ESPN FF API URL - Customizing the request view below will return different results
        self.ffURL = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leagues/{self.leagueID}'

        # ESPN Players API URL
        self.playerURL = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leaguedefaults/3?view=kona_player_info'
        
        # ESPN Team API URL
        self.teamURL = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams'

    def callESPNAPI(self, reqData = None):
        # This function will call the ESPN Fantasy Football API and return the json response
        # Params - Requested Data - This is the data requested to be shown, defaulted to None
        # Return - df - A dataframe of the json response data from the API

        # Based on the requested data, configure the params and url to use 
        if reqData == 'matchup':
            params = {'view':'mMatchup'}
            apiURL = self.ffURL
        elif reqData == 'draft':
            params = {'view':'mDraftDetail'}
            apiURL = self.ffURL
        elif reqData == 'team':
            params = {}
            apiURL = self.teamURL
        elif reqData == 'player':
            # Because Player data requires unique filtering and headers, we return it in the elif
            filters = { "players": { "limit": 2000, "sortPercOwned":{"sortPriority":4,"sortAsc":False}}}
            headers = {'x-fantasy-filter': json.dumps(filters)}
            response = requests.get(self.playerURL, headers=headers)
            resData = response.json()
            return resData
        else:
            params = {}
            apiURL = self.ffURL
        
        # Call the API with the URL and params selected
        response = requests.get(apiURL, cookies=self.cookies, params=params)
        resData = response.json()
        return resData