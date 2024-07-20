import os
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sqrt')

def create_histogram():
    cereal_data = pd.read_csv(os.path.join('public', 'cereal_data.csv'))
    governorate_data = cereal_data.groupby('gov_name_f_y')[['BD', 'BT', 'Tr', 'Or']].sum().reset_index()
    governorate_data_melted = pd.melt(governorate_data, id_vars='gov_name_f_y', var_name='Cereal', value_name='Quantity')
    fig = px.bar(governorate_data_melted, x='gov_name_f_y', y='Quantity', color='Cereal', title='Cereal Production by Governorate - Simulated Data', labels={'gov_name_f_y': 'Governorate', 'Quantity': 'Total Quantity'}, barmode='group')
    fig.update_layout(xaxis_tickangle=-45, xaxis_title='Governorate', yaxis_title='Total Quantity')
    return fig

def create_bar_chart():
    cereal_data = pd.read_csv(os.path.join('public', 'cereal_data.csv'))
    governorate_data = cereal_data.groupby('gov_name_f_y')[['superficie', 'BD', 'BT', 'Tr', 'Or']].sum().reset_index()
    colors = ['#440154', '#3b528b', '#21908d', '#5dc863']
    fig = go.Figure()
    cereals = ['BD', 'BT', 'Tr', 'Or']
    for i, cereal in enumerate(cereals):
        fig.add_trace(go.Bar(x=governorate_data['gov_name_f_y'], y=governorate_data[cereal], name=cereal, marker_color=colors[i]))
    fig.update_layout(title='Cereal Production as Proportion of Area by Governorate - Simulated Data', xaxis_title='Governorate', yaxis_title='Superficie', barmode='stack', xaxis_tickangle=-45, showlegend=True, plot_bgcolor='white')
    return fig

hist_app = dash.Dash(__name__, server=app, url_base_pathname='/hist/')
bar_chart_app = dash.Dash(__name__, server=app, url_base_pathname='/bar_chart/')

hist_app.layout = html.Div([dcc.Graph(id='hist', figure=create_histogram())])
bar_chart_app.layout = html.Div([dcc.Graph(id='bar', figure=create_bar_chart())])

@app.route('/private_dashboard')
def private_dashboard():
    return render_template('private_dashboard.html')

@app.route('/')
def public_dashboard():
    dash_urls = ['/hist/', '/bar_chart/']
    return render_template('public_dashboard.html', dash_urls=dash_urls)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
