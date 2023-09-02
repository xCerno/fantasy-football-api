# Regan Givens
# 8/24/23
# Main file to call necessary functions

#Import functions
import functions.espn_api_class as espnAPI
import functions.data_functions as dataFunc
import functions.formatting_functions as formatFunc

# Updating scripting below to utilize classes
leagueClass = espnAPI.espnAPILeague()

gen_data = leagueClass.callESPNAPI()
league_name = dataFunc.getLeagueName(gen_data)

# As of 8/29/23, API is not properly returning correct team names.
# Function below commented out until properly functioning
#ff_teams = dataFunc.mapTeams(gen_data)
ff_teams = dataFunc.ffTeamsDict()

nfl_data = leagueClass.callESPNAPI('team')
nfl_df = dataFunc.mapNFLTeams(nfl_data)

player_data = leagueClass.callESPNAPI('player')
player_df = dataFunc.mapPlayerData(player_data)

draft_data = leagueClass.callESPNAPI('draft')
draft_df = dataFunc.mapDraft(draft_data, player_df, ff_teams, nfl_df)
formatFunc.draftText(draft_df)

matchup_data = leagueClass.callESPNAPI('matchup')
curr_schedule = dataFunc.mapSchedule(matchup_data, ff_teams)
