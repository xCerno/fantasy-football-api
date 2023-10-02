# Regan Givens
# 8/24/23
# This py file calls the necessary APIs and convers the json returns to dataframes to be manipulated
import requests
import pandas as pd
import numpy as np
import espn_league_info
import espn_team_info
import json
import matplotlib.pyplot as mp
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression


class espnAPILeague:
    
    def __init__(self):
        self.leagueID = espn_league_info.leagueID
        self.year = espn_league_info.year
        self.espnS2 = espn_league_info.espnS2
        self.swid = espn_league_info.swid
        
        self.positionMap = {
        1: 'QB',
        2: 'RB',
        3: 'WR',
        4: 'TE',
        5: 'K',
        16: 'D/ST'
        }

        self.statMap = {
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
        self.ffTeamsDict = espn_team_info.teams

        self.cookies = {'swid':self.swid, 'espn_s2':self.espnS2}

        # ESPN FF API URL - Customizing the request view below will return different results
        self.ffURL = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leagues/{self.leagueID}'
        
        # ESPN Match URL
        self.matchURL = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leagues/{self.leagueID}?view=mMatchup&view=mMatchupScore'
        
        # ESPN Players API URL
        self.playerURL = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leaguedefaults/3?view=kona_player_info'
        
        # ESPN Team API URL
        self.teamURL = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams'

    def callESPNAPI(self, reqData = None, week = None):
        # This function will call the ESPN Fantasy Football API and return the json response
        # Params - Requested Data - This is the data requested to be shown, defaulted to None
        # Return - df - A dataframe of the json response data from the API

        # Based on the requested data, configure the params and url to use 
        if reqData == 'matchup':
            params = {}
            if week is not None:
                params['scoringPeriodId'] = week
            apiURL = self.matchURL
        elif reqData == 'draft':
            params = {'view':'mDraftDetail'}
            apiURL = self.ffURL
        elif reqData == 'team':
            params = {}
            apiURL = self.teamURL
        elif reqData == 'player':
            # Because Player data requires unique filtering and headers, we return it in the elif
            filters = { "players": { "limit": 2000, "sortPercOwned":{"sortPriority":4,"sortAsc":False}}}
            headers = {'x-fantasy-filter': json.dumps(filters)}
            response = requests.get(self.playerURL, headers=headers)
            resData = response.json()
            return resData
        else:
            params = {}
            apiURL = self.ffURL
        
        # Call the API with the URL and params selected
        response = requests.get(apiURL, cookies=self.cookies, params=params)
        resData = response.json()
        return resData

    def getLeagueName(self, genData):
        # Function to return the fantasy football league's name
        leagueName = genData['settings']['name']
        return leagueName

    def currentWeek(self, matchupData):
        # Function to intake a response from the API and return the current week (scoringPeriodId)
        # Grab the current week INT from the matchup data
        currWeek = matchupData['scoringPeriodId']
        # Check to make sure we're not outside of the standard 17 week FF League
        if currWeek > 17:
            currWeek = 17
        # Return the int
        return currWeek

    def mapTeams(self, genData):
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

    def getRosterInfo(self, rosterData, teamID, week):
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
                    position = self.positionMap[positionID]
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
                                if actStat in self.statMap:
                                    playerActStats[self.statMap[actStat]] = actualStats[actStat]
                        elif stat['scoringPeriodId'] == week and stat['statSourceId'] == 1 and stat['stats'] != {}:
                            #appliedTot = stat['appliedTotal']
                            projectedStats = stat['stats']
                            #playerProjStats = {}
                            for projStat in projectedStats:
                                if projStat in self.statMap:
                                    playerProjStats[self.statMap[projStat]] = projectedStats[projStat]
                    rosterArr.append([slotID, playerName, position, appliedTot, playerActStats, playerProjStats])
                break
        return rosterArr


    def getMatchupResults(self, match, teamData, rosterData, week):
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
                awayRoster = self.getRosterInfo(rosterData, awayID, week)
            if homeID == teams:
                homeTeam = teamData[teams]
                homeRoster = self.getRosterInfo(rosterData, homeID, week)
            if homeTeam != '' and awayTeam != '':
                break

        # Return a single dictionary of the data we need    
        return {'away team': awayTeam, 'away score': awayScore, 'away roster':awayRoster, 'home team': homeTeam, 'home score': homeScore, 'home roster': homeRoster, 'winner': winner}
        
    def mapSchedule(self, matchupData, teamData, week=None):
        # Function to intake a dataframe for matches and an array of dictionaries for teams and return the week results for the current week
        # Initialize an array to hold the matchup data to be returned
        matchArr = []
        # Grab the schedule data from the API response dataframe
        scheduleData = matchupData['schedule']
        # Grab the FF Teams Data which holds rosters for a given week
        teamRosters = matchupData['teams']
        # Get the current week of fantasy football from the matchup data
        if week is None:    
            currWeek = self.currentWeek(matchupData)
        else:
            currWeek = week
        # Loop through the schedule data to generate the home and away teams, how many points they scored, and who won
        for match in scheduleData:
            # Get the week value
            week = match['matchupPeriodId']
            # If the week matches the current week, continue
            if week == currWeek:
                # Get the match dictionary from getMatchupResults function above
                matchDict = self.getMatchupResults(match, teamData, teamRosters, week)
                # Append the match dict to the match arr
                matchArr.append(matchDict)
        # Return the array       
        return matchArr       

    def mapDraft(self, draftData, playerDF, ffTeams, nflTeams):
        # Function to intake a dataframe and return the draft information
        # Break dataframe down further with relevant info and return it
        picks = draftData['draftDetail']['picks']
        newDF = pd.DataFrame(picks)
        pickData = newDF[['overallPickNumber', 'playerId', 'teamId']]
        pickData = pickData.replace({'teamId':ffTeams})
        mergedData = pd.merge(pickData, playerDF, how='inner', left_on='playerId', right_on='id') 
        mergedData = mergedData.replace({'proTeamId':nflTeams})
        return mergedData

    def mapPlayerData(self, playerData):
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
        formattedPlayerData = retDF.replace({'defaultPositionId':self.positionMap})
        return formattedPlayerData

    def mapNFLTeams(self, nflTeams):
        teamDict = {}
        nflTeamData = nflTeams['sports'][0]['leagues'][0]['teams']
        for team in nflTeamData:
            teamInfo = team['team']
            teamID = int(teamInfo['id'])
            teamName = teamInfo['name']
            teamDict[teamID] = teamName
        return teamDict

    def getReplacementValues(self, draftData):
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
        
    def getCountValues(self, draftData):
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

    def evaluatePicks(self, draftData):
        replacementData = self.getReplacementValues(draftData)
        tpvArr = []
        for index, row in replacementData.iterrows():
            pickNum = row['overallPickNumber']
            totalRank = row['totalRanking']
            tpvArr.append((pickNum-totalRank))
        replacementData['totalPickValue'] = tpvArr
        return replacementData

    def plotData(self, evalData):
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

    def formatDraftTxtForWrite(self, dataArr, df, index, header):
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

    def formatDraftCounts(self, dataArr, countArr):
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

    def draftText(self, draftData):
        evalData = self.evaluatePicks(draftData)
        evalData.to_csv('espn/evaluated_data.csv')
        self.plotData(evalData)
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
            dataArr = self.formatDraftTxtForWrite(dataArr, evalData, maxPRIndex, 'Max PR')
            dataArr = self.formatDraftTxtForWrite(dataArr, evalData, minPRIndex, 'Min PR')
            dataArr = self.formatDraftTxtForWrite(dataArr, evalData, maxTPVIndex, 'Max TPV')
            dataArr = self.formatDraftTxtForWrite(dataArr, evalData, minTPVIndex, 'Min TPV')
        
        countArr = self.getCountValues(draftData)
        dataArr = self.formatDraftCounts(dataArr, countArr)
        
        with open('espn/draftTxt.txt', 'w') as f:
            for line in dataArr:
                f.write(line)     

    def slotIDReplace(self, idVal):
        if idVal == 20:
            return 'BENCH'
        else:
            return 'STARTER'

    def buildRoster(self, rosterDF):
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

    def bestTeam(self, rosterDF):
        # Full team is QB, RB1, RB2, WR1, WR2, TE, FLEX, D/ST, K
        # Flex can be WR, RB, TE
        rosterDF = rosterDF.sort_values(by=['Position', 'Applied Total'], ascending=[True, False]) # Sorting like this will always result in D/ST, K, QB, RB, WR
        playerArr = []
        bestTeam = {}
        for index, player in rosterDF.iterrows():
            name = player['Player Name']
            if name not in playerArr:
                playerArr.append(name)
                position = player['Position']
                points = float(player['Applied Total'])
                pointArr = [name, points]
                if position in ['QB', 'D/ST', 'K'] and position not in bestTeam.keys():
                    bestTeam[position] = pointArr
                elif position == 'WR':
                    if 'WR1' not in bestTeam.keys():
                        bestTeam['WR1'] = pointArr
                    elif 'WR2' not in bestTeam.keys():
                        bestTeam['WR2'] = pointArr
                    elif 'FLEX' not in bestTeam.keys():
                        bestTeam['FLEX'] = pointArr
                    else:
                        wrOne = bestTeam['WR1'][1]
                        wrTwo = bestTeam['WR2'][1]
                        flex = bestTeam['FLEX'][1]
                        if points > wrOne:
                            bestTeam['WR1'] = pointArr
                        elif points > wrTwo:
                            bestTeam['WR2'] = pointArr
                        elif points > flex:
                            bestTeam['FLEX'] = pointArr
                elif position == 'RB':
                    if 'RB1' not in bestTeam.keys():
                        bestTeam['RB1'] = pointArr
                    elif 'RB2' not in bestTeam.keys():
                        bestTeam['RB2'] = pointArr
                    elif 'FLEX' not in bestTeam.keys():
                        bestTeam['FLEX'] = pointArr
                    else:
                        rbOne = bestTeam['RB1'][1]
                        rbTwo = bestTeam['RB2'][1]
                        flex = bestTeam['FLEX'][1]
                        if points > rbOne:
                            bestTeam['RB1'] = pointArr
                        elif points > rbTwo:
                            bestTeam['RB2'] = pointArr
                        elif points > flex:
                            bestTeam['FLEX'] = pointArr
                elif position == 'TE':
                    if 'TE' not in bestTeam.keys():
                        bestTeam['TE'] = pointArr
                    elif 'FLEX' not in bestTeam.keys():
                        bestTeam['FLEX'] = pointArr
                    else:
                        teOne = bestTeam['TE'][1]
                        flex = bestTeam['FLEX'][1]
                        if points > teOne:
                            bestTeam['TE'] = pointArr
                        elif points > flex:
                           bestTeam['FLEX'] = pointArr
        bestPoints = 0
        for playPos in bestTeam.keys():
            bestPoints += bestTeam[playPos][1]
        return bestPoints

    def formatMatchup(self, match, dataArr):
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
        awayRoster = self.buildRoster(awayDF)
        awayBest = self.bestTeam(awayDF)
        awayEff = (awayScore/awayBest)*100
        awayEff = '{:.2f}%'.format(float(awayEff))
        awayStarters = awayRoster[0]
        awayBench = awayRoster[1]
        homeRoster = self.buildRoster(homeDF)
        homeBest = self.bestTeam(homeDF)
        homeEff = (homeScore/homeBest)*100
        homeEff = '{:.2f}%'.format(float(homeEff))
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
        dataArr.append(f'\n{homeTeam} Best Score: {homeBest}')
        dataArr.append(f'\n{homeTeam} Efficiency: {homeEff}')
        dataArr.append('\n')
        dataArr.append(f'\n{awayTeam} Starters:')
        for awayPlayer in awayStarters:
            dataArr.append(awayPlayer)
        dataArr.append('\n')
        dataArr.append(f'\n{awayTeam} Bench:')
        for awayPlayer in awayBench:
            dataArr.append(awayPlayer)
        dataArr.append('\n')
        dataArr.append(f'\n{awayTeam} Best Score: {awayBest}')
        dataArr.append(f'\n{awayTeam} Efficiency: {awayEff}')
        dataArr.append('\n\n')
        return dataArr
        
    def matchupText(self, matchupData, week, leagueName):
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
            dataArr = self.formatMatchup(match, dataArr)

        fileStr = f'espn/{leagueName}_Week_{week}.txt'
        with open(fileStr, 'w') as f:
            for line in dataArr:
                f.write(line)    

    def run(self, weekVal, draftOpt = None):
        genData = self.callESPNAPI()
        leagueName = self.getLeagueName(genData)

        # As of 8/29/23, API is not properly returning correct team names.
        # Function below commented out until properly functioning
        # ff_teams = self.mapTeams(gen_data)
        ffTeams = self.ffTeamsDict

        nflData = self.callESPNAPI('team')
        nflDF = self.mapNFLTeams(nflData)

        playerData = self.callESPNAPI('player')
        playerDF = self.mapPlayerData(playerData)

        if draftOpt in ['Y', 'y', 'Yes', 'YES', 'yes']:
            draftData = self.callESPNAPI('draft')
            draftDF = self.mapDraft(draftData, playerDF, ffTeams, nflDF)
            self.draftText(draftDF)
        matchupData = self.callESPNAPI('matchup', week = weekVal)
        currSchedule = self.mapSchedule(matchupData, ffTeams, weekVal)
        self.matchupText(currSchedule, weekVal, leagueName)