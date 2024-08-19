import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Predefined tickers and their categories
tickers_data = {
    "GGAL.BA": "Panel Líder", "YPFD.BA": "Panel Líder", "PAMP.BA": "Panel Líder", "TXAR.BA": "Panel Líder",
    "ALUA.BA": "Panel Líder", "CRES.BA": "Panel Líder", "SUPV.BA": "Panel Líder", "CEPU.BA": "Panel Líder",
    "BMA.BA": "Panel Líder", "TGSU2.BA": "Panel Líder", "TRAN.BA": "Panel Líder", "EDN.BA": "Panel Líder",
    "LOMA.BA": "Panel Líder", "MIRG.BA": "Panel Líder", "DGCU2.BA": "Panel General", "BBAR.BA": "Panel Líder",
    "MOLI.BA": "Panel General", "TGNO4.BA": "Panel Líder", "CGPA2.BA": "Panel General", "COME.BA": "Panel Líder",
    "IRSA.BA": "Panel Líder", "BYMA.BA": "Panel Líder", "TECO2.BA": "Panel Líder", "METR.BA": "Panel General",
    "CECO2.BA": "Panel General", "BHIP.BA": "Panel General", "AGRO.BA": "Panel General", "LEDE.BA": "Panel General",
    "CVH.BA": "Panel General", "HAVA.BA": "Panel General", "AUSO.BA": "Panel General", "VALO.BA": "Panel Líder",
    "SEMI.BA": "Panel General", "INVJ.BA": "Panel General", "CTIO.BA": "Panel General", "MORI.BA": "Panel General",
    "HARG.BA": "Panel General", "GCLA.BA": "Panel General", "SAMI.BA": "Panel General", "BOLT.BA": "Panel General",
    "MOLA.BA": "Panel General", "CAPX.BA": "Panel General", "OEST.BA": "Panel General", "LONG.BA": "Panel General",
    "GCDI.BA": "Panel General", "GBAN.BA": "Panel General", "CELU.BA": "Panel General", "FERR.BA": "Panel General",
    "CADO.BA": "Panel General", "GAMI.BA": "Panel General", "PATA.BA": "Panel General", "CARC.BA": "Panel General",
    "BPAT.BA": "Panel General", "RICH.BA": "Panel General", "INTR.BA": "Panel General", "GARO.BA": "Panel General",
    "FIPL.BA": "Panel General", "GRIM.BA": "Panel General", "DYCA.BA": "Panel General", "POLL.BA": "Panel General",
    "DOME.BA": "Panel General", "ROSE.BA": "Panel General", "RIGO.BA": "Panel General", "DGCE.BA": "Panel General",
    "^MERV": "Panel Líder", "MTR.BA": "Panel General"
}

# Helper function to find the most recent valid trading date
def get_recent_valid_date(tickers, date):
    while True:
        try:
            data = yf.download(tickers, start=date, end=date + pd.Timedelta(days=1))
            if not data.empty and not data['Adj Close'].isnull().all().all():
                return date
        except:
            pass
        date -= pd.Timedelta(days=1)

def fetch_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date + pd.Timedelta(days=1))['Adj Close']
    
    # Fill missing data with the last available value
    data.fillna(method='ffill', inplace=True)
    
    # Check if end_date has data, if not, fetch the most recent available date
    if end_date not in data.index:
        end_date = get_recent_valid_date(tickers, end_date)
    
    # Check if start_date has data, if not, fetch the most recent available date
    if start_date not in data.index:
        start_date = get_recent_valid_date(tickers, start_date)
    
    return data, start_date, end_date

# Streamlit UI
st.title('Análisis de Crecimiento de Precios de Acciones')

# Date inputs
start_date = st.date_input("Fecha de inicio", pd.to_datetime("2023-01-01"))
end_date = st.date_input("Fecha de finalización", pd.to_datetime("today"))

# Fetch data and handle dates
if st.button('Obtener Datos y Graficar'):
    tickers = list(tickers_data.keys())
    data, start_date, end_date = fetch_data(tickers, start_date, end_date)

    percentage_changes = {}
    for ticker in tickers:
        if ticker not in data.columns:
            st.warning(f"No se encontró el ticker '{ticker}' en los datos.")
            continue
        
        start_price = data[ticker].loc[start_date]
        end_price = data[ticker].loc[end_date]
        
        # Calculate percentage change
        percentage_change = ((end_price - start_price) / start_price) * 100
        percentage_changes[ticker] = percentage_change
    
    # Create bubble chart
    fig = go.Figure()

    for ticker, change in percentage_changes.items():
        color = 'white' if change == 0 else ('darkgreen' if change > 0 else 'darkred')
        size = abs(change) * 10  # Scale the size for better visualization

        fig.add_trace(go.Scatter(
            x=[ticker],
            y=[change],
            mode='markers+text',
            marker=dict(size=size, color=color, opacity=0.8),
            text=[ticker],
            textposition='middle center',
            name=f'{ticker} ({change:.2f}%)'
        ))

    fig.update_layout(
        title='Cambio porcentual de precios de acciones',
        xaxis_title='Ticker',
        yaxis_title='Cambio Porcentual (%)',
        xaxis=dict(tickvals=list(tickers_data.keys()), ticktext=list(tickers_data.keys())),
        yaxis=dict(showgrid=True),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
