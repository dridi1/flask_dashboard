import os
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo, Email
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import psycopg2
from urllib.parse import urlparse
import requests
import matplotlib.pyplot as plt
import geopandas as gpd
import random
import numpy as np
import plotly.express as px
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go



def fetch_geojson_data():
    url = 'http://catalog.industrie.gov.tn/dataset/9910662a-4594-453f-a710-b2f339e0d637/resource/1b7e3eba-b178-4902-83db-ef46f26e98a0/download/delegations.geojson'
    response = requests.get(url)
    data = response.json()
    return gpd.GeoDataFrame.from_features(data)

def Creation_map():
    # Filter by governorates
    governorates = ['Manubah', 'Bizerte', 'Zaghouan', 'Siliana', 'Ben Arous', 'Béja', 'Jendouba', 'Le Kef', 'Ariana']
    ext = fetch_geojson_data()[fetch_geojson_data()['gov_name_f'].isin(governorates)]

    # Generate random values
    random.seed(42)
    cereale_codes = [random.randint(1, 4) for _ in range(len(ext))]
    variete_codes = [random.randint(1, 12) for _ in range(len(ext))]
    superficies = [random.randint(10, 100) for _ in range(len(ext))]
    productions = [random.randint(20, 5000) for _ in range(len(ext))]

    # Add new columns
    ext.loc[:, 'code_cereale'] = cereale_codes
    ext.loc[:, 'code_variete'] = variete_codes
    ext.loc[:, 'superficie'] = superficies
    ext.loc[:, 'production'] = productions

    # Map code to text
    def map_code_to_text(code):
        if code == 1:
            return 'BD'
        elif code == 2:
            return 'BT'
        elif code == 3:
            return 'Tr'
        elif code == 4:
            return 'Or'
        else:
            return 'Unknown'

    ext.loc[:, 'cereale_text'] = ext['code_cereale'].apply(map_code_to_text)
    # Convert GeoDataFrame to GeoJSON
    geojson = ext.__geo_interface__

    # Create the choropleth map with Plotly
    fig = px.choropleth(
        ext,
        geojson=geojson,
        locations=ext.index,
        color='production',
        color_continuous_scale='YlGn',
        hover_data={'cereale_text': True, 'production': True },
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
            'x': 1.05,  # Positioning the color bar
            'xanchor': 'left',
            'y': 0.5,
            'yanchor': 'middle'
        }
    )

    return fig

Creation_map()