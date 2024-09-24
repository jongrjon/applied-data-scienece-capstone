# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'fontSize': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'}]+
                                        [{'label': f'All {site}', 'value': site.upper()} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder="Placeholder",
                                    searchable=True
                                ),
                                html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'), Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    class_labels = {0: 'Failed', 1: 'Successful'}
    
    if entered_site == 'ALL':
        success_df = spacex_df[spacex_df['class'] == 1]  # Filter only successful launches
        site_counts = success_df['Launch Site'].value_counts().reset_index()
        site_counts.columns = ['Launch Site', 'count']
        
        fig = px.pie(
            site_counts, 
            values='count', 
            names='Launch Site',   
            title='Successful Launches by Site'
        )
    else:
        filtered_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = filtered_site_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        class_counts['class'] = class_counts['class'].map(class_labels)
        
        fig = px.pie(
            class_counts, 
            values='count',  
            names='class',   
            title=f'Success and Failure for {entered_site}'
        )
    
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'), [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload):
    if entered_site == 'ALL':
        data = spacex_df
        
    else:
        data = spacex_df[spacex_df['Launch Site'] == entered_site]
    
    data = data[(data['Payload Mass (kg)'] >= payload[0]) & (data['Payload Mass (kg)'] <= payload[1])]
    fig = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version Category")
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)