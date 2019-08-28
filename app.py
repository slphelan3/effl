#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 17:39:53 2019

@author: scott
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from espn_ffl import espn_ffl
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import json


#server = Flask(__name__)
#app = dash.Dash(__name__, server=server, url_base_pathname='/dummypath')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server # the Flask app



#app.scripts.config.serve_locally=True
app.layout = html.Div([
    html.Div('ESPN Fantasy Football Historical Analysis', style={'fontSize': 20}),
    html.Div('Made by Scott Phelan'),
    html.Div('Go to your ESPN Fantasy Football homepage and pull out your league ID from the url.'),# style={'fontSize': 20}),
    html.Div('For example, the league ID is in bold below:'),# style={'fontSize': 20}),
    
    dcc.Markdown('https://fantasy.espn.com/football/league/schedule?leagueId=**320207**'),
    html.Div('Once you have your league ID, proceed below and take a look at the data.'),
    html.Div('Note: for now, the results only include the regular season.'),
    html.Div('Note: the code identifies teams by their abbreviation, if a team has changed that then this will not work as well. Future iterations could include a data-cleaning module.'),
    
    dcc.Markdown('***'),
    html.Label('Enter League ID (from ESPN Fantasy Football URL) and press Submit'),
    # text box to input league ID
    dcc.Input(id='league_id', type='text', value='League ID'),
    # submit button to kick off once league ID is in the text box
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    dcc.Markdown('***'),
    # non-team-dependant plots
    html.Div('Average Score by Team vs. Average Opposing Team Score, sorted by average point differential', style={'fontSize': 20}),
    dcc.Graph(id='avg_ppg_graph'),#, figure=go.Figure()),
    dcc.Markdown('***'),
    html.Div('Cumulative Points vs. Wins by year', style={'fontSize': 20}),
    # cumulative score vs. wins
    dcc.Graph(id='points_vs_wins_graph'),#, figure=go.Figure()),
    # slider for selecting year
    html.Div([dcc.Slider(id='year--slider')],style={'padding': '20px 20px 20px 20px'}),
    html.Label('\nSelect a year from above to watch how the league has changed through the years'),


    dcc.Markdown('***'),
    # dropdown list for selecting teams
    html.Div('Comparison Plots for Two Teams', style={'fontSize': 20}),
    html.Label('Select two teams to compare: '),
    html.Div([
    html.Div([dcc.Dropdown(id='team_dropdown')],
              style={'display': 'inline-block', 'width': '40%'}, className='two columns'),
    html.Div([dcc.Dropdown(id='team_dropdown2')],
              style={'width': '40%'}, className='two columns')], className='row'),
    dcc.Markdown('***'),
    
    # create the plots
    html.Div('Point differential from average points scored vs. opponent', style={'fontSize': 20}),
    html.Div('On the horizontal axis of these plots is the difference between the points scored by a team and the average points scored by all teams in that week. The vertical axis is the same value for their opponent that week. The colors are different outcomes. Here is an explanation of the outcomes:'),
    html.Div('Deserving Loss: team scores below weekly average and loses'),
    html.Div('Deserving Win: team scores above weekly average and wins'),
    html.Div('Lucky Win: team scores below weekly average and wins'),
    html.Div('Unlucky Loss: team scores above weekly average and loses'),
    
    html.Div([
    html.Div([dcc.Graph(id='plot_diff_graph')],
              style={'display': 'inline-block', 'width': '40%'}, className='three columns'),
    html.Div([dcc.Graph(id='plot_diff_graph2')],
              style={'width': '40%'}, className='three columns')], className='row'),
    
    
    dcc.Markdown('***'),
    html.Div('Overall Score Distribution', style={'fontSize': 20}),
    
    html.Div([
    html.Div([dcc.Graph(id='score_hist_graph')],
              style={'display': 'inline-block', 'width': '40%'}, className='four columns'),
    html.Div([dcc.Graph(id='score_hist_graph2')],
              style={'width': '40%'}, className='four columns')], className='row'),
    
    
    
    dcc.Markdown('***'),
    html.Div('Outcomes vs. Average', style={'fontSize': 20}),
    html.Div('These plots compare the percentage of a given outcome that a team has had to the average occurance rate of that outcome.'),
    
    
    html.Div([
    html.Div([dcc.Graph(id='lucky_graph')],
              style={'display': 'inline-block', 'width': '40%'}, className='four columns'),
    html.Div([dcc.Graph(id='lucky_graph2')],
              style={'width': '40%'}, className='four columns')], className='row'),
    
    

    # hidden node to transfer data between callbacks
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.Div(id='intermediate-plots2', style={'display': 'none'}),
    html.Div(id='intermediate-plots', style={'display': 'none'})
])

@app.callback(Output('intermediate-value', 'children'),
               [Input('league_id', 'value')])
