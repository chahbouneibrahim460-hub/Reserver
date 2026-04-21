import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.admin import is_admin
from utils.db import (
    get_reservations, admin_delete_reservation, admin_create_reservation,
    get_reservations_paused, set_reservations_paused
)

st.header("🔐 Admin Panel")

user_email = st.session_state.get("user_email")

if not is_admin(user_email):
    st.error("Access denied. You are not an admin.")
    st.stop()

st.success(f"Welcome, Admin ({user_email})")

# ---- Global Pause Toggle ----
st.subheader("⏸️ Reservation Controls")
is_paused = get_reservations_paused()

col_status, col_action = st.columns([2, 1])
if is_paused:
    col_status.error("🔴 Reservations are currently **PAUSED** — no one can make new reservations.")
    if col_action.button("▶️ Resume Reservations"):
        set_reservations_paused(False)
        st.rerun()
else:
    col_status.success("🟢 Reservations are **ACTIVE** — everyone can make reservations.")
    if col_action.button("⏸️ Pause Reservations"):
        set_reservations_paused(True)
        st.rerun()

st.divider()

# ---- Admin Reservation (bypass limits) ----
st.subheader("📅 Make a Reservation (No Limits)")

acol1, acol2 = st.columns(2)
with acol1:
    admin_group_type = st.selectbox("Group Type", ["plbd", "bachelor"], key="admin_gt")
with acol2:
    if admin_group_type == "plbd":
        admin_group_index = st.number_input("Group Number", min_value=1, max_value=36, value=1, key="admin_gi")
    else:
        admin_group_index = st.selectbox("Group Number", [1, 2, 3, 4], key="admin_gi_b")

admin_date = st.date_input("Date", value=date.today(), key="admin_date")
is_weekend = admin_date.weekday() >= 5

if is_weekend:
    admin_slots = [("10:30", "13:00"), ("13:00", "15:30"), ("15:30", "18:00"), ("18:00", "20:30"), ("20:30", "23:00")]
else:
    admin_slots = [("18:00", "20:30"), ("20:30", "23:00")]

admin_slot = st.selectbox("Slot", admin_slots, format_func=lambda x: f"{x[0]} - {x[1]}", key="admin_slot")

if st.button("🔒 Admin Reserve", key="admin_reserve"):
    success, msg = admin_create_reservation(
        admin_group_type, admin_group_index, user_email,
        admin_date.strftime("%Y-%m-%d"), admin_slot[0], admin_slot[1]
    )
    if success:
        st.success(msg)
        st.rerun()
    else:
        st.error(msg)

st.divider()

# ---- All Reservations with Delete ----
st.subheader("🗑️ Manage All Reservations")

view_range = st.selectbox("View", ["This Week", "Next Week", "All Future"], key="admin_view")
today = date.today()
monday = today - timedelta(days=today.weekday())

if view_range == "This Week":
    start = monday.strftime("%Y-%m-%d")
    end = (monday + timedelta(days=6)).strftime("%Y-%m-%d")
    df = get_reservations(start, end)
elif view_range == "Next Week":
    next_monday = monday + timedelta(days=7)
    start = next_monday.strftime("%Y-%m-%d")
    end = (next_monday + timedelta(days=6)).strftime("%Y-%m-%d")
    df = get_reservations(start, end)
else:
    df = get_reservations(today.strftime("%Y-%m-%d"), (today + timedelta(days=30)).strftime("%Y-%m-%d"))

if df.empty:
    st.info("No reservations found for this period.")
else:
    df = df.sort_values(['date', 'slot_start'])
    df['group'] = df['group_type'] + " " + df['group_index'].astype(str)

    for idx, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        c1.write(f"**{row['date']}**")
        c2.write(f"{row['slot_start']} - {row['slot_end']}")
        c3.write(f"{row['group']}")
        if c4.button("🗑️ Delete", key=f"adel_{row['id']}"):
            if admin_delete_reservation(row['id']):
                st.success(f"Deleted reservation for {row['group']} on {row['date']}")
                st.rerun()
            else:
                st.error("Failed to delete.")
