import streamlit as st

def render_login():
    """Renders the login/role selection screen."""
    
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