def update_output(league_id):
    # load in data with league ID
    effl=espn_ffl(str(league_id).replace(' ',''))
    # slider data
    marks={str(year): str(year) for year in range(effl.yearFrom,effl.yearTo+1)}
    
    # create team dictionary
    team_list=[]
    for team in effl.all_teams:
        team_dict={}
        team_dict['label']=team
        team_dict['value']=team
        team_list.append(team_dict)
    # get average ppg plots
    df_avg_ppg=effl.avg_ppg()
    # store plots in dict and distribute to other callbacks
    datasets = {
         'slider_marks': json.dumps(marks),
         'slider_max': json.dumps(effl.yearTo),
         'slider_min': json.dumps(effl.yearFrom),
         'slider_value': json.dumps(effl.yearFrom),
         'teams': json.dumps(team_list),
         'avg_ppg': df_avg_ppg.to_json(orient='split', date_format='iso')
         }

    return json.dumps(datasets)

@app.callback(Output('year--slider', 'min'), [Input('intermediate-value', 'children')])
def slider_min_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    return json.loads(passed_data['slider_min'])
@app.callback(Output('year--slider', 'max'), [Input('intermediate-value', 'children')])
def slider_max_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    return json.loads(passed_data['slider_max'])
@app.callback(Output('year--slider', 'marks'), [Input('intermediate-value', 'children')])
def slider_marks_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    return json.loads(passed_data['slider_marks'])
@app.callback(Output('year--slider', 'value'), [Input('intermediate-value', 'children')])
def slider_value_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    return json.loads(passed_data['slider_value'])
@app.callback(Output('team_dropdown', 'options'), [Input('intermediate-value', 'children')])
def team_dropdown_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    team_list=json.loads(passed_data['teams'])
    return team_list
@app.callback(Output('team_dropdown2', 'options'), [Input('intermediate-value', 'children')])
def team_dropdown2_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    team_list=json.loads(passed_data['teams'])
    return team_list
@app.callback(Output('intermediate-plots', 'children'), 
              [Input('team_dropdown', 'value'),
               Input('team_dropdown2', 'value'),
               Input('league_id', 'value')])
def create_plots(team, team2, league_id):
    # load in data with league ID
    effl=espn_ffl(str(league_id))
    # get all the plots
    df_plot_diff=effl.plot_differential(team,True)
    df_score_hist=effl.plot_score_histogram(team,True,False,True)
    df_lucky=effl.lucky_plot(team,True)
    df_plot_diff2=effl.plot_differential(team2,True)
    df_score_hist2=effl.plot_score_histogram(team2,True,False,True)
    df_lucky2=effl.lucky_plot(team2,True)
    # store plots in dict and distribute to other callbacks
    datasets = {
         'plot_diff': df_plot_diff.to_json(orient='split', date_format='iso'),
         'score_hist': df_score_hist.to_json(orient='split', date_format='iso'),
         'lucky': df_lucky.to_json(orient='split', date_format='iso'),
         'plot_diff2': df_plot_diff2.to_json(orient='split', date_format='iso'),
         'score_hist2': df_score_hist2.to_json(orient='split', date_format='iso'),
         'lucky2': df_lucky2.to_json(orient='split', date_format='iso')
         }

    return json.dumps(datasets)
@app.callback(Output('intermediate-plots2', 'children'), 
              [Input('league_id', 'value')])
def create_plots2(league_id):
    # load in data with league ID
    effl=espn_ffl(str(league_id))
    # get all the plots
    df_points_vs_wins=effl.points_vs_wins()
    # store plots in dict and distribute to other callbacks
    datasets = {
         'points_vs_wins': df_points_vs_wins.to_json(orient='split', date_format='iso')
         }
    return json.dumps(datasets)
      
