from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import wget
import pandas as pd
import numpy as np

spacex_csv_file = wget.download('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv')
spacex_df=pd.read_csv(spacex_csv_file)
#for the pie chart
landing_failures = spacex_df[spacex_df['class']==0].groupby('Launch Site')['class'].count()
landing_success = spacex_df[spacex_df['class']==1].groupby('Launch Site')['class'].count()
#for the slider values
min_value = spacex_df['Payload Mass (kg)'].min()
max_value = spacex_df['Payload Mass (kg)'].max()

app = Dash(__name__)


app.layout = html.Div([
    html.H4('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id="site-dropdown",
        options=[{'label': 'All Sites', 'value': 'ALL'},
                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
        value='ALL',
        clearable=False,
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    dcc.Graph(id="graph"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0',
                       2500: '2500',
                       5000: '5000',
                       7500: '7500',
                       10000: '10000'},
                    value=[min_value, max_value]),
    dcc.Graph(id="success-payload-scatter-chart")
])


@app.callback(
    Output("graph", "figure"), 
    Output('success-payload-scatter-chart', 'figure'),
    Input("site-dropdown", "value"), #this changes the value based on the selection from "Options". "Value" is the value selected.
    Input("payload-slider", "value"))

def generate_charts(launch_site, payload_selection):
    temp_df = spacex_df[['Launch Site','Payload Mass (kg)','Booster Version','class']]
    temp_df = temp_df[temp_df['Launch Site'] == launch_site]
    temp_df = temp_df[temp_df['Payload Mass (kg)'].between(payload_selection[0], payload_selection[1], inclusive=True)]
    
    if launch_site == 'ALL':
        headers = list(spacex_df['Launch Site'].unique())
        val = []
        for col in headers:
            val.append(landing_success[col])
        fig = px.pie(
            title='Total Successful Launches By Site',
            values=val,
            hover_name=headers,
            names=headers,
        )
        temp_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_selection[0], payload_selection[1], inclusive=True)]
        fig1 = px.scatter(
            temp_df,
            title = 'Correlation between Payload and Success for all Sites',
            y='class',
            x='Payload Mass (kg)',
            color='Booster Version'
        )
    else:
        fig = px.pie(
            title='Total Successful Launches for ' + launch_site,
            values=[landing_success[launch_site], landing_failures[launch_site]],
            hover_name=['Success', 'Failure'],
            names=['Success', 'Failure']
        )
        fig1 = px.scatter(
            temp_df,
            title = 'Correlation between Payload and Success for ' + launch_site,
            y='class',
            x='Payload Mass (kg)',
            color='Booster Version'
        )
    
    return fig, fig1


app.run_server(debug=True)