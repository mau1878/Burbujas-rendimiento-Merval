import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Define the list of Argentine stocks
stocks = {
    "GGAL.BA": "Panel Líder",
    "YPFD.BA": "Panel Líder",
    "PAMP.BA": "Panel Líder",
    "TXAR.BA": "Panel Líder",
    "ALUA.BA": "Panel Líder",
    "CRES.BA": "Panel Líder",
    "SUPV.BA": "Panel Líder",
    "CEPU.BA": "Panel Líder",
    "BMA.BA": "Panel Líder",
    "TGSU2.BA": "Panel Líder",
    "TRAN.BA": "Panel Líder",
    "EDN.BA": "Panel Líder",
    "LOMA.BA": "Panel Líder",
    "MIRG.BA": "Panel Líder",
    "DGCU2.BA": "Panel General",
    "BBAR.BA": "Panel Líder",
    "MOLI.BA": "Panel General",
    "TGNO4.BA": "Panel Líder",
    "CGPA2.BA": "Panel General",
    "COME.BA": "Panel Líder",
    "IRSA.BA": "Panel Líder",
    "BYMA.BA": "Panel Líder",
    "TECO2.BA": "Panel Líder",
    "METR.BA": "Panel General",
    "CECO2.BA": "Panel General",
    "BHIP.BA": "Panel General",
    "AGRO.BA": "Panel General",
    "LEDE.BA": "Panel General",
    "CVH.BA": "Panel General",
    "HAVA.BA": "Panel General",
    "AUSO.BA": "Panel General",
    "VALO.BA": "Panel Líder",
    "SEMI.BA": "Panel General",
    "INVJ.BA": "Panel General",
    "CTIO.BA": "Panel General",
    "MORI.BA": "Panel General",
    "HARG.BA": "Panel General",
    "GCLA.BA": "Panel General",
    "SAMI.BA": "Panel General",
    "BOLT.BA": "Panel General",
    "MOLA.BA": "Panel General",
    "CAPX.BA": "Panel General",
    "OEST.BA": "Panel General",
    "LONG.BA": "Panel General",
    "GCDI.BA": "Panel General",
    "GBAN.BA": "Panel General",
    "CELU.BA": "Panel General",
    "FERR.BA": "Panel General",
    "CADO.BA": "Panel General",
    "GAMI.BA": "Panel General",
    "PATA.BA": "Panel General",
    "CARC.BA": "Panel General",
    "BPAT.BA": "Panel General",
    "RICH.BA": "Panel General",
    "INTR.BA": "Panel General",
    "GARO.BA": "Panel General",
    "FIPL.BA": "Panel General",
    "GRIM.BA": "Panel General",
    "DYCA.BA": "Panel General",
    "POLL.BA": "Panel General",
    "DOME.BA": "Panel General",
    "ROSE.BA": "Panel General",
    "RIGO.BA": "Panel General",
    "DGCE.BA": "Panel General",
    "^MERV": "Panel Líder",
    "MTR.BA": "Panel General"
}

# Streamlit UI
st.title('Análisis de Cambios de Precio de Acciones del MERVAL')

# Date inputs
start_date = st.date_input("Fecha de inicio", pd.to_datetime("2023-01-01"))
end_date = st.date_input("Fecha de finalización", pd.to_datetime("today"))

# Fetch prices for each stock
def fetch_prices(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
            df = df.fillna(method='ffill')  # Fill missing values with last available
            data[ticker] = df
        except Exception as e:
            st.warning(f"No se pudo descargar datos para {ticker}: {e}")
    return data

# Calculate percentage changes
def calculate_percentage_change(data, start_date, end_date):
    percentage_changes = {}
    for ticker, df in data.items():
        if start_date in df.index and end_date in df.index:
            start_price = df.loc[start_date]
            end_price = df.loc[end_date]
            change = ((end_price - start_price) / start_price) * 100
            percentage_changes[ticker] = change
        else:
            st.warning(f"No hay datos disponibles para {ticker} en las fechas seleccionadas.")
    return percentage_changes

# Define color scale
def get_color(change):
    if change > 0:
        return f"rgba(0, 128, 0, {min(change / 100, 1)})"  # Dark green
    elif change < 0:
        return f"rgba(255, 0, 0, {min(-change / 100, 1)})"  # Dark red
    else:
        return "white"

# Fetch data
data = fetch_prices(stocks.keys(), start_date, end_date)
percentage_changes = calculate_percentage_change(data, start_date, end_date)

# Plotting
if percentage_changes:
    fig = go.Figure()

    for ticker, change in percentage_changes.items():
        fig.add_trace(go.Scatter(
            x=[ticker], 
            y=[change], 
            mode='markers+text',
            marker=dict(
                size=abs(change) * 5,  # Size of the bubble
                color=get_color(change),  # Color based on the change
                line=dict(color='black', width=1)
            ),
            text=[f"{ticker}: {change:.2f}%"],  # Display ticker and percentage change
            textposition='middle center'
        ))

    fig.update_layout(
        title='Cambios de Precio de Acciones',
        xaxis_title='Ticker',
        yaxis_title='Cambio (%)',
        yaxis=dict(range=[min(percentage_changes.values()) - 10, max(percentage_changes.values()) + 10]),
        xaxis=dict(tickvals=list(stocks.keys()), ticktext=list(stocks.keys())),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No se encontraron datos para graficar.")
