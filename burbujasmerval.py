import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Define the updated ticker symbols
tickers = {
    "GGAL.BA", "YPFD.BA", "PAMP.BA", "TXAR.BA", "ALUA.BA", "CRES.BA", "SUPV.BA", "CEPU.BA", "BMA.BA",
    "TGSU2.BA", "TRAN.BA", "EDN.BA", "LOMA.BA", "MIRG.BA", "DGCU2.BA", "BBAR.BA", "MOLI.BA", "TGNO4.BA",
    "CGPA2.BA", "COME.BA", "IRSA.BA", "BYMA.BA", "TECO2.BA", "METR.BA", "CECO2.BA", "BHIP.BA", "AGRO.BA",
    "LEDE.BA", "CVH.BA", "HAVA.BA", "AUSO.BA", "VALO.BA", "SEMI.BA", "INVJ.BA", "CTIO.BA", "MORI.BA",
    "HARG.BA", "GCLA.BA", "SAMI.BA", "BOLT.BA", "MOLA.BA", "CAPX.BA", "OEST.BA", "LONG.BA", "GCDI.BA",
    "GBAN.BA", "CELU.BA", "FERR.BA", "CADO.BA", "GAMI.BA", "PATA.BA", "CARC.BA", "BPAT.BA", "RICH.BA",
    "INTR.BA", "GARO.BA", "FIPL.BA", "GRIM.BA", "DYCA.BA", "POLL.BA", "DGCE.BA", "DOME.BA", "ROSE.BA",
    "RIGO.BA", "MTR.BA"
}

# Fetch data from Yahoo Finance
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    # Fetch last 5 days of data for safety and ensure no duplicates by resetting the index
    df = stock.history(period="5d").reset_index()
    # Drop duplicate dates if any
    df = df.drop_duplicates(subset='Date')
    return df

# Calculate price variation and volume * price
def process_data(df):
    df['Price Variation'] = df['Close'].pct_change() * 100  # Percentage change from previous day
    df['Volume * Price'] = df['Volume'] * df['Close']  # Volume * Price
    return df

# Create scatter plot
def create_plot(df):
    # Remove the first day (NaN for price variation)
    df = df.dropna(subset=['Price Variation'])
    
    # Filter out non-positive Volume * Price values for log scale
    df = df[df['Volume * Price'] > 0]

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
        log_y=True,  # Log scale for Y-axis
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
st.title("Price Variation vs Volume * Price for Selected Argentine Stocks")

# Fetch and process data for all tickers
data_frames = []
for ticker in tickers:
    df = fetch_data(ticker)
    df = process_data(df)
    df['Ticker'] = ticker  # Add ticker as a column
    data_frames.append(df)

# Combine all data into a single dataframe
combined_df = pd.concat(data_frames).drop_duplicates(subset=['Date', 'Ticker'])  # Ensure no duplicate tickers/dates

# Create the scatter plot
scatter_plot = create_plot(combined_df)

# Display the plot in Streamlit
st.plotly_chart(scatter_plot)
