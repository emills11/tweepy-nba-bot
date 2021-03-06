import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, leaguestandings
pd.options.mode.chained_assignment = None  # default='warn'

TEAM_IDS = {'1610612737' : 'Hawks', '1610612738' : 'Celtics', '1610612739' : 'Cavaliers',
            '1610612740' : 'Pelicans', '1610612741' : 'Bulls', '1610612742' : 'Mavericks',
            '1610612743' : 'Nuggets', '1610612744' : 'Warriors', '1610612745' : 'Rockets',
            '1610612746' : 'Clippers', '1610612747' : 'Lakers', '1610612748' : 'Heat',
            '1610612749' : 'Bucks', '1610612750' : 'Timberwolves', '1610612751' : 'Nets',
            '1610612752' : 'Knicks', '1610612753' : 'Magic', '1610612754' : 'Pacers',
            '1610612755' : '76ers', '1610612756' : 'Suns', '1610612757' : 'Trail Blazers',
            '1610612758' : 'Kings', '1610612759' : 'Spurs', '1610612760' : 'Thunder',
            '1610612761' : 'Raptors', '1610612762' : 'Jazz', '1610612763' : 'Grizzlies',
            '1610612764' : 'Wizards', '1610612765' : 'Pistons', '1610612766' : 'Hornets'}

def combine_team_games(df, keep_method='home'):
    '''Combine a TEAM_ID-GAME_ID unique table into rows by game. Slow.

        Parameters
        ----------
        df : Input DataFrame.
        keep_method : {'home', 'away', 'winner', 'loser', ``None``}, default 'home'
            - 'home' : Keep rows where TEAM_A is the home team.
            - 'away' : Keep rows where TEAM_A is the away team.
            - 'winner' : Keep rows where TEAM_A is the losing team.
            - 'loser' : Keep rows where TEAM_A is the winning team.
            - ``None`` : Keep all rows. Will result in an output DataFrame the same
                length as the input DataFrame.
                
        Returns
        -------
        result : DataFrame
    '''
    # Join every row to all others with the same game ID.
    joined = pd.merge(df, df, suffixes=['_A', '_B'],
                    on=['SEASON_ID', 'GAME_ID', 'GAME_DATE'])
    # Filter out any row that is joined to itself.
    result = joined[joined.TEAM_ID_A != joined.TEAM_ID_B]
    # Take action based on the keep_method flag.
    if keep_method is None:
        # Return all the rows.
        pass
    elif keep_method.lower() == 'home':
        # Keep rows where TEAM_A is the home team. 
        result = result[result.MATCHUP_A.str.contains(' vs. ')]
    elif keep_method.lower() == 'away':
        # Keep rows where TEAM_A is the away team.
        result = result[result.MATCHUP_A.str.contains(' @ ')]
    elif keep_method.lower() == 'winner':
        result = result[result.WL_A == 'W']
    elif keep_method.lower() == 'loser':
        result = result[result.WL_A == 'L']
    else:
        raise ValueError(f'Invalid keep_method: {keep_method}')
    return result


def retrieve_team_records():
    # Access endpoint for current NBA standings
    ls = leaguestandings.LeagueStandings()
    standings = ls.get_data_frames()[0]
    # Only select useful columns from DataFrame
    standings = standings[['TeamID', 'TeamName', 'Record']]
    return standings


def retrieve_games(date):
    print("Retrieving games...")

    # Access endpoint for all NBA games and select first 30
    gamefinder = leaguegamefinder.LeagueGameFinder()
    games = gamefinder.get_data_frames()[0].iloc[:30]

    # Only select today's games
    games = games[games.GAME_DATE == date]

    # Drop games that are still in progress or are that part of a different league
    for index, row in games.iterrows():
        if row['WL'] == None or str(row['TEAM_ID']) not in TEAM_IDS:
            games = games.drop([index])

    # Sort games by most recent game id and combine into A/B format,
    # since each game has two indexes (one for each team)
    games = games.sort_values('GAME_ID', ascending=False)
    games = combine_team_games(df=games, keep_method='winner')

    # Get standings and initialize record columns
    standings = retrieve_team_records()
    games['RECORD_A'] = '0-0'
    games['RECORD_B'] = '0-0'
    
    # Iterate through games and set records of each team accordingly
    for index, row in games.iterrows():
        team_record_a = standings.loc[standings.TeamID == row['TEAM_ID_A']]['Record'].iloc[0]
        games.at[index, 'RECORD_A'] = team_record_a

        team_record_b = standings.loc[standings.TeamID == row['TEAM_ID_B']]['Record'].iloc[0]
        games.at[index, 'RECORD_B'] = team_record_b

    # Filter out stats-related info that is not useful
    games_results = games[['GAME_ID', 'TEAM_ID_A', 'TEAM_NAME_A', 'RECORD_A', 'PTS_A', 'TEAM_ID_B', 'TEAM_NAME_B', 'RECORD_B', 'PTS_B']]
    # Make sure leading zeros are kept in games ids when writing to csv
    games_results['GAME_ID'] = games_results['GAME_ID'].astype('str')
    return games_results
