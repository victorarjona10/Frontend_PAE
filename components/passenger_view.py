import streamlit as st
from services.models import Bag, BagStatus
from datetime import datetime, timedelta
from typing import Optional

def render_passenger_bag_details(bag: Bag, api_service=None):
    """
    Enhanced bag details view for passengers with flight info and report options.
    """
    st.markdown("---")

    # Header with bag ID and status
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"🧳 {bag.id}")
        st.caption(f"Passenger: {bag.owner}")

    with col2:
        # Status badge
        status_color = {
            BagStatus.CHECK_IN: "#3b82f6",
            BagStatus.SECURITY: "#8b5cf6",
            BagStatus.AT_GATE: "#06b6d4",
            BagStatus.IN_TRANSIT: "#10b981",
            BagStatus.LANDED: "#f59e0b",
            BagStatus.BAGGAGE_CLAIM: "#8b5cf6",
            BagStatus.CLAIMED: "#22c55e",
            BagStatus.LOST: "#ef4444",
        }.get(bag.status, "#6b7280")

        st.markdown(f"""
        <div style="background: {status_color}; padding: 10px; border-radius: 8px; text-align: center;">
            <h3 style="margin:0; color:white;">{bag.status.value}</h3>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Flight Information
    st.subheader("✈️ Flight Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Origin", f"{bag.origin.code}")
        st.caption(bag.origin.name)

    with col2:
        st.metric("→ Destination", f"{bag.destination.code}")
        st.caption(bag.destination.name)

    with col3:
        # Estimated arrival (mock calculation based on progress)
        if bag.status in [BagStatus.IN_TRANSIT, BagStatus.CHECK_IN]:
            hours_remaining = int((1 - bag.progress) * 8)  # Assume 8h max flight
            eta = datetime.now() + timedelta(hours=hours_remaining)
            st.metric("ETA", eta.strftime("%H:%M"))
            st.caption(eta.strftime("%d %b"))
        elif bag.status == BagStatus.LANDED:
            st.metric("Status", "Arrived")
            st.caption("Check baggage claim")
        else:
            st.metric("Progress", f"{int(bag.progress * 100)}%")
            st.caption("Complete")

    # Current Location
    st.subheader("📍 Current Location")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Coordinates**: {bag.current_lat:.4f}, {bag.current_lon:.4f}")

    with col2:
        # Show expected vs current location
        if bag.status == BagStatus.BAGGAGE_CLAIM:
            st.success(f"✅ At **{bag.destination.code}** Baggage Claim")
        elif bag.status == BagStatus.IN_TRANSIT:
            st.info(f"🛫 En route to **{bag.destination.code}**")
        elif bag.status == BagStatus.CHECK_IN:
            st.warning(f"⏳ Awaiting departure from **{bag.origin.code}**")
        else:
            st.error(f"⚠️ Status: {bag.status.value}")

    st.divider()

    # Tracking History
    st.subheader("📜 Tracking History")

    if bag.history:
        for time, event in reversed(bag.history[-5:]):  # Show last 5 events
            st.markdown(f"""
            <div style="display:flex; margin-bottom: 12px; align-items: flex-start; padding: 8px; background: #1f2937; border-radius: 6px;">
                <div style="min-width: 90px; font-size:0.85rem; color:#9ca3af; font-weight: 600;">
                    {time.strftime('%H:%M:%S')}
                </div>
                <div style="flex-grow:1; padding-left:12px; border-left: 3px solid #3b82f6; color: #e5e7eb;">
                    {event}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No tracking history available yet.")

    st.divider()

    # Report Problem Section
    st.subheader("🚨 Report an Issue")

    with st.expander("📝 My bag is not where it should be", expanded=False):
        render_report_form(bag, api_service)


def render_report_form(bag: Bag, api_service):
    """
    Form for passengers to report bag issues with ML prediction.
    """
    st.markdown("If your bag is missing or delayed, please provide the details below:")

    with st.form("report_issue_form"):
        # Report type
        report_type = st.selectbox(
            "Type of Issue",
            ["Lost - Cannot find my bag",
             "Delayed - Not arrived yet",
             "Misplaced - Wrong location",
             "Damaged - Physical damage"]
        )

        # Location information
        col1, col2 = st.columns(2)

        with col1:
            current_location = st.text_input(
                "Where is your bag currently?",
                placeholder="e.g., Terminal 3, Gate B12, Unknown",
                help="Based on last scan or 'Unknown' if not visible"
            )

        with col2:
            expected_location = st.text_input(
                "Where should it be?",
                placeholder="e.g., Baggage Claim Area 2",
                value=f"{bag.destination.code} Baggage Claim" if bag.status == BagStatus.LANDED else ""
            )

        # Additional details
        description = st.text_area(
            "Additional Details",
            placeholder="Describe what happened... (optional)",
            max_chars=500
        )

        # Submit button
        submitted = st.form_submit_button("🔴 Submit Report", use_container_width=True)

        if submitted:
            if not current_location or not expected_location:
                st.error("❌ Please fill in all location fields")
            else:
                # Process the report
                handle_report_submission(
                    bag=bag,
                    report_type=report_type,
                    current_location=current_location,
                    expected_location=expected_location,
                    description=description,
                    api_service=api_service
                )


def handle_report_submission(bag, report_type, current_location, expected_location, description, api_service):
    """
    Handle the submission of a bag issue report with ML prediction.
    """
    # Map report type to backend enum
    type_map = {
        "Lost - Cannot find my bag": "LOST",
        "Delayed - Not arrived yet": "DELAYED",
        "Misplaced - Wrong location": "MISPLACED",
        "Damaged - Physical damage": "DAMAGED"
    }

    report_data = {
        "report_type": type_map.get(report_type, "LOST"),
        "current_location": current_location,
        "expected_location": expected_location,
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "passenger_location_lat": bag.current_lat,
        "passenger_location_lon": bag.current_lon
    }

    # Try to submit to backend if API service is available
    if api_service and hasattr(api_service, 'report_bag_issue'):
        with st.spinner("📡 Submitting report and analyzing..."):
            result = api_service.report_bag_issue(bag.id, report_data)

            if "error" in result:
                st.error(f"❌ Error submitting report: {result['error']}")
                _show_offline_prediction(bag, api_service)
            else:
                # Success - show prediction from backend
                st.success(f"✅ Report submitted successfully! ID: {result.get('report_id', 'N/A')}")

                if "prediction" in result:
                    _display_prediction_results(result["prediction"])
                else:
                    _show_offline_prediction(bag, api_service)
    else:
        # Offline mode - use local ML prediction
        st.warning("⚠️ Running in offline mode - report saved locally")
        _show_offline_prediction(bag, api_service)


def _show_offline_prediction(bag: Bag, api_service):
    """
    Show ML prediction using the frontend ML service when backend is unavailable.
    """
    if not api_service or not hasattr(api_service, 'predict_risk'):
        st.info("💡 Contact airline staff for assistance")
        return

    # Prepare prediction data
    prediction_data = {
        "origen": bag.origin.code,
        "destino": bag.destination.code,
        "aerolinea": "AA",  # Default
        "time_of_day": datetime.now().hour,
        "retraso_min": 30,  # Assume some delay
        "transfers": 1,
        "airport_risk": 0.3,
        "viajero_vip": False,
        "peso_kg": 20.0
    }

    with st.spinner("🤖 Analyzing with ML model..."):
        prediction = api_service.predict_risk(prediction_data)

        if "error" not in prediction:
            _display_prediction_results(prediction)
        else:
            st.error("Unable to get prediction")


def _display_prediction_results(prediction: dict):
    """
    Display ML prediction results in a nice format.
    """
    st.markdown("### 🤖 AI Analysis")

    # Risk metrics
    col1, col2 = st.columns(2)

    with col1:
        loss_prob = prediction.get("loss_probability", 0.0)
        st.metric(
            "Loss Probability",
            f"{loss_prob * 100:.1f}%",
            delta=None
        )

        # Progress bar
        st.progress(loss_prob)

    with col2:
        risk_level = prediction.get("risk_level", "UNKNOWN")
        risk_colors = {
            "LOW": "#22c55e",
            "MEDIUM": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444"
        }
        color = risk_colors.get(risk_level, "#6b7280")

        st.markdown(f"""
        <div style="background: {color}; padding: 20px; border-radius: 8px; text-align: center;">
            <h3 style="margin:0; color:white;">Risk: {risk_level}</h3>
        </div>
        """, unsafe_allow_html=True)

    # Estimated cause
    if "estimated_cause" in prediction:
        st.info(f"🔍 **Likely Cause**: {prediction['estimated_cause']}")

    # Recommendations
    if "recommendations" in prediction and prediction["recommendations"]:
        st.markdown("### 💡 Recommendations")
        for i, rec in enumerate(prediction["recommendations"], 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.markdown("### 💡 Next Steps")
        st.markdown("""
        1. **Contact airline staff** at the baggage claim desk immediately
        2. **File an official report** with your airline reference number
        3. **Check delayed baggage area** - bags often arrive on next flight
        4. **Keep your baggage claim ticket** as proof
        5. **Track updates** in this app - we'll notify you of any changes
        """)
