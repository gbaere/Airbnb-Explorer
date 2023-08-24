import warnings
import streamlit as st
import folium
import pandas as pd
import plotly.express as px
from folium import plugins
from streamlit_folium import folium_static
from branca.colormap import LinearColormap

warnings.simplefilter(action='ignore', category=FutureWarning)

# metodo para gerar o mapa
def configure_circles(dataset):

    # Tiro a média das coordenadas da região para centrar o mapa
    lat_mean = dataset["latitude"].mean()
    long_mean = dataset["longitude"].mean()

    mapa = folium.Map(location=[lat_mean, long_mean], zoom_start=12)
    # Selecionar as colunas de latitude e longitude
    lat_lon_data = dataset[["latitude", "longitude", "price", "name"]]

    # Encontrar os valores mínimo e máximo de preço para normalização
    min_price = lat_lon_data["price"].min()
    max_price = lat_lon_data["price"].max()

    if max_price == min_price:
        # Se todos os preços forem iguais
        colormap = LinearColormap(colors=["black", "black"], vmin=min_price, vmax=max_price)
    else:
        colormap = LinearColormap(colors=["black", "green", "yellow", "red"], vmin=min_price, vmax=max_price)

    # aqui eu gero a barra horizontal no mapa da faixa de calor dos preços
    colormap = LinearColormap(
        colors=["black", "green", "yellow", "red"],
        vmin=min_price,
        vmax=max_price,
    )

    for index, row in lat_lon_data.iterrows():
        if max_price == min_price:
            color = "black"""
        else:
            # Calcula a proporção do preço em relação ao mínimo e máximo
            price_ratio = (row["price"] - min_price) / (max_price - min_price)
            # Calcula a cor com base na proporção
            color = f'hsl({120 - int(price_ratio * 120)}, 100%, 50%)'


        # aqui eu crio os marcardores em forma de circulo
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,  # Tamanho do círculo
            color=color,  # Cor do círculo com base no preço
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"${row['price']:.2f}",
            tooltip=row['name']
        ).add_to(mapa)

    # folium.TileLayer('openstreetmap').add_to(mapa)
    # folium.TileLayer('cartodb positron').add_to(mapa)
    # folium.TileLayer('stamenterrain').add_to(mapa)
    # folium.TileLayer('stamentoner').add_to(mapa)
    # folium.TileLayer('stamenwatercolor').add_to(mapa)
    # folium.TileLayer('cartodbdark_matter').add_to(mapa)
    # folium.LayerControl().add_to(mapa)

    colormap.caption = "Faixa de preços (Price gradient)"  # Legenda da barra vertical
    colormap.add_to(mapa)

    return mapa


st.set_page_config(
    page_title="Neighbourhood",
    page_icon="🏠",
    layout="wide"
)

if "data" in st.session_state:

    df_city = st.session_state["data"].groupby("neighbourhood_group_cleansed")
    df_result = st.session_state["data"]

    list_city = df_city["neighbourhood_group_cleansed"].value_counts().index
    city_selected = st.sidebar.selectbox("City", list_city)

    df_result = df_result[df_result["neighbourhood_group_cleansed"] == city_selected.strip()]

    df_result["neighbourhood_cleansed"].replace(city_selected.strip(), "")

    # Sidebar
    price_filter = st.sidebar.slider('Escolha o valor por noite: ',
                                     min_value=df_result["price"].min(),
                                     max_value=df_result["price"].max(),
                                     step=df_result["price"].mean())
    filtered_df = df_result[(df_result["price"] <= price_filter)]

    tab1, tab2 = st.tabs(["Resumo", "Dashboard"])
    with tab1:
        # Aplicando a substituição usando .str.replace() e atribuindo de volta à coluna
        df_result["neighbourhood_cleansed"] = df_result["neighbourhood_cleansed"].str.replace(city_selected.strip(), '', regex=True)
        col1, col2, col3 = st.columns(3)

        ## Exibir resumo da região
        col1.metric(label="Cidade (City):", value=f"{city_selected}")
        col2.metric(label="Preço Médio (Average Price):", value=f"${df_result['price'].median():,.0f}")
        col3.metric(label="Media de Avaliação (Rating Average of Location):", value=f"{df_result['review_scores_location'].mean():,.0f}")
    with tab2:
        # pegando as médas de valores
        mean_price_city = int(df_result["price"].mean())
        mean_price_all = int(st.session_state["data"]["price"].mean())
        # Criando um DataFrame com os valores
        data = pd.DataFrame({
            "Categoria": [city_selected, "Região"],
            "Média de Preço": [mean_price_city, mean_price_all]
        })
        # Criando o gráfico usando Plotly Express
        fig = px.bar(data, x="Média de Preço", y="Categoria", orientation="h",
                     labels={"Média de Preço": "Média de Preço", "Categoria": "Categorias"},
                     title=f"Médias de Preço da {city_selected} X Região")

        # Exibindo o gráfico usando Streamlit
        st.plotly_chart(fig)


    st.divider()

    # Configurar e exibir o mapa marcando cada imovel no mapa no mapa
    mapa = configure_circles(filtered_df)
    st.markdown("Abaixo o mapa da localização de cada imóvel")
    folium_static(mapa, height=300, width=1000)

    st.divider()

    # GRID de dados do filtro existentes no sidebar
    columns = ["name", "neighbourhood_cleansed", "picture_url", "host_name", "host_thumbnail_url", "host_url",
               "host_response_rate", "host_acceptance_rate", "price", "minimum_nights",
               "review_scores_rating"]

    st.dataframe(filtered_df[columns], column_config=
    {
        "id": st.column_config.TextColumn(label=""),
        "name": st.column_config.TextColumn(label="Name"),
        "neighbourhood_cleansed": st.column_config.TextColumn(label="Neighbourhood"),
        "picture_url": st.column_config.ImageColumn(label="Picture", width="small", help=None),
        "host_name": st.column_config.TextColumn(label="Host Name"),
        "host_thumbnail_url": st.column_config.ImageColumn(label="Host Photo", width="small", help=None),
        "host_url": st.column_config.LinkColumn(label="Host Link"),
        "host_response_rate": st.column_config.ProgressColumn("Host Response Rate", format="%d", min_value=0,
         max_value=int(df_result["host_response_rate"].astype(int).max())),
        "host_acceptance_rate": st.column_config.ProgressColumn("Host Acceptance Rate", format="%d", min_value=0,
         max_value=int(df_result["host_acceptance_rate"].astype(int).max())),
        "price": st.column_config.ProgressColumn(label="Price",  min_value=0, format="%.2f",
         max_value=int(df_result["price"].max())),
        "minimum_nights": st.column_config.NumberColumn(label="Minimum Nights"),
        "review_scores_rating": st.column_config.ProgressColumn("Review Scores Rating", format="%f", min_value=0,
         max_value=int(df_result["review_scores_rating"].max())),
        "latitude": st.column_config.Column(label="Lat"),
        "longitude": st.column_config.Column(label="Long")
    })

    m = folium.Map([38.55, -7.88], zoom_start=5, width="%100", height="%100")
    locations = list(zip(filtered_df.latitude, df_result.longitude))
    cluster = plugins.MarkerCluster(locations=locations,
                                    popups=filtered_df["neighbourhood"].tolist())
    m.add_child(cluster)
    folium_static(m, height=300, width=1000)



    #st.altair_chart(chart, use_container_width=True)