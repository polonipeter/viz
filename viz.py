import pandas as pd
import plotly.express as px
import numpy as np
from dash import Dash, dcc, html, Input, Output,no_update
import os

data = pd.read_csv("worldometer_coronavirus_daily_data.csv")
data

data['date'] = pd.to_datetime(data['date'])
population = pd.read_csv("worldometer_coronavirus_summary_data.csv") #load the population
population = population[['country', 'population']]
population

data = pd.merge(data, population, on='country', how='left')#merge the datasets

countries_to_remove = [
    'French Guiana', 'Reunion', 'Guadeloupe', 'Martinique', 'Mayotte', 
    'Saint Barthelemy', 'Saint Martin', 'Saint Pierre And Miquelon', 
    'French Polynesia', 'Anguilla', 'British Virgin Islands', 
    'Cayman Islands', 'Channel Islands', 'Montserrat', 
    'Turks And Caicos Islands', 'Aruba', 'Caribbean Netherlands', 
    'Curacao', 'Sint Maarten', 'US Virgin Islands', 
    'China Hong Kong Sar', 'China Macao Sar', 'Cook Islands', 
    'Faeroe Islands', 'San Marino', 'Liechtenstein', 'Grenada'
]#these are not shown on the dash map

data = data[~data['country'].isin(countries_to_remove)]
data['cases_per_million'] = (data['cumulative_total_cases'] / data['population']) * 1_000_000
data['new_cases_per_million'] = (data['daily_new_cases'] / data['population']) * 1_000_000
data['active_cases_per_million'] = (data['active_cases'] / data['population']) * 1_000_000
data['deaths_per_million'] = (data['cumulative_total_deaths'] / data['population']) * 1_000_000
data['new_deaths_per_million'] = (data['daily_new_deaths'] / data['population']) * 1_000_000







app = Dash(__name__)

app.layout = html.Div([
    html.H1("COVID-19 Data Visualization", style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Cases Per Million', 'value': 'cases_per_million'},
                    {'label': 'New Cases Per Million', 'value': 'new_cases_per_million'},
                    {'label': 'Active Cases Per Million', 'value': 'active_cases_per_million'},
                    {'label': 'Deaths Per Million', 'value': 'deaths_per_million'},
                    {'label': 'New Deaths Per Million', 'value': 'new_deaths_per_million'}
                ],
                value='cases_per_million',
                placeholder="Select a Metric for the Map",
                style={'width': '90%', 'margin': 'auto', 'marginBottom': '20px'}
            ),
                html.Div([
                    html.Label("Select Date", style={'textAlign': 'center', 'marginBottom': '10px'}),
                    html.Div(
                        [
                            html.Span(f"Min: {data['date'].min().strftime('%Y-%m-%d')}", style={'fontSize': '14px', 'fontWeight': 'bold', 'color': '#333'}),
                            html.Span(f"Max: {data['date'].max().strftime('%Y-%m-%d')}", style={'fontSize': '14px', 'fontWeight': 'bold', 'color': '#333'}),
                        ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'width': '90%',
                            'margin': 'auto',
                            'marginBottom': '5px'
                        }
                    ),
                ]),
    
            dcc.Slider(
                id='date-slider',
                min=0,
                max=len(data['date'].unique()) - 1,
                step=1,
                value=0,
                marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(sorted(data['date'].unique()))},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            dcc.Graph(
                id='choropleth-map',
                style={'height': '800px', 'width': '100%'}
            )
        ], style={'flex': '2', 'padding': '20px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.2)', 'marginRight': '10px'}),

        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='linechart-1-country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(data['country'].unique())],
                    value='China',#default country displayed
                    placeholder="Select a Country for Linechart 1",
                    style={'marginBottom': '10px'}
                ),
                dcc.Graph(
                    id='line-chart-1',
                    style={'height': '400px', 'width': '100%'}
                )
            ], style={'marginBottom': '30px'}),

            html.Div([
                dcc.Dropdown(
                    id='linechart-2-country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(data['country'].unique())],
                    value='China',
                    placeholder="Select a Country for Linechart 2",
                    style={'marginBottom': '10px'}
                ),
                dcc.Graph(
                    id='line-chart-2',
                    style={'height': '400px', 'width': '100%'}
                )
            ], style={'marginBottom': '30px'}),

            html.Div([
                dcc.Dropdown(
                    id='piechart-country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(data['country'].unique())],
                    value='China',
                    placeholder="Select a Country for Pie Chart",
                    style={'marginBottom': '10px'}
                ),
                dcc.Graph(
                    id='pie-chart',
                    style={'height': '400px', 'width': '100%'}
                )
            ])
        ], style={
            'flex': '1',
            'padding': '20px',
            'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.2)',
            'marginLeft': '10px',
            'height': '800px',
            'overflowY': 'scroll',
        })
    ], style={'display': 'flex', 'width': '90%', 'margin': 'auto'})
])


@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('metric-dropdown', 'value'),
     Input('date-slider', 'value')]
)
def update_map(selected_normalized_metric, selected_date_index):
    unique_dates = sorted(data['date'].unique()) #get dates
    selected_date = unique_dates[selected_date_index]
    filtered_df = data[data['date'] == selected_date] #get the data for a given date

    hover_data = {
        'country': True,
        'population': ':,.2f',
        selected_normalized_metric: True
    }

    fig = px.choropleth(
        filtered_df,
        locations='country',
        locationmode='country names',
        color=selected_normalized_metric,
        hover_name='country',
        hover_data=hover_data,
        title=f"{selected_normalized_metric.replace('_', ' ').title()} on {selected_date.strftime('%Y-%m-%d')}",
        color_continuous_scale='Viridis'
    )

    fig.update_coloraxes(
        colorbar=dict(
            title=selected_normalized_metric.replace('_', ' ').title() #rename the scale so it is clear
        )
    )
    return fig

