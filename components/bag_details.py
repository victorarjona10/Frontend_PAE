import streamlit as st
from services.simulation import SimulationEngine, Bag
from services.models import BagStatus

def render_bag_details(bag: Bag):
    """Renders a detailed view for a single bag."""
    
    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader(f"🧳 {bag.id}")
        st.caption(f"Owner: {bag.owner}")
        
        status_color = "white"
        if bag.status == BagStatus.LOST: status_color = "red"
        if bag.status == BagStatus.IN_TRANSIT: status_color = "#3b82f6"
        if bag.status == BagStatus.CLAIMED: status_color = "green"
        
        st.markdown(f"**Status**: <span style='color:{status_color}; font-weight:bold'>{bag.status.value}</span>", unsafe_allow_html=True)
        st.write(f"**Origin**: {bag.origin.code} ({bag.origin.name})")
        st.write(f"**Destination**: {bag.destination.code} ({bag.destination.name})")
    
    with c2:
        st.subheader("Tracking History")
        
        history_md = ""
        for time, event in reversed(bag.history):
            history_md += f"""
            <div style="display:flex; margin-bottom: 10px; align-items: center;">
                <div style="min-width: 80px; font-size:0.8rem; color:#9ca3af;">{time.strftime('%H:%M:%S')}</div>
                <div style="flex-grow:1; padding-left:10px; border-left: 2px solid #4b5563;">{event}</div>
            </div>
            """
        
        st.markdown(history_md, unsafe_allow_html=True)
