import streamlit as st
import pandas as pd
import altair as alt

def render_analytics(df: pd.DataFrame, history_df: pd.DataFrame):
    """
    Renders the analytics dashboard with various charts.
    
    Args:
        df: Current snapshot of all bags.
        history_df: Historical data of metrics over time.
    """
    
    st.header("📊 Operational Analytics")

    # 1. Top Level Distribution
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Bag Status Distribution")
        
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        # Donut Chart for Status
        base = alt.Chart(status_counts).encode(
            theta=alt.Theta("count", stack=True)
        )
        pie = base.mark_arc(outerRadius=120, innerRadius=60).encode(
            color=alt.Color("status"),
            order=alt.Order("count", sort="descending"),
            tooltip=["status", "count"]
        )
        text = base.mark_text(radius=140).encode(
            text=alt.Text("count"),
            order=alt.Order("count", sort="descending"),
            color=alt.value("white")
        )
        st.altair_chart(pie + text, use_container_width=True)

    with c2:
        st.subheader("Busiest Airports (Origin)")
        origin_counts = df['origin'].value_counts().reset_index().head(5)
        origin_counts.columns = ['airport', 'count']
        
        bar_chart = alt.Chart(origin_counts).mark_bar().encode(
            x=alt.X('count', title='Number of Bags'),
            y=alt.Y('airport', sort='-x', title='Airport'),
            color=alt.Color('count', scale=alt.Scale(scheme='blues')),
            tooltip=['airport', 'count']
        )
        st.altair_chart(bar_chart, use_container_width=True)

    # 2. Trends Over Time (Session)
    st.subheader("Live Operations Trend (Current Session)")
    
    if not history_df.empty:
        # Transform wide to long for multi-line chart
        history_melted = history_df.melt('timestamp', var_name='Metric', value_name='Count')
        
        line_chart = alt.Chart(history_melted).mark_line().encode(
            x=alt.X('timestamp', title='Time (Ticks)'),
            y=alt.Y('Count', title='Count'),
            color='Metric',
            tooltip=['timestamp', 'Metric', 'Count']
        ).interactive()
        
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("Waiting for data collection... Start the simulation to see trends.")
