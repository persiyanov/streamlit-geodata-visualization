import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(layout='wide')

PROCESSED_DATA_PATH = 'data/data_small_processed.csv'


class AggregationType:
    COUNT = 'count'
    SALE_PRICE = 'sale_price'

    @staticmethod
    def to_human_readable(option: str) -> str:
        if option == AggregationType.COUNT:
            return 'Count'
        elif option == AggregationType.SALE_PRICE:
            return 'Sale Price'
        else:
            raise NotImplementedError(f'Option "{option}" not supported.')


@st.cache
def read_processed_data(path):
    return pd.read_csv(path)


st.title('NYC Housing Data Visualization')

st.markdown(
    '**Source Code**: [https://github.com/persiyanov/streamlit-geodata-visualization](https://github.com/persiyanov/streamlit-geodata-visualization)'
)

st.subheader('Controls')
radius = st.slider('Hexagon Radius, meters', 100, 500, value=200, step=10, format='%dm')
remove_top_percentile = st.slider('Remove Top %', 0, 10, value=1)

aggregation_type = st.selectbox(
    'Aggregate By',
    [AggregationType.COUNT, AggregationType.SALE_PRICE],
    format_func=AggregationType.to_human_readable,
)

data = read_processed_data(PROCESSED_DATA_PATH)

location_found_cnt = data['lat'].notna().sum()
st.success(
    f'Succesfully retrieved geo-coordinates for {location_found_cnt} out of {len(data)} objects ({location_found_cnt / len(data) * 100:.2f}%)'
)

data = data[data['lat'].notna() & data['lon'].notna()]


agg_value = '1' if aggregation_type == AggregationType.COUNT else 'SALE_PRICE'
aggregation = 'SUM' if aggregation_type == AggregationType.COUNT else 'MEAN'
tooltip_title = 'Count' if aggregation_type == AggregationType.COUNT else 'Sale Price'

layer = pdk.Layer(
    'HexagonLayer',
    data[['lat', 'lon', 'SALE_PRICE']],
    get_position=['lon', 'lat'],
    auto_highlight=True,
    elevation_scale=100,
    pickable=True,
    elevation_range=[0, 100],
    extruded=True,
    coverage=1,
    radius=radius,
    get_color_weight=agg_value,
    get_elevation_weight=agg_value,
    color_aggregation=pdk.types.String(aggregation),
    elevation_aggregation=pdk.types.String(aggregation),
    upper_percentile=100 - remove_top_percentile,
)

# Set the viewport location
view_state = pdk.ViewState(
    longitude=data['lon'].median(),
    latitude=data['lat'].median(),
    zoom=10,
    min_zoom=5,
    max_zoom=18,
    pitch=40,
    bearing=-15.36,
)
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='light',
    tooltip={
        'html': f'<b>{tooltip_title}:</b> ' + '{elevationValue}',
        'style': {'backgroundColor': 'steelblue', 'color': 'white'},
    },
)


st.subheader('Map')
st.pydeck_chart(r, use_container_width=True)
st.subheader('Data')
st.write(data)
