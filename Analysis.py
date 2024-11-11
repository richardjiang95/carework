import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data (assuming files are in the same directory as this script)
presentation = pd.read_csv('Presentations.csv')
outputs = pd.read_csv('Outputs.csv')

# Data preparation
presentation.columns = presentation.columns.str.strip()
presentation_expanded = presentation.assign(Topic=presentation['Topics (L)'].str.split(';')).explode('Topic')
presentation_expanded['Topic'] = presentation_expanded['Topic'].str.strip()
topic_trends = presentation_expanded.groupby(['Year', 'Topic']).size().reset_index(name='Count')
top_topics_per_year = topic_trends.groupby('Year').apply(lambda df: df.nlargest(5, 'Count')).reset_index(drop=True)

# Dash application setup
app = dash.Dash(__name__)

# Function to create a timeline figure
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
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Presentations",
        hovermode="x unified",
        legend_title_text="Topics",
        title_font=dict(size=22, family='Arial'),
        template='plotly_white',
    )
    return fig

# Function to create a year-specific figure
def create_year_figure(selected_year):
    year_data = topic_trends[topic_trends['Year'] == selected_year]
    top_5_topics = year_data.nlargest(5, 'Count')
    fig = px.bar(
        top_5_topics,
        x="Topic",
        y="Count",
        title=f'Top 5 Topics in {selected_year}',
        labels={"Count": "Number of Presentations", "Topic": "Topic"}
    )
    fig.update_layout(
        xaxis_title="Topic",
        yaxis_title="Number of Presentations",
        hovermode="closest",
        title_font=dict(size=22, family='Arial'),
        template='plotly_white',
    )
    return fig

# App layout
app.layout = html.Div([
    html.H1("Interactive Presentation Topic Trends", style={'text-align': 'center'}),
    dcc.Graph(id='timeline-graph', figure=create_timeline_figure()),
    dcc.Graph(id='year-graph'),
    dcc.Store(id='selected-year', data=None)
])

# Callback to update year-graph based on click event
@app.callback(
    Output('year-graph', 'figure'),
    Input('timeline-graph', 'clickData')
)
def update_year_graph(clickData):
    if clickData:
        selected_year = clickData['points'][0]['x']
        return create_year_figure(selected_year)
    return {}

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080)
