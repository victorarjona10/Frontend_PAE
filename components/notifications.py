import streamlit as st
from services.models import BagStatus

def check_notifications(current_bags):
    """
    Checks for status changes and generates notifications.
    This should be called after a simulation tick.
    """
    if 'previous_states' not in st.session_state:
        st.session_state.previous_states = {}
    
    if 'notification_log' not in st.session_state:
        st.session_state.notification_log = []

    for bag in current_bags:
        prev_status = st.session_state.previous_states.get(bag.id)
        
        # Detect Change
        if prev_status and prev_status != bag.status:
            # Generate Notification
            msg = None
            icon = None
            type_ = "info"
            
            if bag.status == BagStatus.LOST:
                msg = f"⚠️ CRITICAL: {bag.id} reported LOST at {bag.origin.name}!"
                icon = "🚨"
                type_ = "error"
            elif bag.status == BagStatus.LANDED:
                msg = f"🛬 {bag.id} has landed at {bag.destination.name}."
                icon = "✅"
            elif bag.status == BagStatus.WRONG_DESTINATION: # Future proofing
                msg = f"❌ ALARM: {bag.id} arrived at WRONG destination!"
                icon = "🛑"
                type_ = "error"
                
            if msg:
                # Toast for immediate visual
                st.toast(msg, icon=icon)
                
                # Log for history
                st.session_state.notification_log.insert(0, {
                    "time": pd.Timestamp.now().strftime("%H:%M:%S"),
                    "message": msg,
                    "type": type_
                })
        
        # Update State
        st.session_state.previous_states[bag.id] = bag.status

import pandas as pd

def render_notification_center():
    """Renders the notification history."""
    st.subheader("🔔 Alerts Center")
    
    if 'notification_log' not in st.session_state or not st.session_state.notification_log:
        st.caption("No alerts yet.")
        return

    for note in st.session_state.notification_log[:10]: # Show last 10
        if note['type'] == 'error':
            st.error(f"[{note['time']}] {note['message']}")
        else:
            st.info(f"[{note['time']}] {note['message']}")
