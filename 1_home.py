import os
import webbrowser
import folium
import pandas as pd
import streamlit as st
import plotly.express as px
from folium import plugins
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
    mapa = folium.Map(location=["39.55", "-7.85"], zoom_start=8)

    # Selecionar as colunas de latitude e longitude
    lat_lon_data = dataset[["latitude", "longitude"]]

    # Agrupar e contar os dados
    heat_data = lat_lon_data.groupby(["latitude", "longitude"]).size().reset_index(name="count")
    heat_data = heat_data.values.tolist()

    heat_map = HeatMap(heat_data, min_opacity=0.5, blur=16)
    heat_map.add_to(mapa)
    return mapa


def configure_price_heatmap(dataset):
    fig = px.scatter_mapbox(dataset,
                            lat='latitude',
                            lon='longitude',
                            color='price',
                            size='price',
                            color_continuous_scale='Viridis',  # Esquema de cores
                            size_max=25,  # Tamanho máximo dos pontos
                            mapbox_style='open-street-map',  # Estilo do mapa
                            title='Mapa de Calor de Imóveis por Preço',
                            hover_data=['latitude', 'longitude', 'price', 'name'],  # Dados para exibir no hover
                            labels={'price': 'Preço'})

    # Personalizar o texto que aparece no hover
    fig.update_traces(
        hovertemplate='Nome: %{customdata[3]}<br>Preço: R$%{customdata[2]:,.2f}<br>Latitude: %{customdata[0]:.4f}<br>Longitude: %{customdata[1]:.4f}')

    return fig

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

    #chama a função para exibir o mapa de preços
    price_heatmap = configure_price_heatmap(dataset)
    price_heatmap.update_layout(height=500, width=850)
    st.plotly_chart(price_heatmap, use_container_width=True, theme=None)

    # mapa de concentração
    st.markdown('Mapa da concentração maior de imóveis')
    mapa_concentracao = folium.Map([38.55, -7.88], zoom_start=5, width="%100", height="%100")
    locations = list(zip(dataset.latitude, dataset.longitude))
    cluster = plugins.MarkerCluster(locations=locations,
                                    popups=dataset["name"].tolist())
    mapa_concentracao.add_child(cluster)
    folium_static(mapa_concentracao, height=300, width=1000)

    # Link para o GitHub
    st.sidebar.markdown("[GitHub Repository](https://github.com/gbaere)")

    # Gerar e abrir o mapa externamente - uso para debugar o mapa, quando o processamento fica pesado
    # generate_and_open_map(dataset)
