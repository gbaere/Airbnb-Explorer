import warnings
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import streamlit as st
import fiona


#portugal = gpd.read_file('datasets/portugal.shp')
#portugal.plot()

warnings.simplefilter(action='ignore', category=FutureWarning)

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


    # Aplicando a substituição usando .str.replace() e atribuindo de volta à coluna
    df_result["neighbourhood_cleansed"] = df_result["neighbourhood_cleansed"].str.replace(city_selected.strip(), '', regex=True)
    col1, col2, col3 = st.columns(3)

    ## Exibir resumo
    col1.metric(label="City:", value=f"{city_selected}")
    col2.metric(label="Average Price:", value=f"${df_result['price'].median():,.0f}")
    col3.metric(label="Rating Average of Location:", value=f"{df_result['review_scores_location'].mean():,.0f}")


    columns = ["name", "neighbourhood_cleansed", "picture_url", "host_name", "host_thumbnail_url", "host_url",
               "host_response_rate", "host_acceptance_rate", "price", "minimum_nights",
               "review_scores_rating"]

    st.dataframe(df_result[columns], column_config=
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
    })

