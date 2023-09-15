# Regan Givens
# 8/24/23
# This py file contains all data manipulation functions when it comes to dataframes created
# from the response of the ESPN API.
import pandas as pd
import numpy as np
import espn_team_info

positionMap = {
 1: 'QB',
 2: 'RB',
 3: 'WR',
 4: 'TE',
 5: 'K',
 16: 'D/ST'
}

statMap = {
    '0' : 'Pass Attempts',
    '1' : 'Completions',
    '3' : 'Pass Yards',
    '4' : 'Pass TDs',
    '20' : 'Interceptions',
    '23' : 'Rushing Attempts',
    '24' : 'Rushing Yards',
    '25' : 'Rushing TDs',
    '41' : 'Receptions',
    '42' : 'Receiving Yards',
    '43' : 'Receiving TDs',
    '83' : 'Made Field Goals',
    '84' : 'Attempted Field Goals',
    '85' : 'Missed Field Goals',
    '86' : 'Made Extra Points',
    '87' : 'Attempted Extra Points',
    '88' : 'Missed Extra Points',
    '93': 'Defense Blocked Kick for TD',
    '94': 'Defense TDs',
    '95': 'Defense Interceptions',
    '96': 'Defense Fumbles',
    '97': 'Defense Blocked Kicks',
    '98': 'Defense Safeties', 
    '99': 'Defense Sacks',
    '103': 'INT Returned for TD',
    '104': 'Fumbles Returned for TD',
    '106': 'Defense Forced Fumbles',
    '120': 'Defense Points Allowed',
    '127': 'Defense Yards Allowed'
}

# For the time being, the API isn't properly getting the updated names of teams in my league.
# Below is the hardcoded team dictionary in a py file labeled 'team_info' to be replaced later by the mapTeams function
ffTeamsDict = espn_team_info.teams

def espnFFTeams():
    return ffTeamsDict

def getLeagueName(genData):
    # Function to return the fantasy football league's name
    leagueName = genData['settings']['name']
    return leagueName

def currentWeek(matchupData):
    # Function to intake a response from the API and return the current week (scoringPeriodId)
    # Grab the current week INT from the matchup data
    currWeek = matchupData['scoringPeriodId']
    # Check to make sure we're not outside of the standard 17 week FF League
    if currWeek > 17:
        currWeek = 17
    # Return the int
    return currWeek

def mapTeams(genData):
    # Function to intake a dataframe and return a dictionary of ID to Team Name
    # Initialize a dictionary to hold team id and name
    teamDict = {}
    # Grab the teams data from the general data passed in
    teamsData = genData['teams']
    # Loop through the teams data
    for team in teamsData:
        # Generate the team name and grab the team's id value
        teamName = team['location'] + ' ' + team['nickname']
        teamID = team['id']
        # Create a dictionary of the team's id and their name
        teamDict[teamID] = teamName
    # Return the team dictionary
    return teamDict

def getRosterInfo(rosterData, teamID, week):
    # Function to pass in the roster data and return relevant info
    # Rosters are built as a list of every roster for every team in the league
    # ID = FF Team ID
    # Roster For Current Scoring Period  -> Entries & Applied Stat Total
    # Entries -> List
    # Player Pool Entry
    # Player
    # Stats
    # Applied Total = Points
    # Stats within Stats maps to statMap above
    # Stat Source ID = 1 (Projected)
    # Stat Source ID = 0 (Actual)
    rosterArr = []
    for roster in rosterData:
        if roster['id'] == teamID:
            teamRoster = roster['roster']['entries']
            for playerEntry in teamRoster:
                slotID = playerEntry['lineupSlotId']
                playerData = playerEntry['playerPoolEntry']['player']
                playerName = playerData['fullName']
                positionID = playerData['defaultPositionId']
                position = positionMap[positionID]
                stats = playerData['stats']
                appliedTot = 0
                playerActStats = {}
                playerProjStats = {}
                for stat in stats:
                    if stat['scoringPeriodId'] == week and stat['statSourceId'] == 0 and stat['stats'] != {}:
                        appliedTot = stat['appliedTotal']
                        actualStats = stat['stats']
                        #playerActStats = {}
                        for actStat in actualStats:
                            if actStat in statMap:
                                playerActStats[statMap[actStat]] = actualStats[actStat]
                    elif stat['scoringPeriodId'] == week and stat['statSourceId'] == 1 and stat['stats'] != {}:
                        #appliedTot = stat['appliedTotal']
                        projectedStats = stat['stats']
                        #playerProjStats = {}
                        for projStat in projectedStats:
                            if projStat in statMap:
                                playerProjStats[statMap[projStat]] = projectedStats[projStat]
                rosterArr.append([slotID, playerName, position, appliedTot, playerActStats, playerProjStats])
            break
    return rosterArr


def getMatchupResults(match, teamData, rosterData, week):
    # Function to intake individual matches and return a dictionary of away team name, away team points, home team name, home team points, and winner
    # Grab Away ID, Home ID, Away Score, Home Score, and Winner
    awayID = match['away']['teamId']
    homeID = match['home']['teamId']
    awayScore = match['away']['totalPoints']
    homeScore = match['home']['totalPoints']
    winner = match['winner']
    
    # Utilizing the team data, get the actual names of the teams to display
    awayTeam = ''
    homeTeam = ''

    # Loop through team_deta to get names of teams, break when you've got both teams names
    for teams in teamData:
        if awayID == teams:
            awayTeam = teamData[teams]
            awayRoster = getRosterInfo(rosterData, awayID, week)
        if homeID == teams:
            homeTeam = teamData[teams]
            homeRoster = getRosterInfo(rosterData, homeID, week)
        if homeTeam != '' and awayTeam != '':
            break

    # Return a single dictionary of the data we need    
    return {'away team': awayTeam, 'away score': awayScore, 'away roster':awayRoster, 'home team': homeTeam, 'home score': homeScore, 'home roster': homeRoster, 'winner': winner}
     
