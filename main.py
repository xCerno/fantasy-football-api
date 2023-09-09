# Regan Givens
# 8/24/23
# Main file to call necessary functions

#Import functions
import functions.espn_api_class as espnAPI
import functions.sleeper_api_class as sleeperAPI
import functions.espn_data_functions as espnDataFunc
import functions.espn_formatting_functions as espnFormatFunc
import functions.sleeper_data_functions as sleepDataFunc

# Commented out section below - 9/5 to test sleeper API calls
# Updating scripting below to utilize classes
# leagueClass = espnAPI.espnAPILeague()

# genData = leagueClass.callESPNAPI()
# leagueName = espnDataFunc.getLeagueName(genData)

#As of 8/29/23, API is not properly returning correct team names.
#Function below commented out until properly functioning
#ff_teams = dataFunc.mapTeams(gen_data)
# ffTeams = espnDataFunc.espnFFTeams()

# nflData = leagueClass.callESPNAPI('team')
# nflDF = espnDataFunc.mapNFLTeams(nflData)

# playerData = leagueClass.callESPNAPI('player')
# playerDF = espnDataFunc.mapPlayerData(playerData)

# draftData = leagueClass.callESPNAPI('draft')
# draftDF = espnDataFunc.mapDraft(draftData, playerDF, ffTeams, nflDF)
# espnFormatFunc.draftText(draftDF)

# matchupData = leagueClass.callESPNAPI('matchup')
#currSchedule = espnDataFunc.mapSchedule(matchupData, ffTeams)


# 9/7/23 - Testing Sleeper API functionality - WIP
sleeperClass = sleeperAPI.sleeperAPILeague()
genData = sleeperClass.callSleeperAPI()

leagueDF = sleepDataFunc.mapLeagueData(genData)
print(leagueDF)
print()

userData = sleeperClass.callSleeperAPI('users')
userDF = sleepDataFunc.mapUsersData(userData)
print(userDF)
print()

#playerData = sleeperClass.callSleeperAPI('players')

draftData = sleeperClass.callSleeperAPI('picks', draftID=leagueDF['Draft ID'][0])
draftDF = sleepDataFunc.mapDraftPicks(draftData, userDF)
print(draftDF)