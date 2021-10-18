import requests
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import difflib
#import matplotlib.pyplot as plt

# input a player
# gather the team
# gather the teams schedule. For each game, gather the box score
# each game is a row in a dataframe for the player
# how many games has the player actually played in? Call the player api for games played, goals, and assists.
# graph points over each game (cumulative), Plot points per game, injury/usage rate

def get_season_stats(player, team, syear):
  teams = requests.get('https://statsapi.web.nhl.com/api/v1/teams',timeout=15).json()

  year = int(syear[:4])

  teamnames = [each['teamName'] for each in teams['teams']]
  #print(teamnames)

  if team not in teamnames:
    raise Exception('bad team name: is this team in the NHL?')
  
  teamdict = next(item for item in teams['teams'] if item["teamName"] == team)

  roster = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(teamdict['id']), timeout=15).json()

  rosterplayers = [each['person']['fullName'] for each in roster['roster']]
  print(rosterplayers)

  if player not in rosterplayers:
    close_matches = difflib.get_close_matches(player, rosterplayers)

    if len(close_matches) == 0:
      emsg = 'bad player name: is this player on this team?'
    else:
      potential_player = close_matches[0]
      emsg = 'bad player name: did you mean {}?'.format(potential_player)
    raise Exception(emsg)


  playerdict = next(item for item in roster['roster'] if item['person']["fullName"] == player)

  playerid = playerdict['person']['id']

  #print(teamdict)
  #print(playerdict)

  schedule = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?teamId={tid}&startDate={sy}-09-01&endDate={ey}-08-01'.format(tid=teamdict['id'],sy=year, ey=int(year)+ 1), timeout=15).json()

  init_games = [each['games'][0] for each in schedule['dates']]

  game_ids = [{'id': each['gamePk'], 'host_status': 'home' if each['teams']['home']['team']['id'] == teamdict['id'] else 'away'} for each in init_games if each['gameType'] == 'R' and each['status']['detailedState'] == 'Final']

  if game_ids == []:
    raise Exception('Season has not started')
  
  
  season = []
  for gamenum, each in enumerate(game_ids):
    gid = each['id']
    host = each['host_status']

    thegame = requests.get('https://statsapi.web.nhl.com/api/v1/game/{}/boxscore'.format(gid), timeout=15).json()

    teamgame = thegame['teams'][host]

    played = True if playerid not in teamgame['scratches'] and 'ID' + str(playerid) in teamgame['players'] else False

    if played:

      #try:
      retframe = teamgame['players']['ID' + str(playerid)]['stats']['skaterStats']
      #except:
        # print(played)
        # print(thegame['teams'][host]['skaters'])
        # return thegame['teams'][host]

      retframe['gameNumber'] = gamenum + 1
      retframe['played'] = played

      season.append(retframe)

    else:

      retframe = {'assists': np.nan,
                'blocked': np.nan,
                'evenTimeOnIce': '',
                'faceOffPct': np.nan,
                'faceOffWins': np.nan,
                'faceoffTaken': np.nan,
                'giveaways': np.nan,
                'goals': np.nan,
                'hits': np.nan,
                'penaltyMinutes': np.nan,
                'plusMinus': np.nan,
                'powerPlayAssists': np.nan,
                'powerPlayGoals': np.nan,
                'powerPlayTimeOnIce': np.nan,
                'shortHandedAssists': np.nan,
                'shortHandedGoals': np.nan,
                'shortHandedTimeOnIce': '',
                'shots': np.nan,
                'takeaways': np.nan,
                'timeOnIce': ''
                }
      retframe['gameNumber'] = gamenum + 1
      retframe['played'] = played

      season.append(retframe)

  return {'stat_df': pd.DataFrame(season), 'player_number': playerdict['jerseyNumber']}

def plot_player_stats(playerdf, player_name, player_number, season):
  df = playerdf.copy()
  df['points'] = (df.goals + df.assists).fillna(0)
  df['cumulative_points'] = df['points'].cumsum()

  perc_games_played = round(df.played.mean()*100, 1)

  fig = px.line(data_frame=df, x='gameNumber', y='cumulative_points', hover_name='gameNumber', hover_data={'goals': True , 'assists': True, 'gameNumber': False, 'played': True}, markers=True,
                    labels={
                     "gameNumber": "Game #",
                     "cumulative_points": "Total Points",
                     'goals': 'Goals',
                     'assists': 'Assists',
                     'played': 'Played'
                 }
                )
  fig.update_traces(mode='markers+lines',marker_color=df['played'].map({True: '#0000FF', False:'#DC143C'}))
  fig.update_layout(title= dict(text="{player} #{jn} {season} Season<br>{gpp}% Games Played".format(player=player_name, jn=player_number, season=season,gpp=perc_games_played)))
  #fig.show()
  return fig


def nhl_stats_main(player, team, year):

  stats = get_season_stats(player, team,year)

  fig = plot_player_stats(stats['stat_df'], player, stats['player_number'], year)

  return fig

if __name__ == '__main__':
  myfig = nhl_stats_main(sys.argv[1], sys.argv[2], sys.argv[3])
  myfig.show()
