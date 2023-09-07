# Regan Givens
# 8/24/23
# Main file to call necessary functions

#Import functions
import functions.espn_api_class as espnAPI
import functions.sleeper_api_class as sleeperAPI
import functions.espn_data_functions as dataFunc
import functions.espn_formatting_functions as formatFunc

# Commented out section below - 9/5 to test sleeper API calls
# Updating scripting below to utilize classes
leagueClass = espnAPI.espnAPILeague()

genData = leagueClass.callESPNAPI()
leagueName = dataFunc.getLeagueName(genData)

# As of 8/29/23, API is not properly returning correct team names.
# Function below commented out until properly functioning
#ff_teams = dataFunc.mapTeams(gen_data)
ffTeams = dataFunc.ffTeamsDict()

nflData = leagueClass.callESPNAPI('team')
nflDF = dataFunc.mapNFLTeams(nflData)

playerData = leagueClass.callESPNAPI('player')
playerDF = dataFunc.mapPlayerData(playerData)

draftData = leagueClass.callESPNAPI('draft')
draftDF = dataFunc.mapDraft(draftData, playerDF, ffTeams, nflDF)
formatFunc.draftText(draftDF)

matchupData = leagueClass.callESPNAPI('matchup')
currSchedule = dataFunc.mapSchedule(matchupData, ffTeams)


# 9/7/23 - Testing Sleeper API functionality - WIP
# sleeperClass = sleeperAPI.sleeperAPILeague()
# sData = sleeperClass.callSleeperAPI('draft')[0]
# draftID = sData['draft_id']
# dData = sleeperClass.callSleeperAPI('picks', draftID=draftID)
# #print(sData)
# for key in dData:
#     print(key)
#     # List of Dictionaries, each dict is a pick
#     # round
#     # roster_id
#     # player_id
#     # picked_by
#     # pick_no
#     # metadata - This is a dict
#         #years_exp
#         #team
#         #status
#         #position
#         #player_id
#         #last_name
#         #injursy_status
#         #first_name