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
        coefDet = r2_score(X, pickModel)
        r2Str = 'r^2 = {:.2f}'.format(coefDet)
        mp.figure()
        mp.title(team)
        mp.xlabel('Estimated Pick Number')
        mp.ylabel('Actual Pick Number')
        mp.text(7, 185, r2Str, fontsize=12)
        mp.plot(X, Y, 'k. ')
        mp.plot(X, pickModel)
        mp.xlim(0,200)
        mp.ylim(0,200)
        mp.savefig('output/'+str(team)+'.png')

def formatDraftTxtForWrite(dataArr, df, index, header):
    dataCols = ['overallPickNumber', 'fullName', 'teamId', 'proTeamId', 'positionalRanking', 'totalRanking', 'totalPickValue', 'PickRank', 'PickValue']
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
    evalData.to_csv('output/evaluated_data.csv')
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
    
    with open('output/draftTxt.txt', 'w') as f:
        for line in dataArr:
            f.write(line)     

def weeklyMatchupEmail(matchupData):
    pass