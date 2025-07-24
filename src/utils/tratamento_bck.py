import pandas as pd
import plotly.express as px
import warnings
import os
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

warnings.filterwarnings('ignore')

def merged():

    load_dotenv()
    MONGO_USER = os.getenv("mongo_user")
    MONGO_PASS = os.getenv("mongo_pass")

    uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@fraldas.1gjvb.mongodb.net/?retryWrites=true&w=majority&appName=fraldas"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    database = client['fraldas']
    collection = database['price_tracking']

    results = collection.find()

    df = pd.DataFrame(results)
    df.drop('_id', axis=1, inplace=True)

    client.close()

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df

def line_chart(df):
    fig = px.line(df, x="timestamp", y="UNIDADE", template="mantine_light")

    return adjust_chart(fig)

def line_chart_produtos(df):
    fig = px.line(df, x="timestamp", y="UNIDADE", color='QUALIDADE', template="mantine_light")

    fig.update_layout(legend=dict(
        title=None,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=8)
    ))

    return adjust_chart(fig)

def adjust_chart(fig):

    fig.update_traces(
        line=dict(width=2, shape="hvh",smoothing=0.1),  # Match DMC line color & thickness
        mode="markers+lines",  # Add dots at data points
        marker=dict(size=5, color="white",line=dict(width=1,color='blue')),  # Match DMC dot color & size
    )

    fig.update_xaxes(
        title=None,
        showgrid=False,  # Keep gridlines visible
        tickangle=0,  # Ensure horizontal labels
        # tickformat="%Y-%m-%d",  # Dense tick format like DMC
        showline=False,  # Add border line
    )

    fig.update_yaxes(
        title=None,
        showgrid=True,  # Ensure grid visibility
        gridwidth=1,
        gridcolor='lightgray',
        griddash='dash',
        zeroline=False,
        showline=False,  # Add border line
        linecolor="green",
    )

    fig.update_layout(
        font=dict(size=12,color='gray'),
        plot_bgcolor="white",  # Match DMC background
        margin=dict(l=0, r=0, t=0, b=0, pad=20),  # Remove extra margins
        hovermode="x unified"  # More structured hover interaction
    )

    return fig

merged_df = merged()