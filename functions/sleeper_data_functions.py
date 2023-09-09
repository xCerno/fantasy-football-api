# Regan Givens
# 9/5/23
# This py file contains all data manipulation functions when it comes to dataframes created
# from the response of the Sleeper API.
import pandas as pd
import numpy as np

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
        #print(draftRow)
        draftDF = pd.concat([draftDF, draftRow.to_frame().T], ignore_index=True)
    return draftDF

def checkLastPlayerCall():
    pass

def mapPlayerData(playerData):
    pass