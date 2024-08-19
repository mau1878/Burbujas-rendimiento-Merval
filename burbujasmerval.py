import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# List of Argentine stocks with their categories
stocks = {
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

# Helper function to find the closest available date
def get_closest_date(ticker, date):
    data = yf.download(ticker, start=date - pd.Timedelta(days=365), end=date)['Adj Close']
    available_dates = data.index
    if date in available_dates:
        return date
    closest_date = available_dates[available_dates.get_indexer([date], method='pad')[0]]
    return closest_date

# Streamlit UI
st.title('Análisis de Cambios de Precio de Acciones Argentinas')

# Date inputs
start_date = st.date_input("Fecha de inicio", pd.to_datetime("2023-01-01"))
end_date = st.date_input("Fecha de finalización", pd.to_datetime("today"))

# Fetch and process data
if st.button('Obtener Datos y Graficar'):
    prices = {}
    for stock in stocks.keys():
        try:
            # Fetch data
            data = yf.download(stock, start=start_date - pd.Timedelta(days=365), end=end_date + pd.Timedelta(days=1))['Adj Close']
            
            # Get closest available dates
            start_date_closest = get_closest_date(stock, start_date)
            end_date_closest = get_closest_date(stock, end_date)
            
            if start_date_closest in data.index and end_date_closest in data.index:
                start_price = data.loc[start_date_closest]
                end_price = data.loc[end_date_closest]
                percentage_change = (end_price - start_price) / start_price * 100
                prices[stock] = {
                    'percentage_change': percentage_change,
                    'size': abs(percentage_change),
                    'color': 'darkgreen' if percentage_change > 0 else 'darkred' if percentage_change < 0 else 'white'
                }
            else:
                st.warning(f"No hay datos disponibles para el ticker '{stock}' en las fechas seleccionadas.")
        except Exception as e:
            st.error(f"Error al procesar el ticker '{stock}': {e}")

    # Prepare data for plotting
    if prices:
        fig = go.Figure()

        for stock, info in prices.items():
            fig.add_trace(go.Scatter(
                x=[stock],
                y=[info['percentage_change']],
                mode='markers+text',
                marker=dict(
                    size=info['size'] * 10,  # Scale size for better visibility
                    color=info['color']
                ),
                text=[stock],
                textposition='middle center'
            ))

        fig.update_layout(
            title='Cambios de Precio de Acciones Argentinas',
            xaxis_title='Acciones',
            yaxis_title='Cambio en Porcentaje (%)',
            yaxis=dict(range=[min(p['percentage_change'] for p in prices.values()) - 10, 
                              max(p['percentage_change'] for p in prices.values()) + 10]),
            xaxis=dict(tickvals=list(prices.keys()), ticktext=list(prices.keys()))
        )

        st.plotly_chart(fig, use_container_width=True)
