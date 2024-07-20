import os
from flask import Flask, render_template
import requests
#import geopandas as gpd
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sqrt')

# Function to fetch GeoJSON data

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

hist_app = dash.Dash(__name__, server=app, url_base_pathname='/hist/')
bar_chart_app = dash.Dash(__name__, server=app, url_base_pathname='/bar_chart/')

# Define the layout of the map


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
    app.run(debug=True, port=8002)
