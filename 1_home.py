import os
import webbrowser
import folium
import pandas as pd
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import folium_static


# Função para limpar e converter valores de preço
def clean_and_convert_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "")
    return float(price_str)


# Funções para formatar latitude e longitude
def format_latitude(number_str):
    return number_str[:2] + '.' + number_str[2:]


def format_longitude(number_str):
    if number_str[0] == '-':
        return number_str[0] + number_str[1] + '.' + number_str[2:]
    else:
        return number_str[0] + '.' + number_str[1:]


# Carregar e processar o conjunto de dados
def load_and_process_data():
    dataset = pd.read_csv("datasets/listings.csv", sep=';', encoding='latin-1', index_col=0)
    dataset["price"] = dataset["price"].apply(clean_and_convert_price)

    # Remover linhas com valores ausentes
    dataset = dataset.dropna(subset=['latitude', 'longitude'])

    # Limpar os valores das colunas de latitude e longitude
    dataset['latitude_srt'] = dataset['latitude'].astype(str)
    dataset['longitude_srt'] = dataset['longitude'].astype(str)

    dataset['latitude_srt'] = dataset['latitude_srt'].apply(format_latitude)
    dataset['longitude_srt'] = dataset['longitude_srt'].apply(format_longitude)

    dataset['latitude'] = dataset['latitude_srt'].astype(float)
    dataset['longitude'] = dataset['longitude_srt'].astype(float)

    return dataset


def configure_heatmap(dataset):
    mapa = folium.Map(location=["39.557191", "-7.8536599"], zoom_start=7)

    # Selecionar as colunas de latitude e longitude
    lat_lon_data = dataset[["latitude", "longitude"]]

    # Agrupar e contar os dados
    heat_data = lat_lon_data.groupby(["latitude", "longitude"]).size().reset_index(name="count")
    heat_data = heat_data.values.tolist()

    heat_map = HeatMap(heat_data, min_opacity=0.5, blur=18)
    heat_map.add_to(mapa)
    return mapa


def generate_and_open_map(dataset):
    mapa = configure_heatmap(dataset)

    # Obtém o HTML do mapa gerado
    mapa_html = mapa.get_root().render()

    # Salva o HTML do mapa em um arquivo temporário
    with open("temp_map.html", "w", encoding="utf-8") as f:
        f.write(mapa_html)

    # Abre o arquivo HTML em uma nova janela do navegador
    webbrowser.open("file://" + os.path.abspath("temp_map.html"), new=2)


# Configurar a página Streamlit
st.set_page_config(
    page_title="Explore Airbnb information for Lisbon and Region",
    page_icon="🏠",
    layout="wide"
)

st.write("# Explore Airbnb information for Lisbon and Region")
st.divider()

# Carregar ou recuperar os dados do estado da sessão
if "data" not in st.session_state:
    dataset = load_and_process_data()
    st.session_state["data"] = dataset
else:
    dataset = st.session_state["data"]

# Configurar e exibir o mapa de calor no Streamlit
mapa = configure_heatmap(dataset)

st.markdown("Abaixo o mapa de calor que realça áreas onde há uma concentração maior de imóveis")
folium_static(mapa, height=400, width=850)

# Link para o GitHub
st.sidebar.markdown("[GitHub Repository](https://github.com/gbaere)")

# Gerar e abrir o mapa externamente - uso para debugar o mapa, quando o processamento fica pesado
# generate_and_open_map(dataset)
