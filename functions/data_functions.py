# Regan Givens
# 8/24/23
# This py file contains all data manipulation functions when it comes to dataframes created
# from the response of the ESPN API.
import pandas as pd
import numpy as np
import team_info

position_map = {
 1: 'QB',
 2: 'RB',
 3: 'WR',
 4: 'TE',
 5: 'K',
 16: 'D/ST'
}

# For the time being, the API isn't properly getting the updated names of teams in my league.
# Below is the hardcoded team dictionary in a py file labeled 'team_info' to be replaced later by the mapTeams function
ff_teams_dict = team_info.teams

def ffTeamsDict():
    return ff_teams_dict

def getLeagueName(gen_data):
    # Function to return the fantasy football league's name
    league_name = gen_data['settings']['name']
    return league_name

def currentWeek(matchup_data):
    # Function to intake a response from the API and return the current week (scoringPeriodId)
    # Grab the current week INT from the matchup data
    currWeek = matchup_data['scoringPeriodId']
    # Check to make sure we're not outside of the standard 17 week FF League
    if currWeek > 17:
        currWeek = 17
    # Return the int
    return currWeek

def mapTeams(gen_data):
    # Function to intake a dataframe and return a dictionary of ID to Team Name
    # Initialize a dictionary to hold team id and name
    team_dict = {}
    # Grab the teams data from the general data passed in
    teams_data = gen_data['teams']
    # Loop through the teams data
    for team in teams_data:
        # Generate the team name and grab the team's id value
        team_name = team['location'] + ' ' + team['nickname']
        team_id = team['id']
        # Create a dictionary of the team's id and their name
        team_dict[team_id] = team_name
    # Return the team dictionary
    return team_dict

def getMatchupResults(match, team_data):
    # Function to intake individual matches and return a dictionary of away team name, away team points, home team name, home team points, and winner
    # Grab Away ID, Home ID, Away Score, Home Score, and Winner
    away_id = match['away']['teamId']
    home_id = match['home']['teamId']
    away_score = match['away']['totalPoints']
    home_score = match['home']['totalPoints']
    winner = match['winner']
    
    # Utilizing the team data, get the actual names of the teams to display
    away_team = ''
    home_team = ''

    # Loop through team_deta to get names of teams, break when you've got both teams names
    for teams in team_data:
        if away_id == teams:
            away_team = team_data[teams]
        if home_id == teams:
            home_team = team_data[teams]
        if home_team != '' and away_team != '':
            break

    # Return a single dictionary of the data we need    
    return {'away team': away_team, 'away score': away_score, 'home team': home_team, 'home score': home_score, 'winner': winner}
     
def mapSchedule(matchup_data, team_data):
    # Function to intake a dataframe for matches and an array of dictionaries for teams and return the week results for the current week
    # Initialize an array to hold the matchup data to be returned
    match_arr = []
    # Grab the schedule data from the API response dataframe
    schedule_data = matchup_data['schedule']
    # Get the current week of fantasy football from the matchup data
    currWeek = currentWeek(matchup_data)
    # Loop through the schedule data to generate the home and away teams, how many points they scored, and who won
    for match in schedule_data:
        # Get the week value
        week = match['matchupPeriodId']
        # If the week matches the current week, continue
        if week == currWeek:
           # Get the match dictionary from getMatchupResults function above
           match_dict = getMatchupResults(match, team_data)
           # Append the match dict to the match arr
           match_arr.append(match_dict)
    # Return the array       
    return match_arr       

def mapDraft(draft_data, player_df, ff_teams, nfl_teams):
    # Function to intake a dataframe and return the draft information
    # Break dataframe down further with relevant info and return it
    picks = draft_data['draftDetail']['picks']
    new_df = pd.DataFrame(picks)
    pick_data = new_df[['overallPickNumber', 'playerId', 'teamId']]
    pick_data = pick_data.replace({'teamId':ff_teams})
    merged_data = pd.merge(pick_data, player_df, how='inner', left_on='playerId', right_on='id') 
    merged_data = merged_data.replace({'proTeamId':nfl_teams})
    return merged_data

def mapPlayerData(player_data):
    # Function to intake dataframe from API call and return football player data
    players = player_data['players']
    new_df = pd.DataFrame(players)
    player_df = pd.DataFrame(new_df['player'])
    df_columns = ['defaultPositionId', 'fullName', 'id', 'proTeamId', 'positionalRanking', 'totalRanking', 'totalRating']
    final_df = pd.DataFrame(columns=df_columns)
    for index, row in player_df.iterrows():
        id = new_df['id'][index]
        fullName = row['player']['fullName']
        defPosId = row['player']['defaultPositionId']
        proTeamId = row['player']['proTeamId']
        ratings = new_df['ratings'][index]
        # ESPN API sometimes returns 'NaN' for ratings data. If that's the case, we don't care about that entry
        if ratings == ratings:
            ratings = new_df['ratings'][index]['0']
            posRank = ratings['positionalRanking']
            totalRank = ratings['totalRanking']
            totalRating = ratings['totalRating']
            player_row = pd.Series([defPosId, fullName, id, proTeamId, posRank, totalRank, totalRating], index=['defaultPositionId', 'fullName', 'id', 'proTeamId', 'positionalRanking', 'totalRanking', 'totalRating'])
            final_df = pd.concat([final_df, player_row.to_frame().T], ignore_index=True)
    formatted_player_data = final_df.replace({'defaultPositionId':position_map})
    return formatted_player_data

def mapNFLTeams(nfl_teams):
    team_dict = {}
    nfl_team_data = nfl_teams['sports'][0]['leagues'][0]['teams']
    for team in nfl_team_data:
        team_info = team['team']
        team_id = int(team_info['id'])
        team_name = team_info['name']
        team_dict[team_id] = team_name
    return team_dict