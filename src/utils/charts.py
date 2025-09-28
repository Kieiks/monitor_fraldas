import plotly.graph_objects as go
import pandas as pd
import numpy as np

def trend_chart(df):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['min_value'], 
        mode='lines+markers',
        line=dict(width=3, color='rgba(0, 90, 150, 0.9)'),
        marker=dict(size=6, color='white', line=dict(width=2, color='rgba(0, 90, 150, 0.9)')),
        line_shape='hvh',
        name='Mínimo',
        hovertemplate='Menor Preço: R$ %{y:.2f}<extra></extra>'
    ))

    fig.update_xaxes(
        tickformat="%d-%m",
        # tickangle=-30,
        showline=True,
        showgrid=False,
        linecolor="rgba(0,0,0,0.25)"
    )

    fig.update_yaxes(
        gridcolor='rgba(0,0,0,0.05)',
        zeroline=False,
        showline=False,
        title='',
        tickprefix="R$ ",
        tickformat=",.2f"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0.0)',
        paper_bgcolor='rgba(0,0,0,0.0)',
        font=dict(family='Arial', size=14, color='black'),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family='Arial'
        ),
        height=300,
    )
    
    return fig

def recomendation_chart(df):
    vmin = df['min_value'].min()
    vmax = df['min_value'].max()

    extra_margin = (vmax - vmin)*0.1

    current_value = df['min_value'].values[-1]

    gradient_x = np.linspace(vmin, vmax, 200)

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            z=[gradient_x],
            x=gradient_x,
            y=[0],
            colorscale="Tealrose",   # green → yellow → red
            showscale=False
        )
    )

    fig.add_trace(go.Scatter(
        x=[current_value],
        y=[1],
        mode="markers",
        marker=dict(symbol="triangle-down", size=20, color="black"),
        showlegend=False
    ))

    fig.update_traces(hoverinfo="skip")

    fig.update_layout(
        height=40,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(range=[vmin - extra_margin, vmax + extra_margin], showticklabels=False, visible=False),
        yaxis=dict(showticklabels=False, visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig