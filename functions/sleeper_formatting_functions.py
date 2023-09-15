# Regan Givens
# 9/5/23
# This py file contains functions regarding formatting data that has been pulled from the dataframes
import pandas as pd
import matplotlib.pyplot as mp
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
import functions.sleeper_data_functions as sleepDataFunc

def plotData(evalData):
    teams = evalData['Team Name'].unique()
    for team in teams:
        teamEvalData = evalData[evalData['Team Name'] == team]
        teamEvalData = teamEvalData[(teamEvalData['totalRanking'].notna()) & (teamEvalData['totalRanking'] != 0)]
        teamEvalData['Pick Number'] = teamEvalData['Pick Number'].astype('int')
        maxPickNum = teamEvalData['Pick Number'].idxmax()
        maxPickNum = maxPickNum + 25
        if maxPickNum < 200:
            maxPickNum = 200
        teamEvalData['totalRanking'] = teamEvalData['totalRanking'].astype('float')
        maxTotalRank = teamEvalData['totalRanking'].idxmax()
        maxTotalRank = maxTotalRank + 25
        if maxTotalRank < 200:
            maxTotalRank = 200
        model = LinearRegression()
        X = teamEvalData[['totalRanking']]
        Y = teamEvalData[['Pick Number']]
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
        mp.xlim(0,maxPickNum)
        mp.ylim(0,maxTotalRank)
        mp.savefig('sleeper/'+str(team)+'.png')

def formatDraftTxtForWrite(dataArr, df, index, header):
    strDict = {'Pick Number': 'Overall Pick Number: ', 
               'Full Name': 'Player: ',
               'Team Name': 'Fantasy Team: ',
               'NFL Team': 'NFL Team: ', 
               'positionalRanking': 'Positional Ranking: ', 
               'totalRanking': 'Overall Ranking: ', 
               'Total Pick Value': 'Total Pick Value: ',
               'Pick Rank': 'Pick Rank: ', 
               'Pick Value': 'Pick Value: '
               }
    dataCols = list(strDict.keys())
    rowData = df.loc[index]
    dataArr.append('\n')
    dataArr.append(header)
    dataArr.append('\n')
    for col in dataCols:
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

def draftText(evalData):
    evalData.to_csv('sleeper/evaluated_data.csv')
    positions = list(evalData['Position'].unique())
    plotData(evalData)
    dataArr = []
    for position in positions:
        filteredEvalData = evalData[evalData['Position'] == position]
        filteredEvalData = filteredEvalData[(filteredEvalData['positionalRanking'].notna()) & (filteredEvalData['positionalRanking'] != 0)]
        filteredEvalData = filteredEvalData[(filteredEvalData['totalRanking'].notna()) & (filteredEvalData['totalRanking'] != 0)]
        maxPRIndex = filteredEvalData['Pick Rank'].idxmax()
        minPRIndex = filteredEvalData['Pick Rank'].idxmin()
        maxTPVIndex = filteredEvalData['Total Pick Value'].idxmax()
        minTPVIndex = filteredEvalData['Total Pick Value'].idxmin()
        if position != 'WR':
            dataArr.append('\n')
        dataArr.append(str(position))
        dataArr = formatDraftTxtForWrite(dataArr, evalData, maxPRIndex, 'Max PR')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, minPRIndex, 'Min PR')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, maxTPVIndex, 'Max TPV')
        dataArr = formatDraftTxtForWrite(dataArr, evalData, minTPVIndex, 'Min TPV')
    
    countArr = sleepDataFunc.getCountValues(evalData)
    dataArr = formatDraftCounts(dataArr, countArr)
    
    with open('sleeper/draftTxt.txt', 'w') as f:
        for line in dataArr:
            f.write(line)     

def weeklyMatchupEmail(matchupData):
    pass