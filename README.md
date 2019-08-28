# espnffl
ESPN Fantasy Football History Visualization
This project takes in a league ID from the espn fantasy football url. For example if the url is:
https://fantasy.espn.com/football/team?leagueId=320207&teamId=3&seasonId=2019

Then the league ID is 320207.

*** FUTURE WORK ***
-Add data cleaning module for team names

The espn_ffl.py file contains the espn_ffl class, which can be initiated by:
>>from espn_ffl import espn_ffl
>>effl=espn_ffl('320207')

This will pull from the ESPN API v3 and collect all the data needed to create the below plots. Then you can generate dataframes that can be used to make different plots, such as:

Scatter plot of difference between points for and weekly average vs. points against and weekly average (can use to tell how lucky a team is):
>>effl.plot_differential(team)

Overall score histogram for a given team:
>>effl.plot_score_histogram(team)

Bar chart of how lucky a team is vs. average:
>>effl.lucky_plot(team)

Bar chart of average points scored vs. average points against for all teams:
>>effl.avg_ppg()

Cumulative points vs. wins scatterplot for all teams:
>>effl.points_vs_wins()
