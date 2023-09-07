# Regan Givens
# 9/2/23
# This py file calls the necessary APIs and convers the json returns to dataframes to be manipulated
import requests
import sleeper_league_info

class sleeperAPILeague:
    
    def __init__(self):
        self.leagueID = sleeper_league_info.leagueID
        
        self.sleeperURL = f'https://api.sleeper.app/v1/league/{self.leagueID}'
        self.picksURL = f'https://api.sleeper.app/v1/draft/<draft_id>/picks'
        self.playerURL = 'https://api.sleeper.app/v1/players/nfl'

    def callSleeperAPI(self, reqData = None, week = None, draftID = None):
        # This function will call the Sleeper Fantasy Football API and return the json response
        # Params - Requested Data - This is the data requested to be shown, defaulted to None
        # Return - df - A dataframe of the json response data from the API

        # Based on the requested data, configure the params and url to use 
        if reqData == 'matchup':
            apiURL = self.sleeperURL + f'/matchups/{week}'
        elif reqData == 'draft':
            apiURL = self.sleeperURL + '/drafts'
        elif reqData == 'picks':
            apiURL = self.picksURL.replace('<draft_id>', draftID)
        elif reqData == 'users':
            apiURL = self.sleeperURL + '/users'
        elif reqData == 'players':
            apiURL = self.playerURL
        elif reqData == 'trades':
            apiURL = self.sleeperURL + '/traded_picks'
        else:
            apiURL = self.sleeperURL
        
        # Call the API with the URL and params selected
        response = requests.get(apiURL)
        resData = response.json()
        return resData