def mapSchedule(matchupData, teamData, week=None):
    # Function to intake a dataframe for matches and an array of dictionaries for teams and return the week results for the current week
    # Initialize an array to hold the matchup data to be returned
    matchArr = []
    # Grab the schedule data from the API response dataframe
    scheduleData = matchupData['schedule']
    # Grab the FF Teams Data which holds rosters for a given week
    teamRosters = matchupData['teams']
    # Get the current week of fantasy football from the matchup data
    if week is None:    
        currWeek = currentWeek(matchupData)
    else:
        currWeek = week
    # Loop through the schedule data to generate the home and away teams, how many points they scored, and who won
    for match in scheduleData:
        # Get the week value
        week = match['matchupPeriodId']
        # If the week matches the current week, continue
        if week == currWeek:
           # Get the match dictionary from getMatchupResults function above
           matchDict = getMatchupResults(match, teamData, teamRosters, week)
           # Append the match dict to the match arr
           matchArr.append(matchDict)
    # Return the array       
    return matchArr       

def mapDraft(draftData, playerDF, ffTeams, nflTeams):
    # Function to intake a dataframe and return the draft information
    # Break dataframe down further with relevant info and return it
    picks = draftData['draftDetail']['picks']
    newDF = pd.DataFrame(picks)
    pickData = newDF[['overallPickNumber', 'playerId', 'teamId']]
    pickData = pickData.replace({'teamId':ffTeams})
    mergedData = pd.merge(pickData, playerDF, how='inner', left_on='playerId', right_on='id') 
    mergedData = mergedData.replace({'proTeamId':nflTeams})
    return mergedData

def mapPlayerData(playerData):
    # Function to intake dataframe from API call and return football player data
    players = playerData['players']
    newDF = pd.DataFrame(players)
    playerDF = pd.DataFrame(newDF['player'])
    dfColumns = ['defaultPositionId', 'fullName', 'id', 'proTeamId', 'positionalRanking', 'totalRanking', 'totalRating']
    retDF = pd.DataFrame(columns=dfColumns)
    for index, row in playerDF.iterrows():
        id = newDF['id'][index]
        fullName = row['player']['fullName']
        defPosId = row['player']['defaultPositionId']
        proTeamId = row['player']['proTeamId']
        ratings = newDF['ratings'][index]
        # ESPN API sometimes returns 'NaN' for ratings data. If that's the case, we don't care about that entry
        if ratings == ratings:
            ratings = newDF['ratings'][index]['0']
            posRank = ratings['positionalRanking']
            totalRank = ratings['totalRanking']
            totalRating = ratings['totalRating']
            playerRow = pd.Series([defPosId, fullName, id, proTeamId, posRank, totalRank, totalRating], index=['defaultPositionId', 'fullName', 'id', 'proTeamId', 'positionalRanking', 'totalRanking', 'totalRating'])
            retDF = pd.concat([retDF, playerRow.to_frame().T], ignore_index=True)
    formattedPlayerData = retDF.replace({'defaultPositionId':positionMap})
    return formattedPlayerData

def mapNFLTeams(nflTeams):
    teamDict = {}
    nflTeamData = nflTeams['sports'][0]['leagues'][0]['teams']
    for team in nflTeamData:
        teamInfo = team['team']
        teamID = int(teamInfo['id'])
        teamName = teamInfo['name']
        teamDict[teamID] = teamName
    return teamDict

def getReplacementValues(draftData):
    repDict = {}
    for position in draftData['defaultPositionId'].unique():
        positionDF = draftData[draftData['defaultPositionId'] == position]
        maxRank = positionDF['positionalRanking'].max()
        repDict[position] = maxRank
    draftData['VORP'] = draftData.apply(lambda row: repDict[row['defaultPositionId']] - row['positionalRanking'], axis=1)
    draftData['NormalizedVORP'] = draftData.apply(lambda row: row['VORP'] / repDict[row['defaultPositionId']], axis=1)
    draftData['PickValue'] = (draftData['NormalizedVORP']) * (1 / draftData['overallPickNumber'])
    draftData['PickRank'] = draftData['PickValue'].rank(ascending=False)
    return draftData
    
def getCountValues(draftData):
    # Start off by getting # of each position taken in the draft
    wrCount = draftData['defaultPositionId'].value_counts()['WR']
    rbCount = draftData['defaultPositionId'].value_counts()['RB']
    qbCount = draftData['defaultPositionId'].value_counts()['QB']
    dstCount = draftData['defaultPositionId'].value_counts()['D/ST']
    teCount = draftData['defaultPositionId'].value_counts()['TE']
    kCount = draftData['defaultPositionId'].value_counts()['K']
    # Get the number of picks overall
    pickCount = draftData['overallPickNumber'].max()
    return [pickCount, qbCount, wrCount, rbCount, dstCount, teCount, kCount]

def evaluatePicks(draftData):
    replacementData = getReplacementValues(draftData)
    tpvArr = []
    for index, row in replacementData.iterrows():
        pickNum = row['overallPickNumber']
        totalRank = row['totalRanking']
        tpvArr.append((pickNum-totalRank))
    replacementData['totalPickValue'] = tpvArr
    return replacementData