# Regan Givens
# 8/24/23
# This py file contains functions regarding formatting data that has been pulled from the dataframes
import pandas as pd
import matplotlib.pyplot as mp
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
import functions.espn_data_functions as dataFunc

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

def formatTextForWrite(dataArr, df, index, header):
    rowData = df.loc[index]
    dataArr.append('\n')
    dataArr.append(header)
    dataArr.append('\n')
    dataArr.append('\n')
    dataArr.append('Overall Pick Number: ' + str(rowData['overallPickNumber']))
    dataArr.append('\n')
    dataArr.append('Player: ' + str(rowData['fullName']))
    dataArr.append('\n')
    dataArr.append('Fantasy Team: ' + str(rowData['teamId']))
    dataArr.append('\n')
    dataArr.append('NFL Team: ' + str(rowData['proTeamId']))
    dataArr.append('\n')
    dataArr.append('Positional Ranking: ' + str(rowData['positionalRanking']))
    dataArr.append('\n')
    dataArr.append('Overall Ranking: ' + str(rowData['totalRanking']))
    dataArr.append('\n')
    dataArr.append('Total Pick Value: ' + str(rowData['totalPickValue']))
    dataArr.append('\n')
    dataArr.append('Pick Rank: ' + str(rowData['PickRank']))
    dataArr.append('\n')
    dataArr.append('Pick Value: ' + str(rowData['PickValue']))
    dataArr.append('\n')
    dataArr.append('\n')
    return dataArr

def formatCounts(dataArr, countArr):
    dataArr.append('\n')
    dataArr.append('Number of Picks: ' + str(countArr[0]))
    dataArr.append('\n')
    dataArr.append('QBs Taken: ' + str(countArr[1]))
    dataArr.append('\n')
    dataArr.append('WRs Taken: ' + str(countArr[2]))
    dataArr.append('\n')
    dataArr.append('RBs Taken: ' + str(countArr[3]))
    dataArr.append('\n')
    dataArr.append('D/STs Taken: ' + str(countArr[4]))
    dataArr.append('\n')
    dataArr.append('TEs Taken: ' + str(countArr[5]))
    dataArr.append('\n')
    dataArr.append('Ks Taken: ' + str(countArr[6]))
    dataArr.append('\n')
    return dataArr

def draftText(draftData):
    evalData = dataFunc.evaluatePicks(draftData)
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
        dataArr = formatTextForWrite(dataArr, evalData, maxPRIndex, 'Max PR')
        dataArr = formatTextForWrite(dataArr, evalData, minPRIndex, 'Min PR')
        dataArr = formatTextForWrite(dataArr, evalData, maxTPVIndex, 'Max TPV')
        dataArr = formatTextForWrite(dataArr, evalData, minTPVIndex, 'Min TPV')
    
    countArr = dataFunc.getCountValues(draftData)
    dataArr = formatCounts(dataArr, countArr)
    
    with open('output/draftTxt.txt', 'w') as f:
        for line in dataArr:
            f.write(line)     

def weeklyMatchupEmail(matchupData):
    pass