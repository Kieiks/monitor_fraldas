import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import os
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

warnings.filterwarnings('ignore')

def load_data():

    load_dotenv()
    MONGO_USER = os.getenv("mongo_user")
    MONGO_PASS = os.getenv("mongo_pass")

    uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@fraldas.1gjvb.mongodb.net/?retryWrites=true&w=majority&appName=fraldas"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    database = client['essentiel']
    collection = database['pourbebe']

    results = collection.find()

    df = pd.DataFrame(results)
    client.close()

    df.drop('_id', axis=1, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    df = df[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(days=90)]
    df = df.query('ESTOQUE_AJUSTADO == 1')

    df = df.round(2)

    return df

def trend_chart(df):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['min'], 
        mode='lines+markers',
        line=dict(width=3, color='rgba(0, 90, 150, 0.9)'),
        marker=dict(size=6, color='white', line=dict(width=2, color='rgba(0, 90, 150, 0.9)')),
        line_shape='hvh',
        name='Mínimo',
        hovertemplate='Menor Preço: R$ %{y}<extra></extra>'
    ))

    fig.update_yaxes(
        gridcolor='rgba(0,0,0,0.08)',
        zeroline=False,
        showline=False,
        title=''
    )

    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='rgba(0,0,0,0.0)',
        paper_bgcolor='rgba(0,0,0,0.0)',
        font=dict(family='Arial', size=14, color='black'),
        hovermode='x unified',
    )
    
    return fig

# merged_df = load_data()
# print(merged_df.info())