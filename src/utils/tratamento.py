import pandas as pd
import plotly.express as px
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

def merged():
    base_dir = Path(__file__).resolve().parent.parent

    csv_path = base_dir / "data" / "precos_coletados.csv"
    df = pd.read_csv(csv_path)

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
        mode="lines",  # Add dots at data points
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