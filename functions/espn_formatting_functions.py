# Regan Givens
# 8/24/23
# This py file contains functions regarding formatting data that has been pulled from the dataframes
import pandas as pd
import matplotlib.pyplot as mp
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
import functions.espn_data_functions as espnDataFunc

def plotData(evalData):
    teams = evalData.teamId.unique()
    for team in teams:
        teamEvalData = evalData[evalData['teamId'] == team]
        teamEvalData = teamEvalData[(teamEvalData['totalRanking'].notna()) & (teamEvalData['totalRanking'] != 0)]
        model = LinearRegression()
        X = teamEvalData[['totalRanking']]
        Y = teamEvalData[['overallPickNumber']]
        model.fit(X, Y)
        pickModel = model.predict(X)
        pickInt = '{:.2f}'.format(model.intercept_[0])
        modelCoef = '{:.2f}'.format(model.coef_[0][0])
        r2Val = r2_score(X, pickModel)
        r2Str = 'r^2 = {:.2f}'.format(r2Val)
        lineStr = f'y = {modelCoef}x + {pickInt}'
        mp.figure()
        mp.title(team)
        mp.xlabel('Estimated Pick Number')
        mp.ylabel('Actual Pick Number')
        mp.text(7, 185, r2Str, fontsize=12)
        mp.text(130, 4, lineStr, fontsize=12)
        mp.plot(X, Y, 'k. ')
        mp.plot(X, pickModel)
        mp.xlim(0,200)
        mp.ylim(0,200)
        mp.savefig('espn/'+str(team)+'.png')

def formatDraftTxtForWrite(dataArr, df, index, header):
    strDict = {'overallPickNumber': 'Overall Pick Number: ', 
               'fullName': 'Player: ',
               'teamId': 'Fantasy Team: ',
               'proTeamId': 'NFL Team: ', 
               'positionalRanking': 'Positional Ranking: ', 
               'totalRanking': 'Overall Ranking: ', 
               'totalPickValue': 'Total Pick Value: ',
               'PickRank': 'Pick Rank: ', 
               'PickValue': 'Pick Value: '
               }
    dataCols = list(strDict.keys())
    rowData = df.loc[index]
    dataArr.append('\n')
    dataArr.append(header)
    for col in dataCols:
        dataArr.append('\n')
        dataArr.append('\n')
        dataArr.append(strDict[col] + str(rowData[col]))
        dataArr.append('\n')
    dataArr.append('\n')
    return dataArr

def formatDraftCounts(dataArr, countArr):
    strDict = {0: 'Number of Picks: ',
               1: 'QBs Taken: ',
               2: 'WRs Taken: ',
               3: 'RBs Taken: ',
               4: 'D/STs Taken: ',
               5: 'TEs Taken: ',
               6: 'Ks Taken: '}
    for index in range(len(countArr)):
        dataArr.append('\n')
        dataArr.append(strDict[index] + str(countArr[index]))
    return dataArr

def draftText(draftData):
    evalData = espnDataFunc.evaluatePicks(draftData)
    evalData.to_csv('espn/evaluated_data.csv')
    plotData(evalData)
    positions = ['QB', 'WR', 'RB', 'K', 'D/ST', 'TE']
    dataArr = []
    for position in positions:
        filteredEvalData = evalData[evalData['defaultPositionId'] == position]
        filteredEvalData = filteredEvalData[(filteredEvalData['positionalRanking'].notna()) & (filteredEvalData['positionalRanking'] != 0)]
        filteredEvalData = filteredEvalData[(filteredEvalData['totalRanking'].notna()) & (filteredEvalData['totalRanking'] != 0)]
        maxPRIndex = filteredEvalData['PickRank'].idxmax()
        minPRIndex = filteredEvalData['PickRank'].idxmin()
        maxTPVIndex = filteredEvalData['totalPickValue'].idxmax()
        minTPVIndex = filteredEvalData['totalPickValue'].idxmin()
        dataArr.append('\n')
        dataArr.append(str(position))
        dataArr = formatDraftTxtForWrite(dataArr, evalData, maxPRIndex, 'Max PR')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, minPRIndex, 'Min PR')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, maxTPVIndex, 'Max TPV')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, minTPVIndex, 'Min TPV')
    
    countArr = espnDataFunc.getCountValues(draftData)
    dataArr = formatDraftCounts(dataArr, countArr)
    
    with open('espn/draftTxt.txt', 'w') as f:
        for line in dataArr:
            f.write(line)     

