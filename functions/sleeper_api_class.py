# Regan Givens
# 9/2/23
# This py file calls the necessary APIs and convers the json returns to dataframes to be manipulated
import requests
import sleeper_league_info

class sleeperAPILeague:
    
    def __init__(self):
        self.leagueID = sleeper_league_info.leagueID
        
        self.sleeperURL = f'https://api.sleeper.app/v1/league/{self.leagueID}'
        self.playerURL = 'https://api.sleeper.app/v1/players/nfl'

    def callESPNAPI(self, requested_data = None, week = None):
        # This function will call the Sleeper Fantasy Football API and return the json response
        # Params - Requested Data - This is the data requested to be shown, defaulted to None
        # Return - df - A dataframe of the json response data from the API

        # Based on the requested data, configure the params and url to use 
        if requested_data == 'matchup':
            apiURL = self.sleeperURL + f'/matchups/{week}'
        elif requested_data == 'draft':
            apiURL = self.sleeperURL + '/drafts'
        elif requested_data == 'team':
            apiURL = self.sleeperURL + '/users'
        elif requested_data == 'player':
            apiURL = self.playerURL
        else:
            apiURL = self.sleeperURL
        
        # Call the API with the URL and params selected
        response = requests.get(apiURL)
        res_data = response.json()
        return res_data