@app.callback(
    [Output('linechart-1-country-dropdown', 'value'),
     Output('linechart-2-country-dropdown', 'value'),
     Output('piechart-country-dropdown', 'value')],
    [Input('choropleth-map', 'clickData')]
)
def update_dropdowns_on_map_click(click_data):
    #keep the clicks and dropdowns in sync
    if click_data is not None:
        selected_country = click_data['points'][0]['location']
        return selected_country, selected_country, selected_country
    return no_update, no_update, no_update

@app.callback(
    [Output('line-chart-1', 'figure'),
     Output('line-chart-2', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('linechart-1-country-dropdown', 'value'),
     Input('linechart-2-country-dropdown', 'value'),
     Input('piechart-country-dropdown', 'value'),
     Input('date-slider', 'value')]
)
def update_charts(country1, country2, pie_country, selected_date_index):
    unique_dates = sorted(data['date'].unique())
    selected_date = unique_dates[selected_date_index]

    def get_country_date_range(country):
        country_data = data[data['country'] == country]
        if not country_data.empty:
            return country_data['date'].min(), country_data['date'].max() #time range for each country to display correct ranges on the plots
        return None, None

    date_range1 = get_country_date_range(country1)
    date_range2 = get_country_date_range(country2)

    def adjust_date_range(date_range, selected_date):
        if date_range[0] is None or date_range[1] is None:
            return None #no data available
        if selected_date == date_range[0]:
            #if the selected date is the first in data display range from the selected date to date+1 so the plot makes sense
            extended_date = unique_dates[min(selected_date_index + 1, len(unique_dates) - 1)]
            return date_range[0], min(date_range[1], extended_date)
        return date_range[0], min(date_range[1], selected_date)

    adjusted_date_range1 = adjust_date_range(date_range1, selected_date)
    adjusted_date_range2 = adjust_date_range(date_range2, selected_date)
    

    filtered_data1 = data[
        (data['country'] == country1) &
        (data['date'] >= adjusted_date_range1[0]) &
        (data['date'] <= adjusted_date_range1[1])
    ] if adjusted_date_range1 else pd.DataFrame() #if range exists filter the data

    filtered_data2 = data[
        (data['country'] == country2) &
        (data['date'] >= adjusted_date_range2[0]) &
        (data['date'] <= adjusted_date_range2[1])
    ] if adjusted_date_range2 else pd.DataFrame()

    filtered_data_pie = data[
    (data['country'] == pie_country) & (data['date'] == selected_date)
    ] if pie_country else pd.DataFrame()


    #display the linecharts if there are any
    if not filtered_data1.empty:
        fig1 = px.line(
            filtered_data1,
            x='date',
            y='cumulative_total_cases',
            title=f"Cumulative Total Cases in {country1} <br>(from {adjusted_date_range1[0].strftime('%Y-%m-%d')} to {adjusted_date_range1[1].strftime('%Y-%m-%d')})"
        )
        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Total Cases"
        )
    else:
        fig1 = px.scatter()
        fig1.update_layout(
            title=f"No data available for {country1}",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(text="No data available", xref="paper", yref="paper", showarrow=False, font=dict(size=15, color="red"))]
        )

    if not filtered_data2.empty:
        fig2 = px.line(
            filtered_data2,
            x='date',
            y='cumulative_total_deaths',
            title=f"Cumulative Total Deaths in {country2} <br>(from {adjusted_date_range2[0].strftime('%Y-%m-%d')} to {adjusted_date_range2[1].strftime('%Y-%m-%d')})"
        )
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Total Deaths"
        )
    else:
        fig2 = px.scatter()
        fig2.update_layout(
            title=f"No data available for {country2}",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(text="No data available", xref="paper", yref="paper", showarrow=False, font=dict(size=15, color="red"))]
        )

    if not filtered_data_pie.empty:
        row = filtered_data_pie.iloc[0] #data z vybraneho dna
        pie_values = [
            row.get('daily_new_cases', 0) if not pd.isna(row.get('daily_new_cases')) else 0,
            row.get('active_cases', 0) if not pd.isna(row.get('active_cases')) else 0,
            row.get('daily_new_deaths', 0) if not pd.isna(row.get('daily_new_deaths')) else 0
        ]
        #check if at least one value is non-zero
        if sum(pie_values) > 0:
            fig3 = px.pie(
                values=pie_values,
                names=['Daily New Cases', 'Active Cases', 'Daily New Deaths'],
                title=f"New Cases vs Active Cases vs Deaths in {pie_country} <br>(as of {selected_date.strftime('%Y-%m-%d')})"
            )
        else:
            fig3 = px.pie()
            fig3.update_layout(
                title=f"No significant data available for {pie_country}",
                annotations=[
                    dict(
                        text="No data to display",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=15, color="red"),
                        xanchor="center",
                        yanchor="middle"
                    )
                ]
            )
    else:
        #no data available
        fig3 = px.pie()
        fig3.update_layout(
            title=f"No data available for {pie_country}",
            annotations=[
                dict(
                    text="No data available",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=15, color="red"),
                    xanchor="center",
                    yanchor="middle"
                )
            ]
        )


    return fig1, fig2, fig3

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050)) #render hosting sets up the port
    app.run_server(port=port, debug=True)
