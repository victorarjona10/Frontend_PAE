import streamlit as st
import pydeck as pdk
import pandas as pd

def render_map(df: pd.DataFrame, show_heatmap: bool = False):
    """Renders the main map visualization using Pydeck."""
    
    # 1. View State
    view_state = pdk.ViewState(
        latitude=20.0,
        longitude=0.0,
        zoom=1.5,
        pitch=20,
    )

    # 2. Layers
    layers = []
    
    # Heatmap Layer (Optional)
    if show_heatmap:
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=["lon", "lat"],
            opacity=0.4,
            get_weight=1,
            radius_pixels=50,
        )
        layers.append(heatmap_layer)

    # Bag Scatter Layer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="size_scale", 
        radius_scale=500, # Base scale
        radius_min_pixels=3,
        radius_max_pixels=15,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        line_width_min_pixels=1,
    )
    layers.append(scatter_layer)
    
    # Flight Arcs (Only for IN_TRANSIT)
    in_transit = df[df['status'] == 'In Transit']
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=in_transit,
        get_source_position=["lon", "lat"],
        get_target_position=["dest_lon", "dest_lat"],
        get_source_color=[0, 191, 255, 150],
        get_target_color=[255, 255, 255, 100],
        get_width=2,
        pickable=True,
    )
    layers.append(arc_layer)

    # 3. Tooltip
    tooltip = {
        "html": "<b>{id}</b><br/>"
                "{status}<br/>"
                "<i>{origin} ➝ {destination}</i>",
        "style": {
            "backgroundColor": "#111827",
            "color": "white",
            "fontSize": "12px",
            "borderRadius": "5px"
        }
    }

    # 4. Deck
    # Using Carto Dark to ensure no API key key needed and avoid black map issues
    r = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=view_state,
        layers=layers,
        tooltip=tooltip
    )

    st.pydeck_chart(r, use_container_width=True)
