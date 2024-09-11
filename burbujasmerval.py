import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Define the ticker symbols
tickers = {
    "GGAL.BA": "Panel Líder", "YPFD.BA": "Panel Líder", "PAMP.BA": "Panel Líder",
    "TXAR.BA": "Panel Líder", "ALUA.BA": "Panel Líder", "CRES.BA": "Panel Líder",
    "SUPV.BA": "Panel Líder", "CEPU.BA": "Panel Líder", "BMA.BA": "Panel Líder",
    "TGSU2.BA": "Panel Líder", "TRAN.BA": "Panel Líder", "EDN.BA": "Panel Líder",
    "LOMA.BA": "Panel Líder", "MIRG.BA": "Panel Líder", "DGCU2.BA": "Panel General",
    "BBAR.BA": "Panel Líder", "MOLI.BA": "Panel General", "TGNO4.BA": "Panel Líder",
    "CGPA2.BA": "Panel General", "COME.BA": "Panel Líder", "IRSA.BA": "Panel Líder",
    "BYMA.BA": "Panel Líder", "TECO2.BA": "Panel Líder", "METR.BA": "Panel General",
    "CECO2.BA": "Panel General", "BHIP.BA": "Panel General", "AGRO.BA": "Panel General",
    "LEDE.BA": "Panel General", "CVH.BA": "Panel General", "HAVA.BA": "Panel General",
    "AUSO.BA": "Panel General", "VALO.BA": "Panel Líder", "SEMI.BA": "Panel General",
    "INVJ.BA": "Panel General", "CTIO.BA": "Panel General", "MORI.BA": "Panel General",
    "HARG.BA": "Panel General", "GCLA.BA": "Panel General", "SAMI.BA": "Panel General",
    "BOLT.BA": "Panel General", "MOLA.BA": "Panel General", "CAPX.BA": "Panel General",
    "OEST.BA": "Panel General", "LONG.BA": "Panel General", "GCDI.BA": "Panel General",
    "GBAN.BA": "Panel General", "CELU.BA": "Panel General", "FERR.BA": "Panel General",
    "CADO.BA": "Panel General", "GAMI.BA": "Panel General", "PATA.BA": "Panel General",
    "CARC.BA": "Panel General", "BPAT.BA": "Panel General", "RICH.BA": "Panel General",
    "INTR.BA": "Panel General", "GARO.BA": "Panel General", "FIPL.BA": "Panel General",
    "GRIM.BA": "Panel General", "DYCA.BA": "Panel General", "POLL.BA": "Panel General",
    "DOME.BA": "Panel General", "ROSE.BA": "Panel General", "RIGO.BA": "Panel General",
    "DGCE.BA": "Panel General", "^MERV": "Panel Líder", "MTR.BA": "Panel General"
}

# Fetch data from Yahoo Finance
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="5d")  # Fetch last 5 days of data for safety

# Calculate price variation and volume * price
def process_data(df):
    df['Price Variation'] = df['Close'].pct_change() * 100  # Percentage change from previous day
    df['Volume * Price'] = df['Volume'] * df['Close']  # Volume * Price
    return df

# Create scatter plot
def create_plot(df):
    # Remove the first day (NaN for price variation)
    df = df.dropna(subset=['Price Variation'])
    
    # Filter outliers based on interquartile range (IQR)
    Q1 = df['Price Variation'].quantile(0.25)
    Q3 = df['Price Variation'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df['Price Variation'] < lower_bound) | (df['Price Variation'] > upper_bound)]
    non_outliers = df[(df['Price Variation'] >= lower_bound) & (df['Price Variation'] <= upper_bound)]

    # Dynamically adjust axis limits to avoid large empty spaces
    min_price_var = non_outliers['Price Variation'].min() - 5  # Add margin for clarity
    max_price_var = non_outliers['Price Variation'].max() + 5
    min_volume_price = non_outliers['Volume * Price'].min() * 0.9
    max_volume_price = non_outliers['Volume * Price'].max() * 1.1

    # Create scatter plot
    fig = px.scatter(
        non_outliers,
        x='Price Variation',
        y='Volume * Price',
        log_y=True,
        range_x=[min_price_var, max_price_var],  # Dynamic X range
        range_y=[min_volume_price, max_volume_price],  # Dynamic Y range
        hover_name='Ticker',
        title='Price Variation vs Volume * Price',
        labels={"Price Variation": "Price Variation (%)", "Volume * Price": "Volume * Price (Log Scale)"}
    )

    # Annotate outliers
    for i, row in outliers.iterrows():
        fig.add_annotation(
            x=row['Price Variation'],
            y=row['Volume * Price'],
            text=row['Ticker'],
            showarrow=True,
            arrowhead=2
        )

    return fig

# Streamlit app layout
st.title("Price Variation vs Volume * Price for Panel Líder and General Stocks")

# Fetch and process data for all tickers
data_frames = []
for ticker in tickers.keys():
    df = fetch_data(ticker)
    df = process_data(df)
    df['Ticker'] = ticker  # Add ticker as a column
    data_frames.append(df)

# Combine all data into a single dataframe
combined_df = pd.concat(data_frames)

# Create the scatter plot
scatter_plot = create_plot(combined_df)

# Display the plot in Streamlit
st.plotly_chart(scatter_plot)
