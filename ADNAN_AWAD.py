"""
CP321 - Data Visualisation
Adnan Awad - 169028425
Assignment 7
"""

# Published dashboard: https://cp321-a7-w25-adnan-awad-fifa-world-cup.onrender.com

import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import gunicorn

# Step 1: Create the dataset for FIFA World Cup finals
data = {
    'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978,
             1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
    'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil',
               'Brazil', 'England', 'Brazil', 'West Germany', 'Argentina',
               'Italy', 'Argentina', 'West Germany', 'Brazil', 'France', 'Brazil',
               'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
    'RunnerUp': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary',
                 'Sweden', 'Czechoslovakia', 'Germany', 'Italy', 'Netherlands',
                 'Netherlands', 'Germany', 'Germany', 'Argentina', 'Italy',
                 'Brazil', 'Germany', 'France', 'Netherlands', 'Argentina',
                 'Croatia', 'France']
}

# Create DataFrame
df = pd.DataFrame(data)

# Replace 'West Germany' with 'Germany' for consistency
df['Winner'] = df['Winner'].replace({'West Germany': 'Germany'})
df['RunnerUp'] = df['RunnerUp'].replace({'West Germany': 'Germany'})

# Step 2a: Compute the total wins per country from the Winner column
wins = df['Winner'].value_counts().reset_index()
wins.columns = ['Country', 'Wins']

# Mapping for ISO codes required for the choropleth map (only include countries with valid ISO codes)
iso_codes = {
    "Germany": "DEU",
    "Uruguay": "URY",
    "Italy": "ITA",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "England": "GBR",
    "France": "FRA",
    "Spain": "ESP"
}

wins['iso_alpha'] = wins['Country'].apply(lambda x: iso_codes.get(x, None))

# Create a choropleth map showing wins by country using Plotly Express
fig_choropleth = px.choropleth(
    wins,
    locations="iso_alpha",
    color="Wins",
    hover_name="Country",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="FIFA World Cup Wins by Country"
)

# Build the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1(
                    "FIFA World Cup Dashboard",
                    className="text-center my-4"
                )
            )
        ),

        dbc.Row(
            dbc.Col([
                html.H2("World Cup Wins Choropleth Map", className="mb-3"),
                dcc.Graph(id='choropleth', figure=fig_choropleth, style={'height': '70vh'})
            ], width=12),
            className="mb-5"
        ),

        dbc.Row([
            dbc.Col([
                html.H2("Winning Countries", className="mb-3"),
                html.P("Countries that have ever won the World Cup:"),
                html.Ul([html.Li(country) for country in wins['Country'].unique()])
            ], md=4, className="mb-4"),

            dbc.Col([
                html.H2("Country Wins Lookup", className="mb-3"),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[
                        {'label': country, 'value': country}
                        for country in wins['Country'].unique()
                    ],
                    placeholder="Select a country"
                ),
                html.Div(id='country-wins-output', className="mt-3")
            ], md=4, className="mb-4"),

            dbc.Col([
                html.H2("Yearly Finals Lookup", className="mb-3"),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[
                        {'label': year, 'value': year}
                        for year in sorted(df['Year'].unique())
                    ],
                    placeholder="Select a year"
                ),
                html.Div(id='year-finals-output', className="mt-3")
            ], md=4, className="mb-4"),
        ]),
    ]
)

# Callbacks
@app.callback(
    Output('country-wins-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_wins(selected_country):
    if selected_country:
        win_count = wins.loc[wins['Country'] == selected_country, 'Wins'].iloc[0]
        return html.P(f"{selected_country} has won the World Cup {win_count} times.")
    return html.P("Select a country to view its win count.")

@app.callback(
    Output('year-finals-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_finals(selected_year):
    if selected_year:
        final_row = df[df['Year'] == selected_year].iloc[0]
        return html.P(f"In {selected_year}, the winner was {final_row['Winner']} "
                      f"and the runner-up was {final_row['RunnerUp']}.")
    return html.P("Select a year to view the finals details.")

if __name__ == '__main__':
    app.run_server(debug=True)
