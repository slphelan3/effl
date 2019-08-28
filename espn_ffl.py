#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 18:28:26 2019

@author: scott
"""

import pandas as pd
import requests
#import seaborn as sns
#import matplotlib.pyplot as plt

class espn_ffl:
    def __init__(self, league_id):
        self.league_id = league_id
        self.team_results, self.outcome_df, self.all_teams, self.df_out, self.years=self.pull_from_api()
        self.yearFrom=self.years[0]
        self.yearTo=self.years[-1]

    # figure out type of win
    def lucky_win(self,row):
        if row['Win']==1 and row['Diff1'] <= 0:
            return 'Lucky Win'
        elif row['Win']==1 and row['Diff1'] > 0:
            return 'Deserving Win'
        elif row['Win']==0 and row['Diff1'] > 0:
            return 'Unlucky Loss'
        elif row['Win']==0 and row['Diff1'] <= 0:
            return 'Deserving Loss'

    def clean_team_names(self,clean_dict,df_out):
        # clean up team names
        df_out['Team1']=df_out['Team1'].replace(clean_dict)
        df_out['Team2']=df_out['Team2'].replace(clean_dict)
        return df_out

    # pull from api dictionary
    def pull_from_api(self):
        past_szn_base='https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/'+self.league_id+'?seasonId='

        years_init=range(2000,2019)
        df_out=pd.DataFrame()
        avgs_out=pd.DataFrame()
        team_dict={}
        years=[]
        for year in years_init:
            url=past_szn_base+str(year)
            r = requests.get(url, params={"view": "mMatchup"})
            if r.status_code==200:
                years.append(year)
                d = r.json()[0]

                df = [[
                        game['matchupPeriodId'],
                        game.get('home')['teamId'], game.get('home')['totalPoints'],
                        game.get('away')['teamId'], game.get('away')['totalPoints'],
                        year
                    ] for game in d['schedule'] if game.get('away') is not None]
                df = pd.DataFrame(df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2', 'Year'])
                df['Type'] = ['Regular' if w<=14 else 'Playoff' for w in df['Week']]

                # only keep regular season
                df=df[df['Type']=='Regular']


                # get average score by week
                avgs = (df
                 .filter(['Week', 'Score1', 'Score2'])
                 .melt(id_vars=['Week'], value_name='Score')
                 .groupby('Week')
                 .mean()
                 .reset_index()
                )
                avgs['Year']=year

                avgs_out=pd.concat([avgs_out,avgs])
                df_out=pd.concat([df_out,df])

                # get json without params to get team mappings
                r2=requests.get(url)
                d2=r2.json()[0]
                team_dict[year]={}
                for team in d2['teams']:
                    team_dict[year][team['id']]=team['abbrev'].replace(' ','')
                # replace id number with abbrev
                df_out['Team1']=df_out['Team1'].replace(team_dict[year])
                df_out['Team2']=df_out['Team2'].replace(team_dict[year])

        # clean up team names
        clean_dict={'BV': 'MCT', 'ZELE': 'MIKE', 'BJ': 'MCT','ROGE': 'GOOS', 'BIAL': 'AJB', 'PHEL': 'PHE','BILL':'PHE'}
        df_out=self.clean_team_names(clean_dict,df_out)

        # get list of all teams
        all_teams=pd.concat([df_out['Team1'],df_out['Team2']]).value_counts().index

        # re-index avgs_out
        avgs_out.index=[beep for beep in range(len(avgs_out.index))]


        outcome_df=pd.DataFrame()
        team_results={}
        for team in all_teams:
            tm=team
            # grab all games with this team
            df2 = df_out.query('Team1 == @tm | Team2 == @tm').reset_index(drop=True)

            # move the team of interest to "Team1" column
            ix = list(df2['Team2'] == tm)
            df2.loc[ix, ['Team1','Score1','Team2','Score2']] = \
                df2.loc[ix, ['Team2','Score2','Team1','Score1']].values

            # add new score and win cols
            df2['Win']=df2['Score1'] > df2['Score2']
            df2['Diff1']=df2['Score1'] - avgs_out['Score']
            df2['Diff2']=df2['Score2'] - avgs_out['Score']

            # add lucky/unlucky win
            df2['Outcome']=df2.apply(self.lucky_win,axis=1)

            outcome_df=pd.concat([outcome_df,df2])
            team_results[team]=df2



        return team_results, outcome_df, all_teams, df_out, years

    # create differential score plot
    def plot_differential(self,team,suppress=False):
#        plt.figure()
        team_result=self.team_results[team]
        plot_results=pd.DataFrame()
        label1=team+' Point Diff from Weekly Average'
        label2='Opponent Point Diff from Weekly Average'
        label1='Diff1'
        label2='Diff2'
        plot_results[label1]=team_result['Diff1']
        plot_results[label2]=team_result['Diff2']

        plot_results['Outcome']=team_result['Outcome']
#        plot_results['Opponent']=team_result['Team2']
        plot_results['Result Name']=team_result['Outcome'] + ' vs. ' + team_result['Team2']

        plot_results['Win']=team_result['Win'].replace({1:'Win',0:'Loss'})
        if suppress==False:
            pass
#            ax=sns.scatterplot(x=label1,y=label2,data=plot_results,hue='Outcome')
#            ax.legend(loc='center right', bbox_to_anchor=(1.38, 0.5), ncol=1)

        return plot_results

    # create score histogram
    def plot_score_histogram(self,team,overlay=False,team_year=False,suppress=False):
#        plt.figure()
        label1=team+' Score'
        team_result=self.team_results[team]
        plot_results=pd.DataFrame()
        plot_results[label1]=team_result['Score1']
        if overlay:
            ax_dict={}
            if team_year != False:
                year_df=self.df_out[self.df_out['Year']==team_year]
                teamlist=pd.concat([year_df['Team1'],year_df['Team2']]).value_counts().index
            else:
                teamlist=self.all_teams
            for tid in teamlist:
                curr_label=tid+' Scores'
                plot_results[curr_label]=self.team_results[tid]['Score1']
                if suppress==False:
                    pass
#                    ax_dict[tid]=sns.kdeplot(plot_results[curr_label])
        if suppress==False:
            pass
#            ax=sns.distplot(plot_results[label1], bins=20, kde=True)
        return plot_results

    # create lucky histogram
    def lucky_plot(self,team,suppress=False):
#        plt.figure()
        team_result=self.team_results[team]
        avg_outcomes=self.outcome_df['Outcome'].value_counts()/len(self.all_teams)
        outcomes=team_result['Outcome'].value_counts()
        avg_sum=sum(avg_outcomes.values)
        team_sum=sum(outcomes.values)
#        avg_outcomes=avg_outcomes*team_sum/avg_sum

        label1=team+' Outcomes'
        label2='Average Outcomes'

        plot_outcomes=pd.DataFrame(index=outcomes.index)

        plot_outcomes[label1]=outcomes.values/team_sum
        plot_outcomes[label2]=avg_outcomes.values/avg_sum
        plot_outcomes = pd.melt(plot_outcomes.reset_index(), id_vars='index', var_name='Team', value_name='Count')
        if suppress==False:
            pass
#            ax=sns.factorplot(x='index', y='Count', hue='Team', data=plot_outcomes, kind='bar')
        return plot_outcomes

    def avg_ppg(self):
        teamscore=[]
        oppscore=[]
        teams=[]
        for team in self.team_results:
            df=self.team_results[team]
            teams.append(team)
            teamscore.append(df['Score1'].mean())
            oppscore.append(df['Score2'].mean())
        plot_results=pd.DataFrame()
        plot_results['Team']=teams
        plot_results['Average Score']=teamscore
        plot_results['Average Opponent Score']=oppscore
        plot_results['Average Differential']=plot_results['Average Score']-plot_results['Average Opponent Score']
        return plot_results.sort_values(by=['Average Differential'])

    def points_vs_wins(self):
        points=[]
        teams=[]
        years=[]
        wins=[]
        team_points={}
        team_wins={}
        for team in self.team_results:
            team_points[team]=[]
            team_wins[team]=[]
            df=self.team_results[team]
            for year in df['Year'].unique():
                years.append(year)
                teams.append(team)

                points.append(df[df['Year']==year]['Score1'].sum()+sum(team_points[team]))
                wins.append(df[df['Year']==year]['Win'].sum()+sum(team_wins[team]))
                team_points[team].append(df[df['Year']==year]['Score1'].sum())
                team_wins[team].append(df[df['Year']==year]['Win'].sum())


        plot_results=pd.DataFrame()
        plot_results['Team']=teams
        plot_results['Year']=years
        plot_results['Cumulative Wins']=wins
        plot_results['Cumulative Points']=points
        return plot_results