def slotIDReplace(idVal):
    if idVal == 20:
        return 'BENCH'
    else:
        return 'STARTER'

def buildRoster(rosterDF):
    rosterDF = rosterDF.sort_values(by=['Position']) # Sorting like this will always result in D/ST, K, QB, RB, WR
    rosterDF.loc[rosterDF['Slot ID'] != 20, 'Slot Value'] = 'STARTER' 
    rosterDF.loc[rosterDF['Slot ID'] == 20, 'Slot Value'] = 'BENCH' 
    playerArr = []
    retStarters = []
    retBench = []
    for index, player in rosterDF.iterrows():
        name = player['Player Name']
        if name not in playerArr:
            playerArr.append(name)
            position = player['Position']
            points = '{:.2f}'.format(float(player['Applied Total']))
            slot = player['Slot Value']
            if slot == 'STARTER':
                retStarters.append(f'\n{name} - {position} - {points}')
            else:
                retBench.append(f'\n{name} - {position} - {points}')
    return retStarters, retBench

def formatMatchup(match, dataArr):
    playerArrDict = {
        0: 'Slot ID',
        1: 'Player Name',
        2: 'Position',
        3: 'Player Actual Stats',
        4: 'Player Projected Stats'
    }
    dfHeaders = ['Slot ID', 'Player Name', 'Position', 'Applied Total', 'Player Actual Stats', 'Player Projected Stats']
    homeTeam = match['home team']
    homeScore = match['home score']
    homeRoster = match['home roster']
    homeDF = pd.DataFrame()
    for player in homeRoster:
        homeRow = pd.Series([player[0],player[1],player[2], player[3], player[4], player[5]], index=dfHeaders)
        homeDF = pd.concat([homeDF, homeRow.to_frame().T], ignore_index=True)

    awayTeam = match['away team']
    awayScore = match['away score']
    awayRoster = match['away roster']
    awayDF = pd.DataFrame()
    for player in awayRoster:
        awayRow =  pd.Series([player[0],player[1],player[2], player[3], player[4], player[5]], index=dfHeaders)
        awayDF = pd.concat([awayDF, awayRow.to_frame().T], ignore_index=True)
    
    matchStr = f'{homeTeam} vs. {awayTeam}'
    scoreStr = f'\n{homeScore} - {awayScore}'
    # From build roster the order is always D/ST, K, QB, RB, TE, WR
    awayRoster = buildRoster(awayDF)
    awayStarters = awayRoster[0]
    awayBench = awayRoster[1]
    homeRoster = buildRoster(homeDF)
    homeStarters = homeRoster[0]
    homeBench = homeRoster[1]

    dataArr.append(matchStr)
    dataArr.append(scoreStr)
    dataArr.append(f'\n{homeTeam} Starters:')
    for homePlayer in homeStarters:
        dataArr.append(homePlayer)
    dataArr.append('\n')
    dataArr.append(f'\n{homeTeam} Bench:')
    for homePlayer in homeBench:
        dataArr.append(homePlayer)
    dataArr.append('\n')
    dataArr.append(f'\n{awayTeam} Starters:')
    for awayPlayer in awayStarters:
        dataArr.append(awayPlayer)
    dataArr.append('\n')
    dataArr.append(f'\n{awayTeam} Bench:')
    for awayPlayer in awayBench:
        dataArr.append(awayPlayer)
    dataArr.append('\n\n')
    return dataArr
    
def matchupText(matchupData, week, leagueName):
    # Matchup Data at this point is an array of objects
    # Away Team
    # Away Score
    # Away Roster
        # Slot ID
        # Player Name
        # Position
        # Player Actual Stats 
        # Player Projected Stats
    # Home has same data
    # Winner
    dataArr = [f'Week {week} of {leagueName}\n']
    for match in matchupData:
        dataArr = formatMatchup(match, dataArr)

    fileStr = f'espn/{leagueName}_Week_{week}.txt'
    with open(fileStr, 'w') as f:
        for line in dataArr:
            f.write(line)