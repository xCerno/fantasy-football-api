# Regan Givens
# 9/5/23
# This py file contains all data manipulation functions when it comes to dataframes created
# from the response of the Sleeper API.
import pandas as pd
import numpy as np

# Need to write players to a file to reference. Only need to update players file weekly at most.

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

# General Draft API Return Important Data
    # draft_id
    # draft_order

# Draft Picks Return
    # List of Dictionaries, each dict is a pick
    # round
    # roster_id
    # player_id
    # picked_by
    # pick_no
    # metadata - This is a dict
        #years_exp
        #team
        #status
        #position
        #player_id
        #last_name
        #injursy_status
        #first_name