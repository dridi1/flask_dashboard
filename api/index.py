import os
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
import requests
import geopandas as gpd
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'thisisasecretkey')

# Function to fetch GeoJSON data
def fetch_geojson_data():
    url = 'http://catalog.industrie.gov.tn/dataset/9910662a-4594-453f-a710-b2f339e0d637/resource/1b7e3eba-b178-4902-83db-ef46f26e98a0/download/delegations.geojson'
    response = requests.get(url)
    data = response.json()
    return gpd.GeoDataFrame.from_features(data)

def create_map():
    # Filter by governorates
    governorates = ['Manubah', 'Bizerte', 'Zaghouan', 'Siliana', 'Ben Arous', 'Béja', 'Jendouba', 'Le Kef', 'Ariana']
    geo_df = fetch_geojson_data()
    filtered_geo_df = geo_df[geo_df['gov_name_f'].isin(governorates)]

    # Generate random values
    random.seed(42)
    cereale_codes = [random.randint(1, 4) for _ in range(len(filtered_geo_df))]
    variete_codes = [random.randint(1, 12) for _ in range(len(filtered_geo_df))]
    superficies = [random.randint(10, 100) for _ in range(len(filtered_geo_df))]
    productions = [random.randint(20, 5000) for _ in range(len(filtered_geo_df))]

    # Add new columns
    filtered_geo_df['code_cereale'] = cereale_codes
    filtered_geo_df['code_variete'] = variete_codes
    filtered_geo_df['superficie'] = superficies
    filtered_geo_df['production'] = productions

    # Map code to text
    def map_code_to_text(code):
        return {1: 'BD', 2: 'BT', 3: 'Tr', 4: 'Or'}.get(code, 'Unknown')

    filtered_geo_df['cereale_text'] = filtered_geo_df['code_cereale'].apply(map_code_to_text)
    
    # Convert GeoDataFrame to GeoJSON
    geojson = filtered_geo_df.__geo_interface__

    # Create the choropleth map with Plotly
    fig = px.choropleth(
        filtered_geo_df,
        geojson=geojson,
        locations=filtered_geo_df.index,
        color='production',
        color_continuous_scale='YlGn',
        hover_data={'cereale_text': True, 'production': True},
        labels={'production': 'Production', 'cereale_text': 'Cereale Type'},
        hover_name='gov_name_f', 
        title='Map of Production by Governorate - Simulated Data',
        height=895
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=7,
        mapbox_center={"lat": 34.0, "lon": 9.0},
        margin={"r":0,"t":60,"l":0,"b":0},
        coloraxis_colorbar={
            'title': 'Production',
            'tickvals': [min(productions), max(productions)],
            'ticktext': [min(productions), max(productions)],
            'x': 1.05,
            'xanchor': 'left',
            'y': 0.5,
            'yanchor': 'middle'
        }
    )

    return fig

def create_histogram():
    # Read the CSV file
    cereal_data = pd.read_csv('cereal_data.csv')
    
    # Group the data by governorate and sum the cereal quantities
    governorate_data = cereal_data.groupby('gov_name_f_y')[['BD', 'BT', 'Tr', 'Or']].sum().reset_index()

    # Melt the DataFrame to long format for easier plotting
    governorate_data_melted = pd.melt(governorate_data, id_vars='gov_name_f_y', var_name='Cereal', value_name='Quantity')

    # Create the bar plot using Plotly
    fig = px.bar(governorate_data_melted, 
                x='gov_name_f_y', 
                y='Quantity', 
                color='Cereal', 
                title='Cereal Production by Governorate - Simulated Data',
                labels={'gov_name_f_y': 'Governorate', 'Quantity': 'Total Quantity'},
                barmode='group')

    # Update layout for better readability
    fig.update_layout(xaxis_tickangle=-45, xaxis_title='Governorate', yaxis_title='Total Quantity')
    
    return fig

def create_bar_chart():
    cereal_data = pd.read_csv('cereal_data.csv')
    # Group the data by governorate and sum the relevant columns
    governorate_data = cereal_data.groupby('gov_name_f_y')[['superficie', 'BD', 'BT', 'Tr', 'Or']].sum().reset_index()

    # Define the colors for the cereals
    colors = ['#440154', '#3b528b', '#21908d', '#5dc863']  # Example colors from Viridis

    # Create the Plotly figure
    fig = go.Figure()

    # Add traces for each cereal
    cereals = ['BD', 'BT', 'Tr', 'Or']
    for i, cereal in enumerate(cereals):
        fig.add_trace(go.Bar(
            x=governorate_data['gov_name_f_y'],
            y=governorate_data[cereal],
            name=cereal,
            marker_color=colors[i]
        ))

    # Update layout for better readability
    fig.update_layout(
        title='Cereal Production as Proportion of Area by Governorate - Simulated Data',
        xaxis_title='Governorate',
        yaxis_title='Superficie',
        barmode='stack',
        xaxis_tickangle=-45,
        showlegend=True,
        plot_bgcolor='white'  # Change the background color to white
    )
    
    return fig

# Create Dash applications
map_app = dash.Dash(__name__, server=app, url_base_pathname='/tunisia_map/')
hist_app = dash.Dash(__name__, server=app, url_base_pathname='/hist/')
bar_chart_app = dash.Dash(__name__, server=app, url_base_pathname='/bar_chart/')

# Define the layout of the map
map_app.layout = html.Div([
    dcc.Graph(id='map', figure=create_map())
])

# Define the layout of the histogram
hist_app.layout = html.Div([
    dcc.Graph(id='hist', figure=create_histogram())
])

# Define the layout of the bar chart
bar_chart_app.layout = html.Div([
    dcc.Graph(id='bar', figure=create_bar_chart())
])    

@app.route('/private_dashboard')
def private_dashboard():
    return render_template('private_dashboard.html')

@app.route('/')
def public_dashboard():
    dash_urls = ['/tunisia_map/', '/hist/', '/bar_chart/']
    return render_template('public_dashboard.html', dash_urls=dash_urls)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
