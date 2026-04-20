import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.db import create_reservation, get_reservations, delete_reservation
from utils.email_utils import send_reservation_confirmation

st.header("📅 Make a Reservation")

if not st.session_state.get("group_type"):
    st.warning("Please set your identity or login first.")
    if st.button("Go to Login"):
        st.switch_page("app_pages/login.py")
    st.stop()

group_type = st.session_state.group_type
group_index = st.session_state.group_index
user_email = st.session_state.get("user_email")
group_label = f"{group_type} {group_index}"

st.info(f"Booking for: **{group_label}**")

# Date selection
today = date.today()
max_date = today + timedelta(days=14) # Allow booking 2 weeks in advance
selected_date = st.date_input("Select Date", min_value=today, max_value=max_date, value=today)

# Determine if weekend
is_weekend = selected_date.weekday() >= 5 # 5=Saturday, 6=Sunday

# Define slots
if is_weekend:
    slots = [
        ("10:30", "13:00"),
        ("13:00", "15:30"),
        ("15:30", "18:00"),
        ("18:00", "20:30"),
        ("20:30", "23:00")
    ]
else:
    slots = [
        ("18:00", "20:30"),
        ("20:30", "23:00")
    ]

# Get existing reservations for the selected date to show availability
reservations_df = get_reservations(selected_date.strftime("%Y-%m-%d"), selected_date.strftime("%Y-%m-%d"))

st.subheader("Available Slots")
st.write("Each slot can accommodate up to 2 groups simultaneously.")

for start, end in slots:
    # Count existing reservations for this slot
    if not reservations_df.empty and 'slot_start' in reservations_df.columns:
        slot_res = reservations_df[(reservations_df['slot_start'] == start) & (reservations_df['slot_end'] == end)]
        count = len(slot_res)
    else:
        count = 0
    
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.write(f"**{start} - {end}**")
    
    if count >= 2:
        col2.error("Full")
        col3.write("Unavailable")
    else:
        col2.success(f"{count}/2 Booked")
        if col3.button("Reserve", key=f"btn_{start}_{selected_date}"):
            success, message = create_reservation(
                group_type,
                group_index,
                user_email, 
                selected_date.strftime("%Y-%m-%d"), 
                start, 
                end, 
                is_weekend
            )
            if success:
                st.success(message)
                # Send confirmation email if user is PLBD (has email)
                if user_email:
                    send_reservation_confirmation(user_email, group_label, selected_date.strftime("%Y-%m-%d"), f"{start}-{end}")
                st.rerun()
            else:
                st.error(message)

st.divider()

# My Reservations Section
st.subheader("My Group's Reservations")
all_res = get_reservations()

if not all_res.empty and 'group_type' in all_res.columns:
    my_res = all_res[(all_res['group_type'] == group_type) & (all_res['group_index'] == group_index)]
else:
    my_res = pd.DataFrame()

if not my_res.empty:
    # Filter for future or today's reservations
    my_res = my_res.copy()
    my_res['date_parsed'] = my_res['date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date() if isinstance(x, str) else x)
    future_res = my_res[my_res['date_parsed'] >= today].sort_values('date_parsed')
    
    if not future_res.empty:
        for idx, row in future_res.iterrows():
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"{row['date']}")
            c2.write(f"{row['slot_start']} - {row['slot_end']}")
            if c3.button("Cancel", key=f"del_{row['id']}"):
                if delete_reservation(row['id'], group_type, group_index):
                    st.success("Reservation cancelled.")
                    st.rerun()
                else:
                    st.error("Failed to cancel.")
    else:
        st.write("No upcoming reservations.")
else:
    st.write("You haven't made any reservations yet.")
