# Regan Givens
# 8/24/23
# This py file contains functions regarding formatting data that has been pulled from the dataframes
import pandas as pd
import copy
import matplotlib.pyplot as mp
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression

def getReplacementValues(draft_data):
    rep_values = {}
    for position in draft_data['defaultPositionId'].unique():
        position_df = draft_data[draft_data['defaultPositionId'] == position]
        max_rank = position_df['positionalRanking'].max()
        rep_values[position] = max_rank
    draft_data['VORP'] = draft_data.apply(lambda row: rep_values[row['defaultPositionId']] - row['positionalRanking'], axis=1)
    draft_data['NormalizedVORP'] = draft_data.apply(lambda row: row['VORP'] / rep_values[row['defaultPositionId']], axis=1)
    draft_data['PickValue'] = (draft_data['NormalizedVORP']) * (1 / draft_data['overallPickNumber'])
    draft_data['PickRank'] = draft_data['PickValue'].rank(ascending=False)
    return draft_data
    
def getCountValues(draft_data):
    # Start off by getting # of each position taken in the draft
    wr_taken = draft_data['defaultPositionId'].value_counts()['WR']
    rb_taken = draft_data['defaultPositionId'].value_counts()['RB']
    qb_taken = draft_data['defaultPositionId'].value_counts()['QB']
    d_st_taken = draft_data['defaultPositionId'].value_counts()['D/ST']
    te_taken = draft_data['defaultPositionId'].value_counts()['TE']
    k_taken = draft_data['defaultPositionId'].value_counts()['K']
    # Get the number of picks overall
    num_of_picks = draft_data['overallPickNumber'].max()
    return [num_of_picks, qb_taken, wr_taken, rb_taken, d_st_taken, te_taken, k_taken]

def evaluatePicks(draft_data):
    new_draft_data = getReplacementValues(draft_data)
    total_pick_arr = []
    for index, row in new_draft_data.iterrows():
        pick_num = row['overallPickNumber']
        totalRank = row['totalRanking']
        total_pick_arr.append((pick_num-totalRank))
    new_draft_data['totalPickValue'] = total_pick_arr
    return new_draft_data

def plotData(eval_data):
    teams = eval_data.teamId.unique()
    for team in teams:
        team_eval_data = eval_data[eval_data['teamId'] == team]
        team_eval_data = team_eval_data[(team_eval_data['totalRanking'].notna()) & (team_eval_data['totalRanking'] != 0)]
        model = LinearRegression()
        X = team_eval_data[['totalRanking']]
        Y = team_eval_data[['overallPickNumber']]
        model.fit(X, Y)
        predicted_pick = model.predict(X)
        coef_det = r2_score(X, predicted_pick)
        r2_str = 'r^2 = {:.2f}'.format(coef_det)
        mp.figure()
        mp.title(team)
        mp.xlabel('Estimated Pick Number')
        mp.ylabel('Actual Pick Number')
        mp.text(7, 185, r2_str, fontsize=12)
        mp.plot(X, Y, 'k. ')
        mp.plot(X, predicted_pick)
        mp.xlim(0,200)
        mp.ylim(0,200)
        mp.savefig('output/'+str(team)+'.png')

def formatTextForWrite(data_arr, df, index, header):
    row_data = df.loc[index]
    data_arr.append('\n')
    data_arr.append(header)
    data_arr.append('\n')
    data_arr.append('\n')
    data_arr.append('Overall Pick Number: ' + str(row_data['overallPickNumber']))
    data_arr.append('\n')
    data_arr.append('Player: ' + str(row_data['fullName']))
    data_arr.append('\n')
    data_arr.append('Fantasy Team: ' + str(row_data['teamId']))
    data_arr.append('\n')
    data_arr.append('NFL Team: ' + str(row_data['proTeamId']))
    data_arr.append('\n')
    data_arr.append('Positional Ranking: ' + str(row_data['positionalRanking']))
    data_arr.append('\n')
    data_arr.append('Overall Ranking: ' + str(row_data['totalRanking']))
    data_arr.append('\n')
    data_arr.append('Total Pick Value: ' + str(row_data['totalPickValue']))
    data_arr.append('\n')
    data_arr.append('Pick Rank: ' + str(row_data['PickRank']))
    data_arr.append('\n')
    data_arr.append('Pick Value: ' + str(row_data['PickValue']))
    data_arr.append('\n')
    data_arr.append('\n')
    return data_arr

def formatCounts(data_arr, count_arr):
    data_arr.append('\n')
    data_arr.append('Number of Picks: ' + str(count_arr[0]))
    data_arr.append('\n')
    data_arr.append('QBs Taken: ' + str(count_arr[1]))
    data_arr.append('\n')
    data_arr.append('WRs Taken: ' + str(count_arr[2]))
    data_arr.append('\n')
    data_arr.append('RBs Taken: ' + str(count_arr[3]))
    data_arr.append('\n')
    data_arr.append('D/STs Taken: ' + str(count_arr[4]))
    data_arr.append('\n')
    data_arr.append('TEs Taken: ' + str(count_arr[5]))
    data_arr.append('\n')
    data_arr.append('Ks Taken: ' + str(count_arr[6]))
    data_arr.append('\n')
    return data_arr

def draftText(draft_data):
    evaluation_data = evaluatePicks(draft_data)
    evaluation_data.to_csv('output/evaluated_data.csv')
    plotData(evaluation_data)
    positions = ['QB', 'WR', 'RB', 'K', 'D/ST', 'TE']
    data_arr = []
    for position in positions:
        filtered_eval_data = evaluation_data[evaluation_data['defaultPositionId'] == position]
        filtered_eval_data = filtered_eval_data[(filtered_eval_data['positionalRanking'].notna()) & (filtered_eval_data['positionalRanking'] != 0)]
        filtered_eval_data = filtered_eval_data[(filtered_eval_data['totalRanking'].notna()) & (filtered_eval_data['totalRanking'] != 0)]
        max_pr_index = filtered_eval_data['PickRank'].idxmax()
        min_pr_index = filtered_eval_data['PickRank'].idxmin()
        max_tpv_index = filtered_eval_data['totalPickValue'].idxmax()
        min_tpv_index = filtered_eval_data['totalPickValue'].idxmin()
        data_arr.append('\n')
        data_arr.append(str(position))
        data_arr = formatTextForWrite(data_arr, evaluation_data, max_pr_index, 'Max PR')
        data_arr = formatTextForWrite(data_arr, evaluation_data, min_pr_index, 'Min PR')
        data_arr = formatTextForWrite(data_arr, evaluation_data, max_tpv_index, 'Max TPV')
        data_arr = formatTextForWrite(data_arr, evaluation_data, min_tpv_index, 'Min TPV')
    
    count_arr = getCountValues(draft_data)
    data_arr = formatCounts(data_arr, count_arr)
    
    with open('output/draftTxt.txt', 'w') as f:
        for line in data_arr:
            f.write(line)     

def weeklyMatchupEmail(matchup_data):
    pass