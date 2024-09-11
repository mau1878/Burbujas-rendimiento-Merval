import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Define ticker symbols
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

# Fetch data from Yahoo Finance with error handling and fallback to previous data if necessary
def fetch_data(ticker, start_date, end_date):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date).reset_index()
        df = df.drop_duplicates(subset='Date')
        return df
    except Exception as e:
        st.warning(f"Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame()

# Process only the last available day of stock data
def process_last_day(df):
    df['Price Variation'] = df['Close'].pct_change() * 100  # Percentage change from the previous day
    df['Volume * Price'] = df['Volume'] * df['Close']
    last_day_df = df.iloc[-1:]
    return last_day_df

# Create scatter plot with improved annotations
def create_plot(df):
    min_price_var = df['Price Variation'].min() - 5
    max_price_var = df['Price Variation'].max() + 5
    min_volume_price = df['Volume * Price'].min() * 0.9
    max_volume_price = df['Volume * Price'].max() * 1.1

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

    # Add ticker names as annotations
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
            ax=row['Price Variation'] + (15 if row['Price Variation'] < 0 else -15),  
            ay=row['Volume * Price'] + 50,
            font=dict(size=10, color="black"),
            bgcolor="white",
            borderpad=4
        )

    fig.update_layout(
        xaxis_title="Price Variation (%)",
        yaxis_title="Volume * Price (Log Scale)",
        xaxis=dict(zeroline=False),
        yaxis=dict(type='log', zeroline=False),
        autosize=True
    )
    
    return fig

# Streamlit app layout
st.title("Price Variation (Last Trading Day) vs Volume * Price for Selected Argentine Stocks")

# Add date selection widget
start_date = st.date_input("Select start date", pd.Timestamp.today() - pd.DateOffset(10))
end_date = st.date_input("Select end date", pd.Timestamp.today())

# Allow user to select tickers to display
selected_tickers = st.multiselect("Select tickers to display", tickers, default=tickers[:5])

# Fetch and process data for selected tickers
data_frames = []
for ticker in selected_tickers:
    df = fetch_data(ticker, start_date, end_date)
    if not df.empty:
        df = process_last_day(df)
        df['Ticker'] = ticker
        data_frames.append(df)

# Concatenate all data into one dataframe
if data_frames:
    combined_df = pd.concat(data_frames).drop_duplicates(subset=['Date', 'Ticker'])

    # Create the scatter plot
    scatter_plot = create_plot(combined_df)

    # Display the plot in Streamlit
    st.plotly_chart(scatter_plot)

    # Display metadata as a table
    st.subheader("Stock Data Summary")
    st.dataframe(combined_df[['Ticker', 'Price Variation', 'Volume * Price']].set_index('Ticker'))
else:
    st.warning("No data available for the selected tickers.")
