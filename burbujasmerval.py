import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Define the updated ticker symbols
tickers = [
    "GGAL.BA", "YPFD.BA", "PAMP.BA", "TXAR.BA", "ALUA.BA", "CRES.BA", "SUPV.BA", "CEPU.BA", "BMA.BA",
    "TGSU2.BA", "TRAN.BA", "EDN.BA", "LOMA.BA", "MIRG.BA", "DGCU2.BA", "BBAR.BA", "MOLI.BA", "TGNO4.BA",
    "CGPA2.BA", "COME.BA", "IRSA.BA", "BYMA.BA", "TECO2.BA", "METR.BA", "CECO2.BA", "BHIP.BA", "AGRO.BA",
    "LEDE.BA", "CVH.BA", "HAVA.BA", "AUSO.BA", "VALO.BA", "SEMI.BA", "INVJ.BA", "CTIO.BA", "MORI.BA",
    "HARG.BA", "GCLA.BA", "SAMI.BA", "BOLT.BA", "MOLA.BA", "CAPX.BA", "OEST.BA", "LONG.BA", "GCDI.BA",
    "GBAN.BA", "CELU.BA", "FERR.BA", "CADO.BA", "GAMI.BA", "PATA.BA", "CARC.BA", "BPAT.BA", "RICH.BA",
    "INTR.BA", "GARO.BA", "FIPL.BA", "GRIM.BA", "DYCA.BA", "POLL.BA", "DGCE.BA", "DOME.BA", "ROSE.BA",
    "RIGO.BA", "MTR.BA"
]

# Fetch data from Yahoo Finance
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="5d").reset_index()
    df = df.drop_duplicates(subset='Date')
    return df

# Calculate the price variation only for the last trading day
def process_last_day(df):
    df['Price Variation'] = df['Close'].pct_change() * 100  # Percentage change from the previous day
    df['Volume * Price'] = df['Volume'] * df['Close']
    last_day_df = df.iloc[-1:]
    return last_day_df

# Create scatter plot with annotations and arrows
def create_plot(df):
    min_price_var = df['Price Variation'].min() - 5
    max_price_var = df['Price Variation'].max() + 5
    min_volume_price = df['Volume * Price'].min() * 0.9
    max_volume_price = df['Volume * Price'].max() * 1.1

    # Create scatter plot
    fig = px.scatter(
        df,
        x='Price Variation',
        y='Volume * Price',
        color='Price Variation', 
        log_y=True,
        range_x=[min_price_var, max_price_var],
        range_y=[min_volume_price, max_volume_price],
        hover_name='Ticker',
        title='Price Variation (Last Trading Day) vs Volume * Price',
        labels={"Price Variation": "Price Variation (%)", "Volume * Price": "Volume * Price (Log Scale)"}
    )

    # Add red line separating positive and negative values
    fig.add_shape(
        type="line",
        x0=0, y0=min_volume_price, x1=0, y1=max_volume_price,
        line=dict(color="red", width=2),
        xref="x", yref="y"
    )

    # Add ticker names as annotations with arrows
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row['Price Variation'],
            y=row['Volume * Price'],
            text=row['Ticker'],
            showarrow=True,
            arrowhead=2,  
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="black",
            ax=row['Price Variation'] + (10 if row['Price Variation'] < 0 else -10),  # Horizontal offset for arrow
            ay=row['Volume * Price'] * 0.5,  # Vertical offset for arrow
            font=dict(size=12),
            xanchor='center',
            yanchor='bottom',
            bgcolor="white",  # Background for text to make it visible
        )

    return fig

# Streamlit app layout
st.title("Price Variation (Last Trading Day) vs Volume * Price for Selected Argentine Stocks")

# Fetch and process data for all tickers
data_frames = []
for ticker in tickers:
    df = fetch_data(ticker)
    df = process_last_day(df)
    df['Ticker'] = ticker
    data_frames.append(df)

combined_df = pd.concat(data_frames).drop_duplicates(subset=['Date', 'Ticker'])

# Create the scatter plot
scatter_plot = create_plot(combined_df)

# Display the plot in Streamlit
st.plotly_chart(scatter_plot)
