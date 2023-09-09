# Regan Givens
# 9/5/23
# This py file contains all data manipulation functions when it comes to dataframes created
# from the response of the Sleeper API.
import pandas as pd
import numpy as np

nflTeams = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LV": "Las Vegas Raiders",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers",
    "SEA": "Seattle Seahawks",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders"
}

nflTeamsDST = {
    "Cardinals D/ST": "Arizona Cardinals",
    "Falcons D/ST": "Atlanta Falcons",
    "Ravens D/ST": "Baltimore Ravens",
    "Bills D/ST": "Buffalo Bills",
    "Panthers D/ST": "Carolina Panthers",
    "Bears D/ST": "Chicago Bears",
    "Bengals D/ST": "Cincinnati Bengals",
    "Browns D/ST": "Cleveland Browns",
    "Cowboys D/ST": "Dallas Cowboys",
    "Broncos D/ST": "Denver Broncos",
    "Lions D/ST": "Detroit Lions",
    "Packers D/ST": "Green Bay Packers",
    "Texans D/ST": "Houston Texans",
    "Colts D/ST": "Indianapolis Colts",
    "Jaguars D/ST": "Jacksonville Jaguars",
    "Chiefs D/ST": "Kansas City Chiefs",
    "Raiders D/ST": "Las Vegas Raiders",
    "Chargers D/ST": "Los Angeles Chargers",
    "Rams D/ST": "Los Angeles Rams",
    "Dolphins D/ST": "Miami Dolphins",
    "Vikings D/ST": "Minnesota Vikings",
    "Patriots D/ST": "New England Patriots",
    "Saints D/ST": "New Orleans Saints",
    "Giants D/ST": "New York Giants",
    "Jets D/ST": "New York Jets",
    "Eagles D/ST": "Philadelphia Eagles",
    "Steelers D/ST": "Pittsburgh Steelers",
    "49ers D/ST": "San Francisco 49ers",
    "Seahawks D/ST": "Seattle Seahawks",
    "Buccaneers D/ST": "Tampa Bay Buccaneers",
    "Titans D/ST": "Tennessee Titans",
    "Commanders D/ST": "Washington Commanders"
}

# Need to write players to a file to reference. Only need to update players file weekly at most.

def mapLeagueData(genData):
    genDF = pd.DataFrame()
    dfHeaders = ['Name', 'League ID', 'Draft ID', 'Total Rosters']
    dictKeys = ['name', 'league_id', 'draft_id', 'total_rosters']
    genRow = pd.Series([genData[dictKeys[0]], genData[dictKeys[1]], genData[dictKeys[2]], genData[dictKeys[3]]], index=dfHeaders)
    genDF = pd.concat([genDF, genRow.to_frame().T], ignore_index=True)
    return genDF

def mapUsersData(userData):
    userDF = pd.DataFrame()
    dfHeaders = ['User ID', 'Display Name', 'Team Name']
    dictKeys = ['user_id', 'display_name', 'metadata', 'team_name']
    for item in userData:
        metaDict = item[dictKeys[2]]
        metaKeys = list(metaDict.keys())
        if 'team_name' in metaKeys:
            userRow = pd.Series([item[dictKeys[0]], item[dictKeys[1]], metaDict[dictKeys[3]]], index=dfHeaders)
            userDF = pd.concat([userDF, userRow.to_frame().T], ignore_index=True)
        else:
            userRow = pd.Series([item[dictKeys[0]], item[dictKeys[1]], item[dictKeys[1]]], index=dfHeaders)
            userDF = pd.concat([userDF, userRow.to_frame().T], ignore_index=True)
    return userDF

def mapDraftPicks(draftData, userDF):
    draftDF = pd.DataFrame()
    dfHeaders = ['Round', 'Pick Number', 'Player ID', 'Team Name', 'Roster ID', 'Is Keeper', 'NFL Team', 'Full Name', 'Position']
    dictKeys = ['round', 'pick_no', 'player_id', 'picked_by', 'roster_id', 'is_keeper']
    metaKeys = ['team', 'first_name', 'last_name', 'position']
    for item in draftData:
        seriesArr = []
        for dictKey in dictKeys:
            if dictKey == 'picked_by':
                pickID = item[dictKey]
                userInfo = userDF.loc[userDF['User ID'] == pickID]
                teamName = userInfo.iloc[0]['Team Name']
                seriesArr.append(teamName)
            else:
                seriesArr.append(item[dictKey])
        metaDict = item['metadata']
        fullName = ''
        for metaKey in metaKeys:
            if metaKey == 'first_name':
                fullName = metaDict[metaKey]
            elif metaKey == 'last_name':
                fullName = fullName + ' ' + metaDict[metaKey]
                seriesArr.append(fullName)
            else:
                seriesArr.append(metaDict[metaKey])
        draftRow = pd.Series(seriesArr, index=dfHeaders)
        draftDF = pd.concat([draftDF, draftRow.to_frame().T], ignore_index=True)
    return draftDF

def pickRankEval(mergedDF):
    repDict = {}
    for position in mergedDF['Position'].unique():
        positionDF = mergedDF[mergedDF['Position'] == position]
        maxRank = positionDF['positionalRanking'].max()
        repDict[position] = maxRank
    mergedDF['VORP'] = mergedDF.apply(lambda row: repDict[row['Position']] - row['positionalRanking'], axis=1)
    mergedDF['Normalized VORP'] = mergedDF.apply(lambda row: row['VORP'] / repDict[row['Position']], axis=1)
    mergedDF['Pick Value'] = (mergedDF['Normalized VORP']) * (1 / mergedDF['Pick Number'])
    mergedDF['Pick Rank'] = mergedDF['Pick Value'].rank(ascending=False)
    return mergedDF

def tpvEval(mergedDF):
    mergedDF = pickRankEval(mergedDF)
    tpvArr = []
    for index, row in mergedDF.iterrows():
        pickNum = row['Pick Number']
        totalRank = row['totalRanking']
        tpvArr.append((pickNum-totalRank))
    mergedDF['Total Pick Value'] = tpvArr
    return mergedDF

def evaluatePicks(draftDF, playerDF):
    draftDF = draftDF.replace({'NFL Team':nflTeams})
    playerDF = playerDF.replace({'fullName': nflTeamsDST})
    playerDF = playerDF.drop(['defaultPositionId', 'proTeamId', 'id'], axis=1)
    mergedDF = pd.merge(draftDF, playerDF, how='inner', left_on='Full Name', right_on='fullName')
    mergedDF = tpvEval(mergedDF)
    return mergedDF

def getCountValues(draftData):
    # Start off by getting # of each position taken in the draft
    wrCount = draftData['Position'].value_counts()['WR']
    rbCount = draftData['Position'].value_counts()['RB']
    qbCount = draftData['Position'].value_counts()['QB']
    dstCount = draftData['Position'].value_counts()['DEF']
    teCount = draftData['Position'].value_counts()['TE']
    kCount = draftData['Position'].value_counts()['K']
    # Get the number of picks overall
    pickCount = draftData['Pick Number'].max()
    return [pickCount, qbCount, wrCount, rbCount, dstCount, teCount, kCount]