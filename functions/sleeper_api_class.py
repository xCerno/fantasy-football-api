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
        elif reqData == 'rosters':
            apiURL = self.sleeperURL + '/rosters'
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
    
# Comments on the kinds of data returned by API calls

# General League API Return Important Data
    # Total Rosters
    # Status
    # Settings
    # Season Type
    # Season
    # Scoring Settings
    # Roster Positions
    # Name
    # Draft ID

# Draft Picks Return
    # List of Dictionaries, each dict is a pick
    # round
    # roster_id
    # player_id
    # picked_by
    # pick_no
    # is_keeper
    # metadata - This is a dict
        #years_exp
        #team
        #status
        #position
        #player_id
        #last_name
        #injursy_status
        #first_name

# Players return
    # List of Dictionaries - This data is MASSIVE and suggested to be saved
    # First key is the Player ID that contains a dictionary of the player's info
        # Status
        # Depth Chart Position
        # Fantasy Positions
        # Number
        # Injury Start Date
        # Position
        # Team
        # First Name and Last Name
        # College
        # Fantasy Data ID
        # Injury Status
        # Player ID
        # Height
        # Age
        # Depth Chart Order
        # Years Exp

# Rosters return
    # List of Dictionaries
    # Starters - List of Player IDs
    # Settings - Dictionary
        # Wins
        # Waiver Position
        # Waiver Budget Used
        # Total Moves
        # Ties
        # Losses
        # fpts decimal
        # fpts_against_decimal
        # fpts_against
        # fpts
    # roster id
    # players - this is a list of all players
    # owner id
    # reserve - list of reserve players

# Users Return
    # List of Dictionaries
    # User ID
    # Settings
    # Metadata
    # League ID
    # Is Owner
    # Is Bot
    # Display Name
    # Avatar