import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the updated ticker symbols
tickers = [
    "GGAL.BA", "YPFD.BA", "PAMP.BA", "TXAR.BA", "ALUA.BA", "CRES.BA", "SUPV.BA", "CEPU.BA", "BMA.BA",
    "TGSU2.BA", "TRAN.BA", "EDN.BA", "LOMA.BA", "MIRG.BA", "DGCU2.BA", "BBAR.BA", "MOLI.BA", "TGNO4.BA",
    "CGPA2.BA", "COME.BA", "IRSA.BA", "BYMA.BA", "TECO2.BA", "METR.BA", "CECO2.BA", "BHIP.BA", "AGRO.BA",
    "LEDE.BA", "CVH.BA", "HAVA.BA", "AUSO.BA", "VALO.BA", "SEMI.BA", "INVJ.BA", "CTIO.BA", "MORI.BA",
    "HARG.BA", "GCLA.BA", "SAMI.BA", "BOLT.BA", "MOLA.BA", "CAPX.BA", "OEST.BA", "LONG.BA", "GCDI.BA",
    "GBAN.BA", "CELU.BA", "FERR.BA", "CADO.BA", "HSAT.BA", "PATA.BA", "CARC.BA", "BPAT.BA", "RICH.BA",
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
    # Remove duplicates if any
    df = df.drop_duplicates()
    
    # Ensure there are no duplicate indices
    df = df[~df.index.duplicated(keep='first')]

    min_price_var = df['Price Variation'].min() - 5
    max_price_var = df['Price Variation'].max() + 5
    min_volume_price = df['Volume * Price'].min() * 0.9
    max_volume_price = df['Volume * Price'].max() * 1.1

    plt.figure(figsize=(12, 8))
    
    # Scatter plot
    scatter = sns.scatterplot(
        x='Price Variation',
        y='Volume * Price',
        hue='Price Variation',
        data=df,
        palette='coolwarm',
        s=100
    )
    
    # Add red line separating positive and negative values
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2)
    
    # Annotate each point
    for i, row in df.iterrows():
        scatter.annotate(
            row['Ticker'],
            (row['Price Variation'], row['Volume * Price']),
            xytext=(5, 5),
            textcoords='offset points',
            arrowprops=dict(
                arrowstyle='->',
                color='black',
                lw=1
            ),
            fontsize=10
        )
    
    # Formatting the y-axis to a log scale
    plt.yscale('log')
    plt.xlabel('Price Variation (%)')
    plt.ylabel('Volume * Price (Log Scale)')
    plt.title('Price Variation (Last Trading Day) vs Volume * Price')
    
    # Show plot grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    return plt

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

# Ensure the combined DataFrame does not have duplicate indices
combined_df = combined_df[~combined_df.index.duplicated(keep='first')]

# Create the scatter plot
plot = create_plot(combined_df)

# Display the plot in Streamlit
st.pyplot(plot)