@app.callback(Output('plot_diff_graph', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown', 'value')])
def plot_diff_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['plot_diff'], orient='split')
    label1='Diff1'
    label2='Diff2'
    
    figure={
            'data': [
                go.layout.Annotation(
                    x=50,
                    y=40,
                    xref="x",
                    yref="y",
                    text="Wins"),
                go.layout.Annotation(
                    x=40,
                    y=50,
                    xref="x",
                    yref="y",
                    text="Losses"),
                go.Scatter(x=[-60,60],y=[-60,60],name='Win/Loss Line')]+
                [go.Scatter(
#                    x=df['Diff1'],
#                    y=df['Diff2'],
                    x=df[df['Outcome'] == i][label1],
                    y=df[df['Outcome'] == i][label2],
                    text=df[df['Outcome'] == i]['Outcome'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.Outcome.sort_values().unique()
            ],
            'layout': go.Layout(
                xaxis={'title': team+' Point Differential from Weekly Average'},
                yaxis={'title': 'Opponent Point Differential from Weekly Average'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                annotations=[
                    go.layout.Annotation(
                        x=50,
                        y=30,
                        xref="x",
                        yref="y",
                        text="Wins",
                        showarrow=False),
                    go.layout.Annotation(
                        x=40,
                        y=50,
                        xref="x",
                        yref="y",
                        text="Losses",
                        showarrow=False)])
        }
    return figure
@app.callback(Output('plot_diff_graph2', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown2', 'value')])
def plot_diff2_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['plot_diff2'], orient='split')
    label1='Diff1'
    label2='Diff2'
    figure={
            'data': [go.Scatter(x=[-60,60],y=[-60,60],name='Win/Loss Line')]+
                [go.Scatter(
#                    x=df['Diff1'],
#                    y=df['Diff2'],
                    x=df[df['Outcome'] == i][label1],
                    y=df[df['Outcome'] == i][label2],
                    text=df[df['Outcome'] == i]['Outcome'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.Outcome.sort_values().unique()
            ],
            'layout': go.Layout(
                xaxis={'title': team+' Point Differential from Weekly Average'},
                yaxis={'title': 'Opponent Point Differential from Weekly Average'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                annotations=[
                    go.layout.Annotation(
                        x=50,
                        y=30,
                        xref="x",
                        yref="y",
                        text="Wins",
                        showarrow=False),
                    go.layout.Annotation(
                        x=40,
                        y=50,
                        xref="x",
                        yref="y",
                        text="Losses",
                        showarrow=False)])
        }
    return figure

@app.callback(Output('score_hist_graph', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown', 'value')])
def plot_hist_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['score_hist'], orient='split')
    label1=team+' Score'

    trace = go.Histogram(x=df[label1], opacity=0.7, marker={"line": {"color": "#25232C", "width": 0.2}},
                         xbins={"size": 5})
    layout = go.Layout(title=team +" Score Distribution", xaxis={"title": "Score", "showgrid": False},
                       yaxis={"title": "Count", "showgrid": False}, )
    figure2 = {"data": [trace], "layout": layout}
    return figure2
@app.callback(Output('score_hist_graph2', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown2', 'value')])
def plot_hist2_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['score_hist2'], orient='split')
    label1=team+' Score'

    trace = go.Histogram(x=df[label1], opacity=0.7, marker={"line": {"color": "#25232C", "width": 0.2}},
                         xbins={"size": 5})
    layout = go.Layout(title=team+" Score Distribution", xaxis={"title": "Score", "showgrid": False},
                       yaxis={"title": "Count", "showgrid": False}, )
    figure2 = {"data": [trace], "layout": layout}
    return figure2

@app.callback(Output('lucky_graph', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown', 'value')])
def plot_lucky_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['lucky'], orient='split')
    df=df.sort_values(by=['index'])
    label1=team+' Outcomes'
    label2='Average Outcomes'
    figure=go.Figure(
        data=[
            go.Bar(
                x=df[df['Team']==i]['index'],
                y=df[df['Team']==i]['Count'],
                name=i,
#                marker=go.bar.Marker(
#                    color='rgb(55, 83, 109)'
#                )
            )
            for i in df.Team.unique()
        ],
        layout=go.Layout(
            title=team+' Outcome Percentage vs. Average',
            showlegend=True,
            legend=go.layout.Legend(
                x=1.0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )
    return figure
@app.callback(Output('lucky_graph2', 'figure'), 
              [Input('intermediate-plots', 'children'),
               Input('team_dropdown2', 'value')])
def plot_lucky2_update(jsonified_cleaned_data, team):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['lucky2'], orient='split')
    df=df.sort_values(by=['index'])
    label1=team+' Outcomes'
    label2='Average Outcomes'
    figure=go.Figure(
        data=[
            go.Bar(
                x=df[df['Team']==i]['index'],
                y=df[df['Team']==i]['Count'],
                name=i,
#                marker=go.bar.Marker(
#                    color='rgb(55, 83, 109)'
#                )
            )
            for i in df.Team.unique()
        ],
        layout=go.Layout(
            title=team+' Outcome Percentage vs. Average',
            showlegend=True,
            legend=go.layout.Legend(
                x=1.0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )
    return figure



@app.callback(Output('avg_ppg_graph', 'figure'), 
              [Input('intermediate-value', 'children')])
def avg_ppg_update(jsonified_cleaned_data):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['avg_ppg'], orient='split')
    columns=['Average Score','Average Opponent Score']
    figure=go.Figure(
        data=[
            go.Bar(
                x=df['Team'],
                y=df[col],
                name=col
            )
            for col in columns
        ],
        layout=go.Layout(
            showlegend=True,
            legend=go.layout.Legend(
                x=1.0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )
    return figure
@app.callback(Output('points_vs_wins_graph', 'figure'), 
              [Input('intermediate-plots2', 'children'),
               Input('year--slider', 'value')])
def points_vs_wins_update(jsonified_cleaned_data, year):
    passed_data = json.loads(jsonified_cleaned_data)
    df=pd.read_json(passed_data['points_vs_wins'], orient='split')
    year_df=df[df['Year']==year]
    figure={
            'data': [
                go.Scatter(
#                    x=df['Diff1'],
#                    y=df['Diff2'],
                    x=year_df[year_df['Team']==team]['Cumulative Points'],
                    y=year_df[year_df['Team']==team]['Cumulative Wins'],
                    text=team,
                    mode='markers',
                    opacity=0.7,
                    marker={'size': 30},
                    name=team
                ) for team in year_df['Team'].unique()
            ],
            'layout': go.Layout(
                xaxis={'title': 'Cumulative Points Before '+str(year)},
                yaxis={'title': 'Cumulative Wins Before '+str(year)},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    return figure


@server.route("/dash")
def MyDashApp():
    return app.index()