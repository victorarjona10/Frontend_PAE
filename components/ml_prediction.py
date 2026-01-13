import streamlit as st
from typing import Dict, Any

def render_ml_prediction(api_service):
    """
    Renders the Machine Learning Prediction form for bag loss risk.

    Args:
        api_service: Instance of RealTimeService with API methods.
    """

    st.header("🤖 Predicción de Riesgo de Pérdida (ML)")
    st.caption("Utiliza nuestro modelo de Machine Learning para predecir el riesgo de pérdida de equipaje")

    with st.form("ml_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📍 Ruta de Vuelo")

            # Get airports from API
            airports = api_service.get_airports()
            airport_codes = [a.code for a in airports] if airports else ["JFK", "LHR", "MAD", "CDG"]

            origen = st.selectbox(
                "Aeropuerto de Origen",
                options=airport_codes,
                help="Código IATA del aeropuerto de origen"
            )

            destino = st.selectbox(
                "Aeropuerto de Destino",
                options=airport_codes,
                index=1 if len(airport_codes) > 1 else 0,
                help="Código IATA del aeropuerto de destino"
            )

            aerolinea = st.text_input(
                "Código de Aerolínea",
                value="AA",
                max_chars=3,
                help="Código de 2-3 letras (ej: AA, BA, IB)"
            )

            time_of_day = st.selectbox(
                "Hora del Día",
                options=["morning", "afternoon", "evening", "night"],
                format_func=lambda x: {
                    "morning": "🌅 Mañana (6:00-12:00)",
                    "afternoon": "☀️ Tarde (12:00-18:00)",
                    "evening": "🌆 Noche (18:00-22:00)",
                    "night": "🌙 Madrugada (22:00-6:00)"
                }[x]
            )

        with col2:
            st.subheader("📊 Factores de Riesgo")

            retraso_min = st.slider(
                "Retraso del Vuelo (minutos)",
                min_value=0,
                max_value=999,
                value=0,
                help="Minutos de retraso esperado"
            )

            transfers = st.select_slider(
                "Número de Conexiones",
                options=[0, 1, 2],
                value=0,
                help="Vuelos de conexión"
            )

            airport_risk = st.select_slider(
                "Nivel de Riesgo del Aeropuerto",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: f"{'⭐' * x} ({x}/5)",
                help="1 = Bajo riesgo, 5 = Alto riesgo"
            )

            viajero_vip = st.checkbox(
                "✨ Viajero VIP",
                value=False,
                help="Los pasajeros VIP tienen prioridad"
            )

            peso_kg = st.number_input(
                "Peso del Equipaje (kg)",
                min_value=1.0,
                max_value=50.0,
                value=23.0,
                step=0.5,
                help="Peso de la maleta en kilogramos"
            )

        # Submit button
        submitted = st.form_submit_button("🔮 Predecir Riesgo", use_container_width=True)

        if submitted:
            with st.spinner("Calculando riesgo con IA..."):
                # Prepare prediction data
                prediction_data = {
                    "origen": origen,
                    "destino": destino,
                    "aerolinea": aerolinea,
                    "time_of_day": time_of_day,
                    "retraso_min": retraso_min,
                    "transfers": transfers,
                    "airport_risk": airport_risk,
                    "viajero_vip": 1 if viajero_vip else 0,
                    "peso_kg": peso_kg
                }

                # Call ML API
                result = api_service.predict_risk(prediction_data)

                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Display results
                    _display_prediction_results(result, prediction_data)


def _display_prediction_results(result: Dict[str, Any], input_data: Dict[str, Any]):
    """Display the ML prediction results in a nice format."""

    st.divider()
    st.subheader("📈 Resultados de la Predicción")

    # Extract results
    probabilidad = result.get("probabilidad_perdida", 0.0)
    prediccion = result.get("prediccion", 0)
    risk_level = result.get("risk_level", "UNKNOWN")
    factors = result.get("factors", [])

    # Risk level styling
    risk_config = {
        "LOW": {
            "color": "green",
            "icon": "🟢",
            "label": "Riesgo Bajo",
            "description": "Tu equipaje tiene muy pocas probabilidades de perderse"
        },
        "MEDIUM": {
            "color": "yellow",
            "icon": "🟡",
            "label": "Riesgo Moderado",
            "description": "Existe un riesgo moderado de pérdida, mantente atento"
        },
        "HIGH": {
            "color": "orange",
            "icon": "🟠",
            "label": "Riesgo Alto",
            "description": "Alto riesgo de pérdida, considera medidas preventivas"
        },
        "CRITICAL": {
            "color": "red",
            "icon": "🔴",
            "label": "Riesgo Crítico",
            "description": "Riesgo muy alto, se recomienda llevar equipaje de mano"
        }
    }

    config = risk_config.get(risk_level, risk_config["LOW"])

    # Main metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Nivel de Riesgo",
            value=f"{config['icon']} {config['label']}"
        )

    with col2:
        st.metric(
            label="Probabilidad de Pérdida",
            value=f"{probabilidad * 100:.2f}%"
        )

    with col3:
        prediction_text = "❌ Se perderá" if prediccion == 1 else "✅ No se perderá"
        st.metric(
            label="Predicción",
            value=prediction_text
        )

    # Description
    st.info(f"**{config['description']}**")

    # Risk factors
    if factors:
        st.subheader("⚠️ Factores de Riesgo Detectados")
        for factor in factors:
            st.warning(f"• {factor}")

    # Recommendations based on risk level
    st.subheader("💡 Recomendaciones")

    if risk_level == "LOW":
        st.success("""
        - ✅ Tu equipaje está en buenas manos
        - 📱 Puedes hacer seguimiento en tiempo real
        - 🏷️ Asegúrate de que las etiquetas estén bien colocadas
        """)
    elif risk_level == "MEDIUM":
        st.warning("""
        - ⏰ Llega al aeropuerto con tiempo suficiente
        - 📸 Toma fotos de tu equipaje antes de facturarlo
        - 🏷️ Coloca etiquetas con tus datos de contacto
        - 📱 Activa las notificaciones de seguimiento
        """)
    elif risk_level == "HIGH":
        st.warning("""
        - 🎒 Considera llevar objetos valiosos en equipaje de mano
        - 📸 Documenta el contenido de tu maleta
        - 🏷️ Usa múltiples etiquetas de identificación
        - 💼 Contrata un seguro de equipaje
        - 📱 Mantén el seguimiento activo constantemente
        """)
    else:  # CRITICAL
        st.error("""
        - 🚨 Riesgo muy elevado de pérdida
        - 🎒 **Recomendación fuerte**: Lleva solo equipaje de mano
        - 💼 Si debes facturar, contrata seguro premium
        - 📦 Envía objetos valiosos por separado
        - 🏷️ Usa rastreadores GPS en tu maleta
        - 📱 Configura alertas inmediatas
        """)

    # Trip summary
    with st.expander("📋 Resumen del Viaje"):
        st.write(f"**Ruta**: {input_data['origen']} → {input_data['destino']}")
        st.write(f"**Aerolínea**: {input_data['aerolinea']}")
        st.write(f"**Hora**: {input_data['time_of_day']}")
        st.write(f"**Conexiones**: {input_data['transfers']}")
        st.write(f"**Retraso esperado**: {input_data['retraso_min']} min")
        st.write(f"**Riesgo aeropuerto**: {'⭐' * input_data['airport_risk']}")
        st.write(f"**VIP**: {'Sí' if input_data['viajero_vip'] else 'No'}")
        st.write(f"**Peso**: {input_data['peso_kg']} kg")
