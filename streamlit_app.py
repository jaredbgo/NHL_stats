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

chosen_player = sideb.text_input("Input a player's name")
chosen_team = sideb.selectbox("Choose the player's team", sorted(teamnames), index=0)
chosen_year = sideb.selectbox("Choose a season", seasons_strings, index=0)



try:
	stats = get_season_stats(chosen_player, chosen_team,chosen_year)
	fig = plot_player_stats(stats['stat_df'], chosen_player, stats['player_number'], chosen_year)

	st.plotly_chart(fig, use_container_width=True)

except Exception as e:
	st.error(e)