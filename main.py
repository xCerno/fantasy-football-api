# Regan Givens
# 9/26/23
# Main file to call necessary functions

#Import class
import functions.espn_api_class as espnAPI

# Initiate class instance
leagueClass = espnAPI.espnAPILeague()
# Ask user for data
weekVal = int(input('Enter Week of Fantasy: '))
draftOpt = str(input('Do you want draft info? '))
# Run the functions
leagueClass.run(weekVal, draftOpt)