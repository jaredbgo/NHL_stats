import streamlit as st
import datetime
from datetime import timedelta

from nhl_stats import get_season_stats, plot_player_stats

teamnames = ['Devils', 'Islanders', 'Rangers', 'Flyers', 'Penguins', 'Bruins', 'Sabres', 'Canadiens', 'Senators', 'Maple Leafs', 'Hurricanes', 'Panthers', 'Lightning', 'Capitals', 'Blackhawks', 'Red Wings', 'Predators', 'Blues', 'Flames', 'Avalanche', 'Oilers', 'Canucks', 'Ducks', 'Stars', 'Kings', 'Sharks', 'Blue Jackets', 'Wild', 'Jets', 'Coyotes', 'Golden Knights', 'Kraken']
next_year = datetime.datetime.utcnow().year + 1

seasons = sorted(list(range(2000, next_year)), reverse=True)

seasons_strings = [str(each) + '-' + str(each + 1) for each in seasons]


sideb = st.sidebar

sideb.title('NHL Stats')
sideb.write('Choose a player, team, and season below \n\n\n\n')

chosen_player = sideb.text_input("Input a player's name", '')

if chosen_player == '':
	st.error("Input a player's name")
chosen_team = sideb.selectbox("Choose the player's team", sorted(teamnames), index=0)
chosen_year = sideb.selectbox("Choose a season", seasons_strings, index=1)



try:
	stats = get_season_stats(chosen_player, chosen_team,chosen_year)
	fig = plot_player_stats(stats['stat_df'], chosen_player, stats['player_number'], chosen_year)

	stat_df = stats['stat_df']
	goals = int(stat_df.goals.sum())
	assists = int(stat_df.assists.sum())
	games_played = stat_df[stat_df.timeOnIce != ''].shape[0]

	st.plotly_chart(fig, use_container_width=True)

	#st.text("{gp} games played: {g} goals + {a} assists = {p} points".format(gp=games_played, g=goals, a=assists, p=goals + assists))

	ocol1, ocol2, ocol3, ocol4 = st.columns(4)

	ocol1.metric('Games Played', games_played)
	ocol2.metric('Goals', goals)
	ocol3.metric('Assists', assists)
	ocol4.metric('Points', goals + assists)

except Exception as e:
	st.error(e)