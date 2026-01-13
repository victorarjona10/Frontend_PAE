import streamlit as st
import pandas as pd
import altair as alt
from typing import Optional

def render_analytics(df: pd.DataFrame, history_df: pd.DataFrame, api_service=None):
    """
    Renders the analytics dashboard with various charts.
    Now integrates with backend API for real analytics data.

    Args:
        df: Current snapshot of all bags (for local simulation).
        history_df: Historical data of metrics over time (for local simulation).
        api_service: Optional RealTimeService instance for API mode.
    """

    st.header("📊 Operational Analytics")

    # If API service is available, use backend analytics
    if api_service:
        _render_api_analytics(api_service)
    else:
        _render_simulation_analytics(df, history_df)


def _render_api_analytics(api_service):
    """Render analytics using backend API data."""

    # Fetch analytics data
    dashboard_data = api_service.get_analytics_dashboard()
    loss_data = api_service.get_loss_analytics()
    top_airports = api_service.get_top_airports()
    hub_stats = api_service.get_hub_statistics()

    # === SECTION 1: STATUS DISTRIBUTION & BUSIEST AIRPORTS ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Distribución por Estado")
        if dashboard_data and "status_distribution" in dashboard_data:
            status_dist = dashboard_data["status_distribution"]
            status_df = pd.DataFrame(list(status_dist.items()), columns=['Status', 'Count'])

            pie_chart = alt.Chart(status_df).mark_arc(outerRadius=120, innerRadius=60).encode(
                theta=alt.Theta("Count", stack=True),
                color=alt.Color("Status", scale=alt.Scale(scheme='category20')),
                tooltip=["Status", "Count"]
            )
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No hay datos de distribución disponibles")

    with col2:
        st.subheader("✈️ Aeropuertos Más Concurridos")
        if dashboard_data and "busiest_airports" in dashboard_data:
            busiest = pd.DataFrame(dashboard_data["busiest_airports"][:10])
            if not busiest.empty:
                # Determinar qué campos están disponibles para tooltip
                tooltip_fields = ['code', 'count']
                if 'name' in busiest.columns:
                    tooltip_fields.insert(1, 'name')

                bar_chart = alt.Chart(busiest).mark_bar().encode(
                    x=alt.X('count:Q', title='Número de Maletas'),
                    y=alt.Y('code:N', sort='-x', title='Aeropuerto'),
                    color=alt.Color('count:Q', scale=alt.Scale(scheme='blues')),
                    tooltip=tooltip_fields
                )
                st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("No hay datos de aeropuertos disponibles")

    # === SECTION 2: SESSION TRENDS ===
    st.divider()
    st.subheader("📈 Tendencias de Operación (Última Hora)")

    if dashboard_data and "session_trends" in dashboard_data:
        trends = pd.DataFrame(dashboard_data["session_trends"])
        if not trends.empty:
            # Melt for multi-line chart
            trends_melted = trends.melt('timestamp', var_name='Métrica', value_name='Cantidad')

            line_chart = alt.Chart(trends_melted).mark_line(point=True).encode(
                x=alt.X('timestamp:T', title='Tiempo'),
                y=alt.Y('Cantidad:Q', title='Cantidad'),
                color='Métrica:N',
                tooltip=['timestamp:T', 'Métrica:N', 'Cantidad:Q']
            ).interactive()

            st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("No hay datos de tendencias disponibles")

    # === SECTION 3: LOSS ANALYTICS ===
    st.divider()
    st.subheader("🔴 Análisis de Pérdidas")

    if loss_data:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Perdidas",
                loss_data.get("total_losses", 0),
                help="Número total de maletas perdidas"
            )

        with col2:
            recovered = loss_data.get("loss_status", {}).get("RECOVERED", 0)
            st.metric(
                "Recuperadas",
                recovered,
                help="Maletas recuperadas exitosamente"
            )

        with col3:
            in_search = loss_data.get("loss_status", {}).get("IN_SEARCH", 0)
            st.metric(
                "En Búsqueda",
                in_search,
                delta=f"-{in_search}",
                delta_color="inverse",
                help="Maletas aún siendo buscadas"
            )

        with col4:
            avg_recovery = loss_data.get("avg_recovery_time_hours", 0)
            st.metric(
                "Tiempo Medio Recuperación",
                f"{avg_recovery:.1f}h",
                help="Tiempo promedio para recuperar maletas"
            )

        # Loss reasons breakdown
        if "loss_reasons" in loss_data:
            st.subheader("🔍 Razones de Pérdida")
            loss_reasons = pd.DataFrame(
                list(loss_data["loss_reasons"].items()),
                columns=['Razón', 'Cantidad']
            )

            reasons_chart = alt.Chart(loss_reasons).mark_bar(color='#ff6b6b').encode(
                x=alt.X('Cantidad:Q', title='Número de Casos'),
                y=alt.Y('Razón:N', sort='-x', title='Motivo'),
                tooltip=['Razón', 'Cantidad']
            )
            st.altair_chart(reasons_chart, use_container_width=True)

    # === SECTION 4: TOP AIRPORTS WITH LOSSES ===
    st.divider()
    st.subheader("🌍 Aeropuertos con Más Pérdidas")

    if top_airports:
        top_df = pd.DataFrame(top_airports[:10])

        col1, col2 = st.columns([2, 1])

        with col1:
            loss_chart = alt.Chart(top_df).mark_bar(color='#e74c3c').encode(
                x=alt.X('loss_count:Q', title='Maletas Perdidas'),
                y=alt.Y('airport_code:N', sort='-x', title='Aeropuerto'),
                tooltip=['airport_code', 'loss_count']
            )
            st.altair_chart(loss_chart, use_container_width=True)

        with col2:
            st.dataframe(
                top_df,
                column_config={
                    "airport_code": "Código",
                    "loss_count": st.column_config.NumberColumn(
                        "Pérdidas",
                        format="%d 🧳"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

    # === SECTION 5: HUB STATISTICS ===
    st.divider()
    st.subheader("🏢 Estadísticas de Hubs")

    if hub_stats and "data" in hub_stats:
        hub_df = pd.DataFrame(hub_stats["data"])

        if not hub_df.empty:
            st.caption(f"Total de Hubs Monitoreados: **{hub_stats.get('total_hubs', 0)}**")

            # Display table with formatting
            st.dataframe(
                hub_df,
                column_config={
                    "airport_code": "Aeropuerto",
                    "total_bags": st.column_config.NumberColumn("Total Maletas", format="%d"),
                    "avg_processing_time": st.column_config.NumberColumn("Tiempo Procesamiento (min)", format="%.1f"),
                    "efficiency_score": st.column_config.ProgressColumn("Eficiencia", format="%.2f", min_value=0, max_value=1)
                },
                hide_index=True,
                use_container_width=True
            )


def _render_simulation_analytics(df: pd.DataFrame, history_df: pd.DataFrame):
    """Render analytics using local simulation data (fallback)."""

    st.info("📡 Mostrando datos de simulación local. Conecta al backend para analytics en tiempo real.")

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
