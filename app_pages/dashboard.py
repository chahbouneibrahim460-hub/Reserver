import streamlit as st
import pandas as pd
from utils.db import get_reservations
from datetime import date, timedelta

st.header("📊 Current Schedule")

# Filters
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

st.write(f"Showing reservations for the current week: **{monday}** to **{sunday}**")

df = get_reservations(monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d"))

if df.empty:
    st.info("No reservations found for this week.")
else:
    # Formatting for display
    df['reservation_date'] = pd.to_datetime(df['reservation_date']).dt.date
    df = df.sort_values(['reservation_date', 'slot_start'])
    
    # Pivoting or grouping to show a nice calendar view might be complex in a simple table
    # Let's just show a clean list/table first
    
    display_df = df[['reservation_date', 'slot_start', 'slot_end', 'group_name']].copy()
    display_df.columns = ['Date', 'Start', 'End', 'Group']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# Detailed view per day
st.subheader("Daily Breakdown")
view_date = st.date_input("Select a day to view details", value=today)
day_df = get_reservations(view_date.strftime("%Y-%m-%d"), view_date.strftime("%Y-%m-%d"))

if day_df.empty:
    st.write(f"No reservations for {view_date}.")
else:
    for start, end in day_df[['slot_start', 'slot_end']].drop_duplicates().values:
        slot_groups = day_df[(day_df['slot_start'] == start) & (day_df['slot_end'] == end)]['group_name'].tolist()
        st.write(f"**{start} - {end}:** {', '.join(slot_groups)}")
