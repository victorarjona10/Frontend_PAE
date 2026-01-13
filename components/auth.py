import streamlit as st
from typing import Optional

def render_login(api_service=None):
    """
    Renders the login screen with real API authentication.

    Args:
        api_service: Optional RealTimeService instance for API authentication.
    """

    st.markdown("""
    <style>
        .login-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #1f2937;
            border-radius: 12px;
            border: 1px solid #374151;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🧳 OmniTrack Identity")

    # Check if API mode or Simulation mode
    use_api = api_service is not None

    if use_api:
        st.info("🔐 **Modo API Activado** - Autenticación con Backend")
        _render_api_login(api_service)
    else:
        st.warning("🎮 **Modo Simulación** - Login simplificado")
        _render_simulation_login()


def _render_api_login(api_service):
    """Render login form with real API authentication."""

    with st.form("login_form"):
        st.subheader("Iniciar Sesión")

        username = st.text_input(
            "Usuario",
            placeholder="admin, passenger_1, passenger_2...",
            help="Usuarios de prueba: admin, passenger_1, passenger_2"
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="password",
            help="Contraseña para todos: 'password'"
        )

        submit = st.form_submit_button("🔓 Iniciar Sesión", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("❌ Por favor completa todos los campos")
            else:
                with st.spinner("Autenticando..."):
                    result = api_service.login(username, password)

                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        # Successful login
                        role = result.get("role")
                        target_bag_id = result.get("target_bag_id")
                        user_id = result.get("user_id")

                        # Map API roles to session state
                        if role == "ADMIN":
                            st.session_state.user_role = 'admin'
                            st.session_state.user_id = user_id
                            st.success(f"✅ Bienvenido, {user_id}!")
                        elif role == "PASSENGER":
                            st.session_state.user_role = 'passenger'
                            st.session_state.user_id = user_id
                            # Fetch passenger's specific bag and get the actual ID
                            actual_bag_id = api_service.fetch_bags_for_passenger(target_bag_id)
                            if actual_bag_id:
                                st.session_state.target_bag_id = actual_bag_id
                                st.success(f"✅ Bienvenido! Rastreando maleta: {actual_bag_id}")
                            else:
                                st.session_state.target_bag_id = None
                                st.warning(f"⚠️ No se pudo cargar la maleta {target_bag_id}")

                        st.rerun()

    # Show available test accounts
    with st.expander("👥 Cuentas de Prueba"):
        st.markdown("""
        **Administrador:**
        - Usuario: `admin`
        - Contraseña: `password`
        - Acceso: Todas las maletas

        **Pasajeros:**
        - Usuario: `passenger_1` | Contraseña: `password` | Maleta: `BAG1000000001`
        - Usuario: `passenger_2` | Contraseña: `password` | Maleta: `BAG1000000050`
        """)


def _render_simulation_login():
    """Render simplified login for simulation mode."""

    c1, c2 = st.columns(2)

    with c1:
        st.info("👤 **Passenger**")
        st.write("Track your personal luggage.")
        bag_id = st.text_input("Enter your Bag ID", value="BAG-1001", placeholder="e.g. BAG-1001")
        if st.button("Track My Bag"):
            st.session_state.user_role = 'passenger'
            st.session_state.target_bag_id = bag_id
            st.rerun()

    with c2:
        st.info("👮 **Operations**")
        st.write("Airport & Airline Staff Access.")
        password = st.text_input("Access Code", type="password", placeholder="(Any code works)")
        if st.button("Enter Ops Center"):
            st.session_state.user_role = 'admin'
            st.rerun()

    st.write("---")
    st.caption("Simulation Mode: No real authentication required.")
