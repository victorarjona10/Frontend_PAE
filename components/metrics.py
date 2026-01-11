import streamlit as st
import pandas as pd

def render_metrics(df: pd.DataFrame):
    """Displays key performance indicators."""
    
    total = len(df)
    lost = len(df[df['status'] == 'Lost'])
    flying = len(df[df['status'] == 'In Transit'])
    landed = len(df[df['status'] == 'Baggage Claim']) + len(df[df['status'] == 'Landed'])

    st.markdown("""
    <style>
        .metric-container {
            background-color: #1f2937;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #374151;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .metric-label {
            font-size: 0.8rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f3f4f6;
            margin-top: 5px;
        }
        .metric-alert {
            color: #ef4444; /* Red for alerts */
        }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Bags</div>
            <div class="metric-value">{total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">On-Board</div>
            <div class="metric-value" style="color: #60a5fa;">{flying}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">On Ground</div>
            <div class="metric-value" style="color: #34d399;">{landed}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-container" style="border-color: #7f1d1d;">
            <div class="metric-label">Lost/Alerts</div>
            <div class="metric-value metric-alert">{lost}</div>
        </div>
        """, unsafe_allow_html=True)
