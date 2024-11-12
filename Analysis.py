import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio


import dash
from dash import dcc, html
from dash.dependencies import Input, Output

def load_data():
    presentation = pd.read_csv('data\Presentations Only Spreadsheet - Presentations.csv')
    outputs = pd.read_csv('data\Carework Network database - Outputs.csv')
    return presentation, outputs

# Prepare the data (assuming you already have the presentation data in a DataFrame)
presentation.columns = presentation.columns.str.strip()

# Split the topics by semicolon, creating a new row for each topic
presentation_expanded = presentation.assign(Topic=presentation['Topics (L)'].str.split(';')).explode('Topic')

# Strip any leading/trailing whitespace from topics
presentation_expanded['Topic'] = presentation_expanded['Topic'].str.strip()

# Count occurrences of each topic by year
topic_trends = presentation_expanded.groupby(['Year', 'Topic']).size().reset_index(name='Count')

# For each year, select the top 5 topics and combine them into a single DataFrame
top_topics_per_year = topic_trends.groupby('Year').apply(
    lambda df: df.nlargest(5, 'Count')
).reset_index(drop=True)

# Dash application
app = dash.Dash(__name__)

# Function to create a timeline with dynamic top 5 topics per year
def create_timeline_figure():
    fig = px.line(
        top_topics_per_year,
        x="Year",
        y="Count",
        color="Topic",
        title="Trends in Presentation Topics Over Years (Top 5 Topics per Year)",
        labels={"Count": "Number of Presentations", "Year": "Year"},
        markers=True
    )

    # Prettify the layout with hover details
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Presentations",
        hovermode="x unified",
        legend_title_text="Topics",
        title_font=dict(size=22, family='Arial'),
        template='plotly_white',
    )
    
    return fig

# Create a function to generate the figure for a specific year
def create_year_figure(selected_year):
    # Filter data for the selected year
    year_data = topic_trends[topic_trends['Year'] == selected_year]
    
    # Get the top 5 topics for that year
    top_5_topics = year_data.nlargest(5, 'Count')
    
    # Create a bar chart for the selected year
    fig = px.bar(
        top_5_topics,
        x="Topic",
        y="Count",
        title=f'Top 5 Topics in {selected_year}',
        labels={"Count": "Number of Presentations", "Topic": "Topic"}
    )

    # Prettify the layout
    fig.update_layout(
        xaxis_title="Topic",
        yaxis_title="Number of Presentations",
        hovermode="closest",
        title_font=dict(size=22, family='Arial'),
        template='plotly_white',
    )

    return fig

# Define the layout of the app
app.layout = html.Div([
    html.H1("Interactive Presentation Topic Trends", style={'text-align': 'center'}),

    # Timeline graph
    dcc.Graph(
        id='timeline-graph',
        figure=create_timeline_figure()
    ),

    # Output graph for top 5 topics in a selected year
    dcc.Graph(id='year-graph'),

    # Hidden div to store the clicked year
    dcc.Store(id='selected-year', data=None)
])

# Callback to update the year-graph based on a click event from the timeline graph
@app.callback(
    Output('year-graph', 'figure'),
    Input('timeline-graph', 'clickData')
)
def update_year_graph(clickData):
    if clickData:
        # Extract the year from the click event
        selected_year = clickData['points'][0]['x']
        return create_year_figure(selected_year)
    # Return an empty figure if no year is selected
    return {}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
